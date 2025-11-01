import { api } from './api'
import { Cart, CartItemCreate, CartItemUpdate } from '@/types/cart'

export const cartService = {
  async getCart(): Promise<Cart> {
    const response = await api.get('/cart')
    return response.data
  },

  async addToCart(itemData: CartItemCreate): Promise<Cart> {
    const response = await api.post('/cart/items', itemData)
    return response.data
  },

  async updateCartItem(itemId: string, itemData: CartItemUpdate): Promise<void> {
    // O backend retorna apenas o CartItem, não o Cart completo
    // Então não precisamos retornar nada aqui, o store vai recarregar o carrinho
    await api.put(`/cart/items/${itemId}`, itemData)
  },

  async removeFromCart(itemId: string): Promise<void> {
    await api.delete(`/cart/items/${itemId}`)
  },

  async clearCart(): Promise<void> {
    await api.delete('/cart')
  }
}
