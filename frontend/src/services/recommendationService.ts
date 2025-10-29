import { api } from './api'
import { BookRecommendation, RecommendationResponse } from '@/types/recommendation'

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
    const response = await api.get('/recommendations/trending', {
      params: { limit }
    })
    return response.data
  },

  async getPopularBooks(limit: number = 10): Promise<BookRecommendation[]> {
    const response = await api.get('/recommendations/popular', {
      params: { limit }
    })
    return response.data
  },

  async getSimilarBooks(bookId: string, limit: number = 10): Promise<BookRecommendation[]> {
    const response = await api.get(`/recommendations/books/${bookId}/similar`, {
      params: { limit }
    })
    return response.data
  }

  ,

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
