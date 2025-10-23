import { useEffect, useState } from 'react'
import { BookRecommendation } from '@/types/recommendation'
import { BookCard } from '@/components/books/BookCard'
import { recommendationService } from '@/services/recommendationService'
import { useAuthStore } from '@/stores/authStore'

export function RecommendationSection() {
  const { isAuthenticated } = useAuthStore()
  const [recommendations, setRecommendations] = useState<BookRecommendation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setIsLoading(true)
        let recs: BookRecommendation[] = []

        if (isAuthenticated) {
          // Get personalized recommendations for authenticated users
          const response = await recommendationService.getPersonalizedRecommendations(8)
          recs = response.recommendations
        } else {
          // Get popular books for non-authenticated users
          recs = await recommendationService.getPopularBooks(8)
        }

        setRecommendations(recs)
      } catch (error) {
        console.error('Error fetching recommendations:', error)
        // Fallback to popular books
        try {
          const popularBooks = await recommendationService.getPopularBooks(8)
          setRecommendations(popularBooks)
        } catch (fallbackError) {
          console.error('Error fetching popular books:', fallbackError)
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchRecommendations()
  }, [isAuthenticated])

  if (isLoading) {
    return (
      <section>
        <h2 className="text-2xl font-bold mb-6">
          {isAuthenticated ? 'Recomendados para Você' : 'Livros Populares'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
              <div className="bg-gray-200 h-4 rounded mb-2"></div>
              <div className="bg-gray-200 h-4 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </section>
    )
  }

  if (recommendations.length === 0) {
    return null
  }

  return (
    <section>
      <h2 className="text-2xl font-bold mb-6">
        {isAuthenticated ? 'Recomendados para Você' : 'Livros Populares'}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {recommendations.map((rec) => (
          <BookCard key={rec.book_id} book={rec.book!} />
        ))}
      </div>
    </section>
  )
}
