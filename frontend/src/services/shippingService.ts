import { api } from './api'

export interface PackageItem {
  weight_kg: number
  length_cm: number
  width_cm: number
  height_cm: number
  quantity: number
}

export interface QuoteRequest {
  destination_zip: string
  origin_zip?: string
  items: PackageItem[]
  declared_value?: number
}

export interface CarrierOption {
  carrier: string
  service: string
  price: number
  currency: string
  estimated_days: number
  estimated_delivery_date: string
}

export interface QuoteResponse {
  destination_zip: string
  options: CarrierOption[]
}

export interface CreateShipmentRequest {
  order_id: string
  carrier: string
  service: string
  destination: Record<string, any>
  items: PackageItem[]
  declared_value?: number
}

export interface CreateShipmentResponse {
  tracking_code: string
  carrier: string
  service: string
  label_url?: string | null
  price: number
  currency: string
  estimated_delivery_date: string
}

export interface TrackingEvent {
  status: string
  location?: string
  timestamp: string
}

export interface TrackingResponse {
  tracking_code: string
  carrier: string
  service: string
  status: string
  history: TrackingEvent[]
  estimated_delivery_date: string
}

export const shippingService = {
  async quote(payload: QuoteRequest): Promise<QuoteResponse> {
    const { data } = await api.post('/shipping/quote', payload)
    return data
  },

  async createShipment(payload: CreateShipmentRequest): Promise<CreateShipmentResponse> {
    const { data } = await api.post('/shipping/shipments', payload)
    return data
  },

  async track(trackingCode: string): Promise<TrackingResponse> {
    const { data } = await api.get(`/shipping/track/${trackingCode}`)
    return data
  },
}
