import React, { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { oauth2Service } from '../services/oauth2Service'
import { useAuth } from '../context/AuthContext'
import './Login.css'

function OAuth2Callback() {
  const navigate = useNavigate()
  const location = useLocation()
  const { verifyToken } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      // URL에서 code와 returnUrl 파라미터 추출
      // 가이드에 따르면 ig-member가 콜백 URL에 code를 추가하여 리다이렉트
      // 형식: http://localhost:8400/oauth2/callback?returnUrl=%2F&code={code}
      const urlParams = new URLSearchParams(location.search)
      const code = urlParams.get('code')
      const returnUrl = urlParams.get('returnUrl')
      const error = urlParams.get('error')

      if (error) {
        console.error('OAuth2 에러:', error)
        navigate('/login?error=oauth2_failed')
        return
      }

      if (!code) {
        console.error('인증 코드가 없습니다')
        navigate('/login?error=no_code')
        return
      }

      try {
        // 일회용 코드로 토큰과 사용자 정보 가져오기
        const response = await fetch(`http://localhost:8201/api/auth/token/${code}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        const result = await response.json()

        if (result.success && result.data) {
          const { token, user } = result.data

          // 토큰과 사용자 정보 저장
          localStorage.setItem('token', token)
          localStorage.setItem('user', JSON.stringify(user))

          // 토큰 검증하여 사용자 정보 업데이트
          await verifyToken(token)

          // returnUrl로 리다이렉트 (없으면 홈으로)
          const redirectPath = returnUrl ? decodeURIComponent(returnUrl) : '/'
          navigate(redirectPath)
        } else {
          // 토큰 교환 실패
          console.error('토큰 교환 실패:', result.message)
          navigate('/login?error=token_exchange_failed')
        }
      } catch (error) {
        console.error('OAuth2 콜백 처리 중 오류:', error)
        navigate('/login?error=unknown')
      }
    }

    handleCallback()
  }, [navigate, location, verifyToken])

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <h1>맡길랩 엔터프라이즈</h1>
          <p className="login-subtitle">로그인 처리 중...</p>
        </div>
      </div>
    </div>
  )
}

export default OAuth2Callback

