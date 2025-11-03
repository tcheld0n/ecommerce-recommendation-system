import { api } from './api'

export type FeatureFlags = {
  catalog: boolean
  auth: boolean
  users: boolean
  cart: boolean
  orders: boolean
  payment: boolean
  recommendation: boolean
  shipping: boolean
  personalizedRecommendations: boolean
  similarInCart: boolean
}

export const defaultFlags: FeatureFlags = {
  catalog: true,
  auth: true,
  users: true,
  cart: true,
  orders: true,
  payment: true,
  recommendation: true,
  shipping: true,
  personalizedRecommendations: true,
  similarInCart: true,
}

export const featuresService = {
  async get(): Promise<FeatureFlags> {
    const { data } = await api.get('/features')
    return { ...defaultFlags, ...data }
  },

  async update(flags: Partial<FeatureFlags>): Promise<FeatureFlags> {
    const { data } = await api.put('/features', flags)
    return { ...defaultFlags, ...data }
  }
}
