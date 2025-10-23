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

  async updateCartItem(itemId: string, itemData: CartItemUpdate): Promise<Cart> {
    const response = await api.put(`/cart/items/${itemId}`, itemData)
    return response.data
  },

  async removeFromCart(itemId: string): Promise<void> {
    await api.delete(`/cart/items/${itemId}`)
  },

  async clearCart(): Promise<void> {
    await api.delete('/cart')
  }
}
