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
          console.log('Cart loaded:', cart)
          set({ cart, isLoading: false, error: null })
        } catch (error: any) {
          console.error('Error loading cart:', error)
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to get cart'
          
          // Se for erro 401, manter o carrinho existente mas mostrar erro
          if (error.response?.status === 401) {
            console.warn('Authentication error - keeping existing cart data')
            set({ 
              error: 'Sessão expirada. Por favor, faça login novamente.',
              isLoading: false
              // Não limpar cart aqui para manter dados visuais
            })
          } else {
            set({ 
              error: errorMessage, 
              isLoading: false,
              // Só limpar cart se não for erro de autenticação
              cart: error.response?.status === 401 ? get().cart : null
            })
          }
        }
      },

      addToCart: async (bookId: string, quantity: number) => {
        set({ isLoading: true, error: null })
        try {
          await cartService.addToCart({ book_id: bookId, quantity })
          // Recarregar carrinho completo após adicionar item
          await get().getCart()
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
          // O backend retorna apenas o item atualizado, então precisamos recarregar o carrinho completo
          await cartService.updateCartItem(itemId, { quantity })
          // Recarregar carrinho completo após atualizar item
          await get().getCart()
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
