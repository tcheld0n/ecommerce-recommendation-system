import { Book } from './book'

export interface Cart {
  id: string
  user_id: string
  items: CartItem[]
  total_items: number
  total_amount: number
  created_at: string
  updated_at: string
}

export interface CartItem {
  id: string
  cart_id: string
  book_id: string
  quantity: number
  created_at: string
  updated_at: string
  book?: Book
  unit_price?: number
  subtotal?: number
}

export interface CartItemCreate {
  book_id: string
  quantity: number
}

export interface CartItemUpdate {
  quantity: number
}
