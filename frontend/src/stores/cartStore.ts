import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Cart, CartItem } from '@/types/cart'
import { cartService } from '@/services/cartService'

interface CartState {
  cart: Cart | null
  isLoading: boolean
  error: string | null
}

interface CartActions {
  getCart: () => Promise<void>
  addToCart: (bookId: string, quantity: number) => Promise<void>
  updateCartItem: (itemId: string, quantity: number) => Promise<void>
  removeFromCart: (itemId: string) => Promise<void>
  clearCart: () => Promise<void>
  clearError: () => void
}

export const useCartStore = create<CartState & CartActions>()(
  persist(
    (set, get) => ({
      cart: null,
      isLoading: false,
      error: null,

      getCart: async () => {
        set({ isLoading: true, error: null })
        try {
          const cart = await cartService.getCart()
          set({ cart, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to get cart', 
            isLoading: false 
          })
        }
      },

      addToCart: async (bookId: string, quantity: number) => {
        set({ isLoading: true, error: null })
        try {
          const cart = await cartService.addToCart({ book_id: bookId, quantity })
          set({ cart, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to add to cart', 
            isLoading: false 
          })
          throw error
        }
      },

      updateCartItem: async (itemId: string, quantity: number) => {
        set({ isLoading: true, error: null })
        try {
          const cart = await cartService.updateCartItem(itemId, { quantity })
          set({ cart, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to update cart item', 
            isLoading: false 
          })
          throw error
        }
      },

      removeFromCart: async (itemId: string) => {
        set({ isLoading: true, error: null })
        try {
          await cartService.removeFromCart(itemId)
          await get().getCart() // Refresh cart
          set({ isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to remove from cart', 
            isLoading: false 
          })
          throw error
        }
      },

      clearCart: async () => {
        set({ isLoading: true, error: null })
        try {
          await cartService.clearCart()
          set({ cart: null, isLoading: false })
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to clear cart', 
            isLoading: false 
          })
          throw error
        }
      },

      clearError: () => set({ error: null })
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({ cart: state.cart })
    }
  )
)
