import { api } from './api'
import { Order, OrderCreate, OrderSummary } from '@/types/order'
import { useState, useCallback } from 'react'

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

// Hook for order operations
export const useOrderService = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createOrder = useCallback(async (orderData: OrderCreate): Promise<Order> => {
    setIsLoading(true)
    setError(null)
    try {
      const order = await orderService.createOrder(orderData)
      return order
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar pedido')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const getOrder = useCallback(async (id: string): Promise<Order> => {
    setIsLoading(true)
    setError(null)
    try {
      const order = await orderService.getOrder(id)
      return order
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao buscar pedido')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const getUserOrders = useCallback(async (): Promise<OrderSummary[]> => {
    setIsLoading(true)
    setError(null)
    try {
      const orders = await orderService.getUserOrders()
      return orders
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao buscar pedidos')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const processPayment = useCallback(async (orderId: string): Promise<any> => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await orderService.processPayment(orderId)
      return result
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao processar pagamento')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    createOrder,
    getOrder,
    getUserOrders,
    processPayment,
    isLoading,
    error
  }
}
