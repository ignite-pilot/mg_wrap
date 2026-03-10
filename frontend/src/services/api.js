import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 요청 인터셉터: 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 401 에러 시 로그아웃
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 로그인 페이지로 리다이렉트하되, localStorage의 사용자 정보는 유지
      // (페이지 이동 시 토큰 검증이 실패할 수 있지만, 사용자 정보는 유지)
      const savedUser = localStorage.getItem('user')
      if (!savedUser) {
        // 사용자 정보가 없으면 완전히 로그아웃
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else {
        // 사용자 정보가 있으면 토큰만 제거하고 로그인 페이지로 이동
        // (사용자가 다시 로그인할 수 있도록)
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

