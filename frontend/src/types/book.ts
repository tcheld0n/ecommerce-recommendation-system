export interface Book {
  id: string
  isbn: string
  title: string
  author: string
  publisher: string
  published_year: number
  description?: string
  price: number
  stock_quantity: number
  cover_image_url?: string
  average_rating: number
  total_reviews: number
  category_id: string
  created_at: string
  updated_at: string
  category?: Category
  tags?: BookTag[]
}

export interface Category {
  id: string
  name: string
  slug: string
  description?: string
  parent_id?: string
  created_at: string
}

export interface BookTag {
  id: string
  book_id: string
  tag: string
  created_at: string
}

export interface BookSearchParams {
  query?: string
  category_id?: string
  min_price?: number
  max_price?: number
  min_rating?: number
  author?: string
  publisher?: string
  published_year?: number
  sort_by?: 'relevance' | 'price_asc' | 'price_desc' | 'rating' | 'newest'
  page?: number
  limit?: number
}
