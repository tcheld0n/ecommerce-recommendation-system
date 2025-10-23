import { api } from './api'
import { Book, BookSearchParams, Category } from '@/types/book'

export const bookService = {
  async getBooks(searchParams: BookSearchParams = {}): Promise<Book[]> {
    const response = await api.get('/books', { params: searchParams })
    return response.data
  },

  async getBook(id: string): Promise<Book> {
    const response = await api.get(`/books/${id}`)
    return response.data
  },

  async getPopularBooks(limit: number = 10): Promise<Book[]> {
    const response = await api.get('/books/popular', { params: { limit } })
    return response.data
  },

  async getRecentBooks(limit: number = 10): Promise<Book[]> {
    const response = await api.get('/books/recent', { params: { limit } })
    return response.data
  },

  async getBooksByAuthor(author: string, limit: number = 10): Promise<Book[]> {
    const response = await api.get(`/books/author/${author}`, { params: { limit } })
    return response.data
  },

  async getBooksByCategory(categoryId: string, skip: number = 0, limit: number = 20): Promise<Book[]> {
    const response = await api.get(`/categories/${categoryId}/books`, { 
      params: { skip, limit } 
    })
    return response.data
  },

  async getCategories(): Promise<Category[]> {
    const response = await api.get('/categories')
    return response.data
  },

  async getCategory(id: string): Promise<Category> {
    const response = await api.get(`/categories/${id}`)
    return response.data
  },

  // Admin methods
  async createBook(bookData: any): Promise<Book> {
    const response = await api.post('/books', bookData)
    return response.data
  },

  async updateBook(id: string, bookData: any): Promise<Book> {
    const response = await api.put(`/books/${id}`, bookData)
    return response.data
  },

  async deleteBook(id: string): Promise<void> {
    await api.delete(`/books/${id}`)
  },

  async createCategory(categoryData: any): Promise<Category> {
    const response = await api.post('/categories', categoryData)
    return response.data
  },

  async updateCategory(id: string, categoryData: any): Promise<Category> {
    const response = await api.put(`/categories/${id}`, categoryData)
    return response.data
  },

  async deleteCategory(id: string): Promise<void> {
    await api.delete(`/categories/${id}`)
  }
}
