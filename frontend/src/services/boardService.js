import api from './api'

// 게시글 목록 조회
export const getPosts = async (page = 1, perPage = 10) => {
  const response = await api.get('/board/posts', {
    params: { page, per_page: perPage }
  })
  return response.data
}

// 게시글 상세 조회
export const getPost = async (postId) => {
  const response = await api.get(`/board/posts/${postId}`)
  return response.data
}

// 게시글 조회수 증가
export const incrementViewCount = async (postId) => {
  try {
    const response = await api.post(`/board/posts/${postId}/view`)
    return response.data
  } catch (error) {
    // 조회수 증가 실패해도 에러를 throw하지 않음
    console.warn('조회수 증가 실패:', error)
    return { success: false }
  }
}

// 게시글 작성
export const createPost = async (postData) => {
  const response = await api.post('/board/posts', postData)
  return response.data
}

// 게시글 수정
export const updatePost = async (postId, postData) => {
  const response = await api.put(`/board/posts/${postId}`, postData)
  return response.data
}

// 게시글 삭제
export const deletePost = async (postId) => {
  const response = await api.delete(`/board/posts/${postId}`)
  return response.data
}

// 댓글 목록 조회
export const getComments = async (postId) => {
  const response = await api.get(`/board/posts/${postId}/comments`)
  return response.data
}

// 댓글 작성
export const createComment = async (postId, commentData) => {
  const response = await api.post(`/board/posts/${postId}/comments`, commentData)
  return response.data
}

// 게시판 정보 조회
export const getBoardInfo = async () => {
  const response = await api.get('/board/board')
  return response.data
}

