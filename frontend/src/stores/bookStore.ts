import { create } from 'zustand'
import { Book, BookSearchParams, Category } from '@/types/book'
import { bookService } from '@/services/bookService'

interface BookState {
  books: Book[]
  categories: Category[]
  popularBooks: Book[]
  recentBooks: Book[]
  currentBook: Book | null
  isLoading: boolean
  error: string | null
  searchParams: BookSearchParams
}

interface BookActions {
  searchBooks: (params: BookSearchParams) => Promise<void>
  getBook: (id: string) => Promise<void>
  getPopularBooks: (limit?: number) => Promise<void>
  getRecentBooks: (limit?: number) => Promise<void>
  getBooksByAuthor: (author: string, limit?: number) => Promise<void>
  getBooksByCategory: (categoryId: string, skip?: number, limit?: number) => Promise<void>
  getCategories: () => Promise<void>
  clearBooks: () => void
  clearError: () => void
}

export const useBookStore = create<BookState & BookActions>((set, get) => ({
  books: [],
  categories: [],
  popularBooks: [],
  recentBooks: [],
  currentBook: null,
  isLoading: false,
  error: null,
  searchParams: {},

  searchBooks: async (params: BookSearchParams) => {
    set({ isLoading: true, error: null, searchParams: params })
    try {
      const books = await bookService.getBooks(params)
      set({ books, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to search books', 
        isLoading: false 
      })
    }
  },

  getBook: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      const book = await bookService.getBook(id)
      set({ currentBook: book, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to get book', 
        isLoading: false 
      })
    }
  },

  getPopularBooks: async (limit: number = 10) => {
    set({ isLoading: true, error: null })
    try {
      const books = await bookService.getPopularBooks(limit)
      set({ popularBooks: books, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to get popular books', 
        isLoading: false 
      })
    }
  },

  getRecentBooks: async (limit: number = 10) => {
    set({ isLoading: true, error: null })
    try {
      const books = await bookService.getRecentBooks(limit)
      set({ recentBooks: books, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to get recent books', 
        isLoading: false 
      })
    }
  },

  getBooksByAuthor: async (author: string, limit: number = 10) => {
    set({ isLoading: true, error: null })
    try {
      const books = await bookService.getBooksByAuthor(author, limit)
      set({ books, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to get books by author', 
        isLoading: false 
      })
    }
  },

  getBooksByCategory: async (categoryId: string, skip: number = 0, limit: number = 20) => {
    set({ isLoading: true, error: null })
    try {
      const books = await bookService.getBooksByCategory(categoryId, skip, limit)
      set({ books, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to get books by category', 
        isLoading: false 
      })
    }
  },

  getCategories: async () => {
    set({ isLoading: true, error: null })
    try {
      const categories = await bookService.getCategories()
      set({ categories, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to get categories', 
        isLoading: false 
      })
    }
  },

  clearBooks: () => set({ books: [], currentBook: null }),
  clearError: () => set({ error: null })
}))
