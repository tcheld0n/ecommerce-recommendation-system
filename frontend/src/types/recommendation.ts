import { Book } from './book'

export interface BookRecommendation {
  book_id: string
  score: number
  reason?: string
  book?: Book
}

export interface RecommendationResponse {
  recommendations: BookRecommendation[]
  algorithm_used: string
  generated_at: string
}

export interface RecommendationRequest {
  user_id?: string
  book_id?: string
  limit?: number
  algorithm?: 'content' | 'collaborative' | 'hybrid'
}
