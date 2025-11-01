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
  },

  /**
   * Verifica se o token está expirado ou próximo de expirar e renova se necessário
   * @returns Promise<boolean> - true se o token está válido (renovado ou não expirado), false se não foi possível renovar
   */
  async ensureValidToken(): Promise<boolean> {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')

    console.log('Verificando validade do token...', {
      hasAccessToken: !!accessToken,
      hasRefreshToken: !!refreshToken,
      accessTokenLength: accessToken?.length || 0,
      refreshTokenLength: refreshToken?.length || 0
    })

    if (!accessToken || !refreshToken) {
      console.warn('Tokens não encontrados no localStorage')
      return false
    }

    try {
      // Tentar decodificar o token JWT (sem verificar assinatura, apenas para ler o exp)
      const tokenParts = accessToken.split('.')
      if (tokenParts.length !== 3) {
        console.warn('Token com formato inválido (não tem 3 partes)')
        // Tentar renovar mesmo assim
        console.log('Tentando renovar token devido a formato inválido...')
        return await this.tryRefreshToken()
      }

      let payload: any
      try {
        const decodedPayload = atob(tokenParts[1])
        payload = JSON.parse(decodedPayload)
        console.log('Token decodificado com sucesso', {
          hasExp: !!payload.exp,
          hasSub: !!payload.sub,
          type: payload.type
        })
      } catch (decodeError) {
        console.error('Erro ao decodificar payload do token:', decodeError)
        // Tentar renovar se não conseguir decodificar
        return await this.tryRefreshToken()
      }

      const exp = payload.exp
      
      if (!exp) {
        console.warn('Token não contém informação de expiração (exp)')
        // Tentar renovar mesmo assim para garantir token válido
        console.log('Tentando renovar token para garantir validade...')
        return await this.tryRefreshToken()
      }

      const now = Math.floor(Date.now() / 1000)
      const timeUntilExpiry = exp - now

      console.log('Informações do token:', {
        expiresIn: timeUntilExpiry,
        expiresAt: new Date(exp * 1000).toISOString(),
        currentTime: new Date().toISOString(),
        isExpired: timeUntilExpiry <= 0,
        needsRefresh: timeUntilExpiry < 300
      })

      // Se o token já expirou ou está próximo de expirar (menos de 5 minutos), renovar
      if (timeUntilExpiry <= 0) {
        console.log('Token EXPIRADO, renovando imediatamente...')
        return await this.tryRefreshToken()
      }

      if (timeUntilExpiry < 300) {
        console.log('Token próximo de expirar (menos de 5 min), renovando proativamente...', {
          expiresIn: timeUntilExpiry,
          expiresAt: new Date(exp * 1000).toISOString()
        })
        return await this.tryRefreshToken()
      }

      // Token ainda válido por mais de 5 minutos
      console.log('Token válido, não precisa renovar', {
        expiresIn: timeUntilExpiry,
        expiresAt: new Date(exp * 1000).toISOString()
      })
      return true
    } catch (error: any) {
      console.error('Erro inesperado ao verificar token:', error)
      // Em caso de erro ao decodificar, tentar renovar
      console.log('Tentando renovar token devido a erro na verificação...')
      return await this.tryRefreshToken()
    }
  },

  /**
   * Tenta renovar o token usando o refresh token
   * @returns Promise<boolean> - true se renovado com sucesso, false caso contrário
   */
  async tryRefreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      console.error('Refresh token não disponível no localStorage')
      return false
    }

    try {
      console.log('Tentando renovar token proativamente...', {
        refreshTokenLength: refreshToken.length,
        refreshTokenPreview: refreshToken.substring(0, 20) + '...'
      })
      
      const tokens = await this.refreshToken(refreshToken)
      
      console.log('Resposta do refresh recebida:', {
        hasAccessToken: !!tokens.access_token,
        hasRefreshToken: !!tokens.refresh_token,
        accessTokenLength: tokens.access_token?.length || 0
      })
      
      if (!tokens.access_token) {
        console.error('Resposta do refresh não contém access_token')
        return false
      }
      
      this.setTokens(tokens)
      console.log('Token renovado e armazenado com sucesso')
      return true
    } catch (error: any) {
      console.error('Erro ao renovar token:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        detail: error.response?.data?.detail || error.response?.data?.message,
        data: error.response?.data,
        message: error.message,
        code: error.code
      })
      
      // Se o refresh token também está expirado, limpar tokens
      if (error.response?.status === 401 || error.response?.status === 400) {
        console.error('Refresh token inválido ou expirado, limpando tokens')
        this.clearTokens()
      }
      return false
    }
  }
}
