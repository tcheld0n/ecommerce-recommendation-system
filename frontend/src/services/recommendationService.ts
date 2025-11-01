import { api } from './api'
import { BookRecommendation, RecommendationResponse } from '@/types/recommendation'
import type { Book } from '@/types/book'

export const recommendationService = {
  async getPersonalizedRecommendations(
    limit: number = 10,
    algorithm: string = 'hybrid'
  ): Promise<RecommendationResponse> {
    const response = await api.get('/recommendations/for-you', {
      params: { limit, algorithm }
    })
    return response.data
  },

  async getTrendingBooks(limit: number = 10): Promise<BookRecommendation[]> {
    const response = await api.get('/books/recent', { params: { limit } })
    const books: Book[] = response.data
    return books.map((b) => ({
      book_id: b.id,
      score: 0,
      book: b,
    }))
  },

  async getPopularBooks(limit: number = 10): Promise<BookRecommendation[]> {
    const response = await api.get('/books/popular', { params: { limit } })
    const books: Book[] = response.data
    return books.map((b) => ({
      book_id: b.id,
      score: 0,
      book: b,
    }))
  },

  async getSimilarBooks(bookId: string, limit: number = 10): Promise<BookRecommendation[]> {
    try {
      const response = await api.get(`/recommendations/books/${bookId}/similar`, {
        params: { limit }
      })
      return response.data
    } catch (err) {
      return []
    }
  },

  async recordInteraction(bookId: string, interactionType: string): Promise<void> {
    try {
      await api.post('/recommendations/interactions', {
        book_id: bookId,
        interaction_type: interactionType
      })
    } catch (err) {
    }
  }
}
