#!/usr/bin/env python3
"""
Script para importar APENAS os dados do livros.csv para o banco de dados
"""

import csv
import sys
import os
from pathlib import Path
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from core.database import SessionLocal, engine
from models.book import Book, Category
from models.review import Review
from models.user import User
from models.cart import CartItem
from models.order import OrderItem
from models.recommendation import UserInteraction
from core.config import settings

def create_default_categories(db: Session):
    """Cria categorias padrão se não existirem"""
    default_categories = [
        {"name": "Ficção", "slug": "ficcao", "description": "Livros de ficção"},
        {"name": "Não-Ficção", "slug": "nao-ficcao", "description": "Livros de não-ficção"},
        {"name": "Tecnologia", "slug": "tecnologia", "description": "Livros sobre tecnologia"},
        {"name": "Negócios", "slug": "negocios", "description": "Livros sobre negócios e finanças"},
        {"name": "Biografia", "slug": "biografia", "description": "Biografias e memórias"},
        {"name": "História", "slug": "historia", "description": "Livros de história"},
        {"name": "Ciência", "slug": "ciencia", "description": "Livros de ciência"},
        {"name": "Arte", "slug": "arte", "description": "Livros sobre arte e cultura"},
        {"name": "Infantil", "slug": "infantil", "description": "Livros infantis"},
        {"name": "Outros", "slug": "outros", "description": "Outras categorias"}
    ]
    
    for cat_data in default_categories:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    db.commit()

def get_category_by_name(db: Session, book_title: str, book_author: str) -> Category:
    """Determina a categoria do livro baseado no título e autor"""
    category_mapping = {
        "ficcao": ["romance", "ficção", "novela", "conto", "fantasia", "ficção científica"],
        "tecnologia": ["tecnologia", "programação", "computação", "software", "hardware", "digital"],
        "negocios": ["negócios", "finanças", "economia", "gestão", "marketing", "empreendedorismo"],
        "biografia": ["biografia", "memórias", "autobiografia"],
        "historia": ["história", "histórico", "guerra", "política"],
        "ciencia": ["ciência", "científico", "pesquisa", "estudo"],
        "arte": ["arte", "cultura", "música", "cinema", "teatro"],
        "infantil": ["infantil", "criança", "baby", "kids"]
    }
    
    default_category = db.query(Category).filter(Category.slug == "outros").first()
    
    text_to_analyze = f"{book_title} {book_author}".lower()
    
    for slug, keywords in category_mapping.items():
        for keyword in keywords:
            if keyword in text_to_analyze:
                category = db.query(Category).filter(Category.slug == slug).first()
                if category:
                    return category
    
    return default_category

def clean_isbn(isbn: str) -> str:
    """Limpa e valida ISBN"""
    if not isbn:
        return None
    
    clean_isbn = ''.join(filter(str.isdigit, isbn))
    
    if len(clean_isbn) in [10, 13]:
        return clean_isbn
    
    return None

def import_books_from_csv(csv_path: str):
    """Importa livros do CSV para o banco de dados"""
    
    db = SessionLocal()
    
    try:
        create_default_categories(db)
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        print(f"📚 Importando dados de: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    title = row.get('titulo', '').strip()
                    author = row.get('autor', '').strip()
                    isbn = clean_isbn(row.get('isbn', ''))
                    pages = row.get('paginas', '0')
                    year = row.get('ano', '0')
                    
                    if not title or not author or not isbn:
                        skipped_count += 1
                        continue
                    
                    try:
                        pages = int(pages) if pages.isdigit() else 0
                        year = int(year) if year.isdigit() else 2020
                    except ValueError:
                        pages = 0
                        year = 2020
                    
                    existing_book = db.query(Book).filter(Book.isbn == isbn).first()
                    if existing_book:
                        skipped_count += 1
                        continue
                    
                    category = get_category_by_name(db, title, author)
                    
                    book = Book(
                        isbn=isbn,
                        title=title,
                        author=author,
                        publisher="Editora Desconhecida",
                        published_year=year,
                        description=f"Livro com {pages} páginas publicado em {year}",
                        price=Decimal('29.90'),
                        stock_quantity=10,
                        cover_image_url='/placeholder-book.svg',
                        category_id=category.id,
                        average_rating=0.0,
                        total_reviews=0
                    )
                    
                    db.add(book)
                    db.commit()
                    
                    imported_count += 1
                    
                    if imported_count % 100 == 0:
                        print(f"📊 Importados {imported_count} livros...")
                        
                except IntegrityError as e:
                    db.rollback()
                    error_count += 1
                except Exception as e:
                    db.rollback()
                    error_count += 1
        
        print(f"\n✅ Importação concluída!")
        print(f"📚 Livros importados: {imported_count}")
        print(f"⚠️  Livros pulados: {skipped_count}")
        print(f"❌ Erros: {error_count}")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    """Função principal"""
    csv_path = "livros.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo CSV não encontrado: {csv_path}")
        return
    
    print("🚀 Importando dados do livros.csv...")
    import_books_from_csv(csv_path)

if __name__ == "__main__":
    main()
