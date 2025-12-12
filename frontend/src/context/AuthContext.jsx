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
    if (token) {
      verifyToken(token)
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async (token) => {
    try {
      // 가이드에 따라 ig-member API 직접 호출
      const response = await fetch('http://localhost:8201/api/users/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (data.success && data.data) {
        setUser(data.data)
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    } catch (error) {
      localStorage.removeItem('token')
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
        if (token) {
          localStorage.setItem('token', token)
          // 토큰 검증하여 사용자 정보 가져오기
          await verifyToken(token)
          return { success: true }
        }
      }
      return { success: false, error: response.data.error || '로그인 실패' }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || '로그인 실패'
      console.error('Login error:', error)
      return { success: false, error: errorMessage }
    }
  }

  // Google OAuth 로그인 (ig-member OAuth2 엔드포인트로 직접 리다이렉트)
  const loginWithGoogle = () => {
    // 콜백 URL에 mg-wrap home(/)을 returnUrl로 포함
    const callbackUrl = `${window.location.origin}/oauth2/callback?returnUrl=${encodeURIComponent('/')}`
    // ig-member OAuth2 엔드포인트로 직접 리다이렉트 (로그인 페이지 거치지 않음)
    // returnUrl을 쿼리 파라미터로 전달
    const returnUrl = encodeURIComponent(callbackUrl)
    window.location.href = `http://localhost:8201/api/login/oauth2/authorization/google?returnUrl=${returnUrl}`
  }

  // 네이버 OAuth 로그인 (ig-member OAuth2 엔드포인트로 직접 리다이렉트)
  const loginWithNaver = () => {
    // 콜백 URL에 mg-wrap home(/)을 returnUrl로 포함
    const callbackUrl = `${window.location.origin}/oauth2/callback?returnUrl=${encodeURIComponent('/')}`
    // ig-member OAuth2 엔드포인트로 직접 리다이렉트 (로그인 페이지 거치지 않음)
    // returnUrl을 쿼리 파라미터로 전달
    const returnUrl = encodeURIComponent(callbackUrl)
    window.location.href = `http://localhost:8201/api/login/oauth2/authorization/naver?returnUrl=${returnUrl}`
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

