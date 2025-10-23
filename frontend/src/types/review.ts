export interface Review {
  id: string
  user_id: string
  book_id: string
  rating: number
  comment?: string
  helpful_count: number
  created_at: string
  updated_at: string
  user?: User
}

export interface ReviewCreate {
  book_id: string
  rating: number
  comment?: string
}

export interface ReviewUpdate {
  rating?: number
  comment?: string
}

export interface ReviewWithUser extends Review {
  user?: User
}

export interface User {
  id: string
  email: string
  full_name: string
}
