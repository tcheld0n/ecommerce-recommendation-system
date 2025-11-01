import { useState, useEffect } from 'react'
import { bookService } from '@/services/bookService'
import { Category } from '@/types/book'

interface CategoryFilterProps {
  selectedCategory?: string
  onCategoryChange?: (categoryId: string | null) => void
}

export function CategoryFilter({ selectedCategory, onCategoryChange }: CategoryFilterProps) {
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsLoading(true)
        const data = await bookService.getCategories()
        setCategories(data)
      } catch (error) {
        console.error('Erro ao carregar categorias:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCategories()
  }, [])

  const handleCategoryClick = (categoryId: string | null) => {
    if (selectedCategory === categoryId) {
      // Se clicar na mesma categoria, deseleciona
      onCategoryChange?.(null)
    } else {
      onCategoryChange?.(categoryId)
    }
  }

  if (isLoading) {
    return (
      <div className="flex border-b border-gray-800 mb-6 overflow-x-auto scrollbar-hide bg-gray-900">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex-shrink-0 h-12 bg-gray-800 animate-pulse"
            style={{ width: '100px' }}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="flex border-b border-gray-800 mb-6 overflow-x-auto scrollbar-hide bg-gray-900">
      {/* Botão "Todas as Categorias" */}
      <button
        onClick={() => handleCategoryClick(null)}
        className={`flex-shrink-0 px-6 py-3 font-semibold transition-all duration-200 whitespace-nowrap border-b-4 -mb-0.5 hover:bg-gray-800 ${
          !selectedCategory
            ? 'border-b-white text-white'
            : 'border-b-transparent text-gray-400'
        }`}
      >
        Todas
      </button>

      {/* Botões de Categorias */}
      {categories.map((category) => (
        <button
          key={category.id}
          onClick={() => handleCategoryClick(category.id)}
          className={`flex-shrink-0 px-6 py-3 font-semibold transition-all duration-200 whitespace-nowrap border-b-4 -mb-0.5 hover:bg-gray-800 ${
            selectedCategory === category.id
              ? 'border-b-white text-white'
              : 'border-b-transparent text-gray-400'
          }`}
        >
          {category.name}
        </button>
      ))}
    </div>
  )
}
