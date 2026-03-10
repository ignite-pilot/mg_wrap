import React, { createContext, useState, useContext, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (token) {
      // localStorage에 사용자 정보가 있으면 먼저 설정 (즉시 UI 업데이트)
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          setUser(userData)
        } catch (e) {
          console.error('Failed to parse saved user:', e)
        }
      }
      
      // 토큰 검증 시도 (백그라운드에서)
      verifyToken(token)
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async (token) => {
    try {
      // 백엔드의 verify 엔드포인트 사용
      const response = await api.post('/auth/verify', {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.data.success && response.data.user) {
        setUser(response.data.user)
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      } else {
        // 토큰 검증 실패 시에도 localStorage에 저장된 사용자 정보가 있으면 유지
        const savedUser = localStorage.getItem('user')
        if (!savedUser) {
          localStorage.removeItem('token')
          setUser(null)
        }
      }
    } catch (error) {
      console.error('Token verification failed:', error)
      // 토큰 검증 실패 시에도 localStorage에 저장된 사용자 정보가 있으면 유지
      const savedUser = localStorage.getItem('user')
      if (!savedUser) {
        localStorage.removeItem('token')
        setUser(null)
      }
    } finally {
      setLoading(false)
    }
  }

  // 자체 로그인 (이메일/비밀번호)
  const loginWithEmail = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      
      if (response.data.success) {
        const token = response.data.token
        const userData = response.data.user
        
        if (token && userData) {
          // 로그인 응답에 이미 사용자 정보가 포함되어 있으므로 직접 사용
          localStorage.setItem('token', token)
          localStorage.setItem('user', JSON.stringify(userData))
          setUser(userData)
          return { success: true, user: userData }
        } else if (token) {
          // 토큰만 있고 사용자 정보가 없는 경우, 백엔드의 verify 엔드포인트 사용
          localStorage.setItem('token', token)
          try {
            const verifyResponse = await api.post('/auth/verify', {}, {
              headers: { 'Authorization': `Bearer ${token}` }
            })
            if (verifyResponse.data.success && verifyResponse.data.user) {
              setUser(verifyResponse.data.user)
              localStorage.setItem('user', JSON.stringify(verifyResponse.data.user))
              return { success: true, user: verifyResponse.data.user }
            }
          } catch (verifyError) {
            console.error('Token verification failed:', verifyError)
          }
          // verify 실패 시에도 토큰은 저장하고, 사용자 정보는 나중에 가져올 수 있도록 함
          return { success: true, user: null }
        }
      }
      return { success: false, error: response.data.error || '로그인 실패' }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || '로그인 실패'
      console.error('Login error:', error)
      return { success: false, error: errorMessage }
    }
  }

  // Google OAuth 로그인 (mg-wrap 백엔드를 통해 ig-member로 리다이렉트)
  const loginWithGoogle = () => {
    // mg-wrap 백엔드의 OAuth2 엔드포인트를 통해 Google 인증 시작
    window.location.href = '/api/auth/oauth2/authorization/google'
  }

  // 네이버 OAuth 로그인 (mg-wrap 백엔드를 통해 ig-member로 리다이렉트)
  const loginWithNaver = () => {
    // mg-wrap 백엔드의 OAuth2 엔드포인트를 통해 네이버 인증 시작
    window.location.href = '/api/auth/oauth2/authorization/naver'
  }

  // 구버전 호환성을 위한 login 함수 (Google 토큰 방식)
  const login = async (googleToken) => {
    // Google OAuth 리다이렉트 방식으로 변경
    loginWithGoogle()
    return { success: false, error: '리다이렉트 중...' }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const value = {
    user,
    loading,
    login,
    loginWithEmail,
    loginWithGoogle,
    loginWithNaver,
    logout,
    verifyToken
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

