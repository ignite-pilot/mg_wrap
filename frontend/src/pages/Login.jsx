import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Login.css'

function Login() {
  const { loginWithEmail, loginWithNaver, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // 로그인 페이지에서는 user가 설정되면 홈으로 이동
    // 하지만 로그인 중일 때는 이동하지 않도록 함
    if (user && !loading) {
      navigate('/')
    }
  }, [user, navigate, loading])

  // 에러 파라미터 확인 (OAuth2 콜백 실패 시)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const error = urlParams.get('error')
    
    if (error) {
      setError('로그인에 실패했습니다: ' + error)
    }
  }, [])

  const handleEmailLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await loginWithEmail(email, password)
      if (result.success) {
        // 로그인 성공 - user 상태가 업데이트될 때까지 잠시 대기
        // setUser는 비동기로 상태를 업데이트하므로, 
        // useEffect가 user 변경을 감지하여 홈으로 이동시킴
        // 최대 1초 대기 후에도 user가 없으면 에러 표시
        let attempts = 0
        const checkUser = setInterval(() => {
          attempts++
          if (user) {
            clearInterval(checkUser)
            setLoading(false)
            // user가 설정되었으므로 useEffect가 홈으로 이동시킴
          } else if (attempts >= 20) {
            // 2초 후에도 user가 없으면 에러
            clearInterval(checkUser)
            setError('로그인은 성공했지만 사용자 정보를 불러오지 못했습니다.')
            setLoading(false)
          }
        }, 100)
      } else {
        setError(result.error || '로그인에 실패했습니다.')
        setLoading(false)
      }
    } catch (err) {
      setError('로그인 중 오류가 발생했습니다.')
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <h1>맡길랩 엔터프라이즈</h1>
          <p className="login-subtitle">로그인하여 서비스를 이용하세요</p>

          {/* 자체 로그인 폼 */}
          <form className="login-form" onSubmit={handleEmailLogin}>
            <div className="form-group">
              <input
                type="email"
                placeholder="이메일"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="비밀번호"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            {error && <div className="error-message">{error}</div>}
            <button 
              type="submit" 
              className="login-button"
              disabled={loading}
            >
              {loading ? '로그인 중...' : '로그인'}
            </button>
          </form>

          {/* 회원 가입 및 비밀번호 찾기 링크 */}
          <div className="login-links">
            <a 
              href="https://ig-member.ig-pilot.com/register" 
              target="_blank" 
              rel="noopener noreferrer"
              className="login-link"
            >
              회원 가입
            </a>
            <span className="link-divider">|</span>
            <a 
              href="https://ig-member.ig-pilot.com/forgot-password" 
              target="_blank" 
              rel="noopener noreferrer"
              className="login-link"
            >
              비밀번호 찾기
            </a>
          </div>

          {/* 구분선 */}
          <div className="divider">
            <span>또는</span>
          </div>

          {/* 소셜 로그인 버튼 */}
          <div className="social-login">
            <button 
              type="button"
              className="social-button naver-button"
              onClick={loginWithNaver}
              disabled={loading}
            >
              <svg className="social-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#03C75A" d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z"/>
              </svg>
              네이버로 로그인
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
