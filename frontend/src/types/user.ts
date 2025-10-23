export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_admin: boolean
  created_at: string
  updated_at: string
  reading_preferences?: Record<string, any>
}

export interface UserCreate {
  email: string
  full_name: string
  password: string
  reading_preferences?: Record<string, any>
}

export interface UserUpdate {
  full_name?: string
  reading_preferences?: Record<string, any>
}

export interface UserLogin {
  email: string
  password: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}
