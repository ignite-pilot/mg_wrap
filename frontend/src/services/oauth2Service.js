/**
 * ig-member OAuth2 서비스
 * 가이드에 따라 구현된 OAuth2 인증 클라이언트
 */

const IG_MEMBER_API_URL = 'http://localhost:8201/api'

class OAuth2Service {
  /**
   * 소셜 로그인 시작
   * @param {string} provider - 'google' 또는 'naver'
   */
  startOAuth2Login(provider) {
    window.location.href = `${IG_MEMBER_API_URL}/login/oauth2/authorization/${provider}`
  }

  /**
   * OAuth2 콜백 처리
   * URL에서 code를 추출하고 토큰으로 교환
   * @returns {Promise<{token: string, user: object} | null>}
   */
  async handleOAuth2Callback() {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const error = urlParams.get('error')

    if (error) {
      console.error('OAuth2 에러:', error)
      return null
    }

    if (!code) {
      console.error('인증 코드가 없습니다')
      return null
    }

    try {
      const response = await fetch(`${IG_MEMBER_API_URL}/auth/token/${code}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (data.success) {
        return {
          token: data.data.token,
          user: data.data.user
        }
      } else {
        console.error('토큰 교환 실패:', data.message)
        return null
      }
    } catch (error) {
      console.error('토큰 교환 중 오류:', error)
      return null
    }
  }

  /**
   * 현재 사용자 정보 조회
   * @param {string} token - JWT 토큰
   * @returns {Promise<object | null>}
   */
  async getCurrentUser(token) {
    try {
      const response = await fetch(`${IG_MEMBER_API_URL}/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (data.success) {
        return data.data
      }
      return null
    } catch (error) {
      console.error('사용자 정보 조회 실패:', error)
      return null
    }
  }
}

export const oauth2Service = new OAuth2Service()

