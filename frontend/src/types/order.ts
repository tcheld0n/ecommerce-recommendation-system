export interface Order {
  id: string
  user_id: string
  status: OrderStatus
  total_amount: number
  shipping_address: Record<string, any>
  payment_method: string
  payment_status: PaymentStatus
  tracking_code?: string
  created_at: string
  updated_at: string
  items: OrderItem[]
}

export interface OrderItem {
  id: string
  order_id: string
  book_id: string
  quantity: number
  unit_price: number
  subtotal: number
  created_at: string
  book?: Book
}

export interface OrderCreate {
  shipping_address: Record<string, any>
  payment_method: string
  items: OrderItemCreate[]
}

export interface OrderItemCreate {
  book_id: string
  quantity: number
  unit_price: number
}

export interface OrderSummary {
  id: string
  status: OrderStatus
  total_amount: number
  created_at: string
  items_count: number
}

export enum OrderStatus {
  PENDING = 'pending',
  PAID = 'paid',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled'
}

export enum PaymentStatus {
  PENDING = 'pending',
  PAID = 'paid',
  FAILED = 'failed',
  REFUNDED = 'refunded'
}

import { Book } from './book'
