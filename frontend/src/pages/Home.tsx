import { useEffect, useState } from 'react'
import { useBookStore } from '@/stores/bookStore'
import { BookCard } from '@/components/books/BookCard'
import { RecommendationSection } from '@/components/recommendations/RecommendationSection'
import { CategoryFilter } from '@/components/common/CategoryFilter'
import { Pagination } from '@/components/common/Pagination'

export function Home() {
  const { 
    books,
    popularBooks, 
    recentBooks, 
    getPopularBooks, 
    getRecentBooks,
    getBooksByCategory,
    isLoading 
  } = useBookStore()
  
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [hasNextPage, setHasNextPage] = useState(false)
  const itemsPerPage = 20

  useEffect(() => {
    if (selectedCategory) {
      const skip = (currentPage - 1) * itemsPerPage
      getBooksByCategory(selectedCategory, skip, itemsPerPage)
        .then(() => {
          // Se recebemos menos livros que o esperado, não há próxima página
          setHasNextPage(false)
        })
        .catch(() => {
          setHasNextPage(false)
        })
    } else {
      getPopularBooks(8)
      getRecentBooks(8)
    }
  }, [selectedCategory, currentPage, getPopularBooks, getRecentBooks, getBooksByCategory])

  // Verifica se há próxima página baseado na quantidade de livros recebidos
  useEffect(() => {
    if (books.length >= itemsPerPage) {
      setHasNextPage(true)
    } else if (currentPage === 1 && books.length > 0) {
      // Se estamos na primeira página e recebemos algum livro
      setHasNextPage(false)
    }
  }, [books.length, currentPage])

  const handleCategoryChange = (categoryId: string | null) => {
    setSelectedCategory(categoryId)
    setCurrentPage(1) // Reset para primeira página ao mudar categoria
    setHasNextPage(false)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="text-center py-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg">
        <h1 className="text-4xl font-bold mb-0">Bem-vindo à Bookstore</h1>
        <p className="text-xl mb-0">Descubra seus próximos livros favoritos</p>
      </section>

      {/* Category Filter */}
      <CategoryFilter 
        selectedCategory={selectedCategory || undefined}
        onCategoryChange={handleCategoryChange}
      />

      {/* Books by Category */}
      {selectedCategory && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Livros por Categoria</h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
                  <div className="bg-gray-200 h-4 rounded mb-2"></div>
                  <div className="bg-gray-200 h-4 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {books.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </div>
              {books.length > 0 && (
                <Pagination
                  currentPage={currentPage}
                  hasNextPage={hasNextPage}
                  hasPrevPage={currentPage > 1}
                  itemsPerPage={itemsPerPage}
                  onPageChange={handlePageChange}
                />
              )}
            </>
          )}
        </section>
      )}

      {/* Recommendations */}
      {!selectedCategory && <RecommendationSection />}

      {/* Popular Books */}
      {!selectedCategory && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Livros Populares</h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
                  <div className="bg-gray-200 h-4 rounded mb-2"></div>
                  <div className="bg-gray-200 h-4 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {popularBooks.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          )}
        </section>
      )}

      {/* Recent Books */}
      {!selectedCategory && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Lançamentos</h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
                  <div className="bg-gray-200 h-4 rounded mb-2"></div>
                  <div className="bg-gray-200 h-4 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {recentBooks.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
