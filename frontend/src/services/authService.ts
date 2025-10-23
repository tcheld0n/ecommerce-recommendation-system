import { api } from './api'
import { User, UserCreate, UserLogin, Token, UserUpdate } from '@/types/user'

export const authService = {
  async register(userData: UserCreate): Promise<Token> {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  async login(loginData: UserLogin): Promise<Token> {
    const response = await api.post('/auth/login', loginData)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<Token> {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me')
    return response.data
  },

  async updateUser(userData: UserUpdate): Promise<User> {
    const response = await api.put('/users/me', userData)
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  // Helper methods
  setTokens(tokens: Token): void {
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  },

  getTokens(): { access_token: string | null; refresh_token: string | null } {
    return {
      access_token: localStorage.getItem('access_token'),
      refresh_token: localStorage.getItem('refresh_token')
    }
  },

  clearTokens(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }
}
