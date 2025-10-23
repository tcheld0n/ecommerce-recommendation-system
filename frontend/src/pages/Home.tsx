import { useEffect } from 'react'
import { useBookStore } from '@/stores/bookStore'
import { BookCard } from '@/components/books/BookCard'
import { RecommendationSection } from '@/components/recommendations/RecommendationSection'
import { SearchBar } from '@/components/common/SearchBar'

export function Home() {
  const { 
    popularBooks, 
    recentBooks, 
    getPopularBooks, 
    getRecentBooks, 
    isLoading 
  } = useBookStore()

  useEffect(() => {
    getPopularBooks(8)
    getRecentBooks(8)
  }, [getPopularBooks, getRecentBooks])

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg">
        <h1 className="text-4xl font-bold mb-4">Bem-vindo à Bookstore</h1>
        <p className="text-xl mb-8">Descubra seus próximos livros favoritos</p>
        <SearchBar />
      </section>

      {/* Recommendations */}
      <RecommendationSection />

      {/* Popular Books */}
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

      {/* Recent Books */}
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
    </div>
  )
}
