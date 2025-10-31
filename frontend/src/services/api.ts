import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.debug('Token adicionado ao header:', { 
        hasToken: !!token, 
        tokenLength: token.length,
        url: config.url 
      })
    } else {
      console.warn('Token não encontrado no localStorage para a requisição:', config.url)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const errorDetail = error.response?.data?.detail || ''
      console.log('Erro 401 detectado, tentando refresh token...', { 
        errorDetail,
        url: originalRequest.url 
      })

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          console.error('Nenhum refresh token disponível')
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          // Se o erro original era "Token necessário", melhorar mensagem
          if (errorDetail.includes('necessário') || errorDetail.includes('Token')) {
            error.response.data.detail = 'Sessão expirada. Por favor, faça login novamente.'
          }
          return Promise.reject(error)
        }

        console.log('Tentando renovar token...', { 
          refreshTokenExists: !!refreshToken,
          refreshTokenLength: refreshToken?.length,
          apiBaseUrl: API_BASE_URL
        })

        // Tentar usar o endpoint correto do API Gateway
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        })

        console.log('Resposta do refresh recebida:', { 
          status: response.status,
          hasAccessToken: !!response.data?.access_token,
          hasRefreshToken: !!response.data?.refresh_token
        })

        const { access_token, refresh_token: newRefreshToken } = response.data
        if (access_token) {
          console.log('Token renovado com sucesso')
          localStorage.setItem('access_token', access_token)
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken)
            console.log('Novo refresh token armazenado')
          }

          // Retry original request with new token - garantir que o header seja atualizado
          // Criar nova configuração da requisição para garantir que tudo está correto
          const retryConfig = {
            ...originalRequest,
            headers: {
              ...originalRequest.headers,
              Authorization: `Bearer ${access_token}`
            }
          }
          
          console.log('Reexecutando requisição original com novo token', { 
            url: originalRequest.url,
            method: originalRequest.method,
            hasAuthHeader: !!retryConfig.headers.Authorization
          })
          
          return api(retryConfig)
        } else {
          console.error('Resposta de refresh sem access_token', response.data)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          if (error.response) {
            error.response.data = {
              ...error.response.data,
              detail: 'Erro ao renovar token. Por favor, faça login novamente.'
            }
          }
          return Promise.reject(error)
        }
      } catch (refreshError: any) {
        console.error('Falha ao renovar token no interceptor:', {
          status: refreshError.response?.status,
          data: refreshError.response?.data,
          message: refreshError.message,
          url: refreshError.config?.url
        })
        
        // Mensagens de erro mais específicas
        let errorMessage = 'Erro ao renovar token'
        
        if (refreshError.response) {
          const status = refreshError.response.status
          const detail = refreshError.response.data?.detail || refreshError.response.statusText
          
          if (status === 404) {
            errorMessage = 'Endpoint de refresh não encontrado. Verifique se o auth service está rodando.'
          } else if (status === 400) {
            errorMessage = 'Refresh token inválido ou faltando'
          } else if (status === 401) {
            errorMessage = 'Refresh token expirado ou inválido'
          } else {
            errorMessage = `Erro ao renovar token: ${detail}`
          }
        } else if (refreshError.code === 'ERR_NETWORK') {
          errorMessage = 'Erro de conexão. Verifique se o servidor está rodando.'
        }
        
        // Limpar tokens se o refresh falhar
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // Proporcionar erro mais útil
        if (error.response) {
          error.response.data = {
            ...error.response.data,
            detail: `Autenticação falhou: ${errorMessage}. Por favor, faça login novamente.`
          }
        }
        
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)
