#!/usr/bin/env python3
"""
Demo script to showcase the E-Commerce Book Recommendation System
This script demonstrates the main features of the system.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def pretty_print(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def demo():
    """Run the demo"""
    
    print_section("E-Commerce Book Recommendation System Demo")
    print("\nMake sure the Flask server is running on http://localhost:5000")
    time.sleep(1)
    
    # 1. Check system health
    print_section("1. System Health Check")
    response = requests.get(f"{BASE_URL}/api/health")
    pretty_print(response.json())
    
    # 2. Get all books
    print_section("2. Browse Book Catalog")
    response = requests.get(f"{BASE_URL}/api/books")
    books = response.json()
    print(f"Total books available: {len(books)}")
    print("\nFirst 3 books:")
    for book in books[:3]:
        print(f"- {book['title']} by {book['author']} (${book['price']})")
    
    # 3. Search for books
    print_section("3. Search Books by Genre")
    response = requests.get(f"{BASE_URL}/api/books?genre=Fantasy")
    fantasy_books = response.json()
    print(f"Found {len(fantasy_books)} Fantasy books:")
    for book in fantasy_books:
        print(f"- {book['title']} by {book['author']}")
    
    # 4. Create a user
    print_section("4. Create New User")
    user_data = {
        "username": "demo_user",
        "email": "demo@example.com"
    }
    response = requests.post(f"{BASE_URL}/api/users", json=user_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user['id']
        print(f"Created user: {user['username']} (ID: {user_id})")
    else:
        # User might already exist, try to get existing users
        user_id = 1
        print(f"Using existing user ID: {user_id}")
    
    # 5. Add books to cart
    print_section("5. Add Books to Shopping Cart")
    cart_items = [
        {"user_id": user_id, "book_id": 1, "quantity": 2},
        {"user_id": user_id, "book_id": 3, "quantity": 1},
    ]
    
    for item in cart_items:
        response = requests.post(f"{BASE_URL}/api/cart", json=item)
        print(f"Added book {item['book_id']} (quantity: {item['quantity']}) to cart")
    
    # 6. View cart
    print_section("6. View Shopping Cart")
    response = requests.get(f"{BASE_URL}/api/cart/{user_id}")
    cart = response.json()
    total = 0
    for item in cart:
        book = item['book']
        subtotal = book['price'] * item['quantity']
        total += subtotal
        print(f"- {book['title']}: {item['quantity']} x ${book['price']} = ${subtotal:.2f}")
    print(f"\nTotal: ${total:.2f}")
    
    # 7. Rate books
    print_section("7. Rate Books")
    ratings = [
        {"user_id": user_id, "book_id": 1, "rating": 5, "review": "Absolutely amazing!"},
        {"user_id": user_id, "book_id": 2, "rating": 4, "review": "Very good read"},
        {"user_id": user_id, "book_id": 3, "rating": 5, "review": "Loved it!"},
    ]
    
    for rating in ratings:
        response = requests.post(f"{BASE_URL}/api/ratings", json=rating)
        print(f"Rated book {rating['book_id']}: {rating['rating']} stars")
    
    # 8. Get popular books
    print_section("8. Get Popular Books")
    response = requests.get(f"{BASE_URL}/api/recommendations/popular?n=5")
    popular = response.json()
    print("Top 5 popular books:")
    for i, book in enumerate(popular, 1):
        print(f"{i}. {book['title']} by {book['author']}")
    
    # 9. Get personalized recommendations
    print_section("9. Get Personalized Recommendations")
    response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}?n=5")
    recommendations = response.json()
    print(f"Recommendations for user {user_id}:")
    for i, book in enumerate(recommendations, 1):
        print(f"{i}. {book['title']} by {book['author']} - {book['genre']}")
    
    # 10. Get similar books
    print_section("10. Get Books Similar to a Specific Book")
    book_id = 1
    response = requests.get(f"{BASE_URL}/api/recommendations/book/{book_id}?n=3")
    similar = response.json()
    print(f"Books similar to book ID {book_id}:")
    for book in similar:
        print(f"- {book['title']} by {book['author']} ({book['genre']})")
    
    # 11. Complete purchase
    print_section("11. Complete Purchase")
    purchase_data = {"user_id": user_id}
    response = requests.post(f"{BASE_URL}/api/purchase", json=purchase_data)
    if response.status_code == 201:
        purchases = response.json()
        print(f"Successfully purchased {len(purchases)} items!")
        for purchase in purchases:
            print(f"- Book ID {purchase['book_id']}: {purchase['quantity']} x ${purchase['total_price']:.2f}")
    else:
        print(f"Purchase failed: {response.json()}")
    
    # 12. View purchase history
    print_section("12. View Purchase History")
    response = requests.get(f"{BASE_URL}/api/purchases/{user_id}")
    purchases = response.json()
    print(f"Total purchases: {len(purchases)}")
    for purchase in purchases:
        print(f"- Book ID {purchase['book_id']}: Qty {purchase['quantity']} - ${purchase['total_price']:.2f}")
    
    print_section("Demo Complete!")
    print("The E-Commerce Book Recommendation System is fully functional!")

if __name__ == "__main__":
    try:
        demo()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Please make sure the Flask server is running:")
        print("  python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
