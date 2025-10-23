import { api } from './api'
import { Order, OrderCreate, OrderSummary } from '@/types/order'

export const orderService = {
  async createOrder(orderData: OrderCreate): Promise<Order> {
    const response = await api.post('/orders', orderData)
    return response.data
  },

  async getOrder(id: string): Promise<Order> {
    const response = await api.get(`/orders/${id}`)
    return response.data
  },

  async getUserOrders(): Promise<OrderSummary[]> {
    const response = await api.get('/orders')
    return response.data
  },

  async processPayment(orderId: string): Promise<any> {
    const response = await api.post(`/orders/${orderId}/payment`)
    return response.data
  },

  // Admin methods
  async updateOrderStatus(orderId: string, status: string): Promise<Order> {
    const response = await api.put(`/orders/${orderId}/status`, { status })
    return response.data
  }
}
