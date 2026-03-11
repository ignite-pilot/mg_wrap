import React, { useState, useEffect } from 'react'
import { getPosts, getPost, getBoardInfo, incrementViewCount } from '../services/boardService'
import './InquiryBoard.css'

function InquiryBoard() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [selectedPost, setSelectedPost] = useState(null)
  const [boardName, setBoardName] = useState('문의하기')
  const [boardId, setBoardId] = useState(null)

  useEffect(() => {
    loadBoardInfo()
    loadPosts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page])

  const loadBoardInfo = async () => {
    try {
      const boardInfo = await getBoardInfo()
      if (boardInfo) {
        if (boardInfo.name) {
          setBoardName(boardInfo.name)
        }
        if (boardInfo.id) {
          setBoardId(boardInfo.id)
        }
      }
    } catch (err) {
      console.error('게시판 정보 로드 오류:', err)
      // 에러가 발생해도 기본값 '문의하기' 사용
    }
  }

  const loadPosts = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getPosts(page, 10)
      setPosts(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error('게시글 로드 오류:', err)
      setError('게시글을 불러오는데 실패했습니다. 게시판 서버를 확인해주세요.')
      setPosts([])
    } finally {
      setLoading(false)
    }
  }

  const handleViewPost = async (post) => {
    if (selectedPost?.id === post.id) {
      setSelectedPost(null)
      return
    }
    
    // 게시글 상세 정보 가져오기 (본문 포함)
    setLoading(true)
    try {
      // 조회수 증가 (비동기로 실행, 실패해도 게시글 조회는 계속 진행)
      incrementViewCount(post.id).then(() => {
        // 조회수 증가 후 목록 새로고침
        loadPosts()
      }).catch(() => {
        // 조회수 증가 실패해도 무시
      })
      
      const postDetail = await getPost(post.id)
      console.log('게시글 상세 정보:', postDetail) // 디버깅용
      setSelectedPost(postDetail)
      
      // 조회수 업데이트를 위해 목록의 해당 게시글도 업데이트
      setPosts(prevPosts => 
        prevPosts.map(p => 
          p.id === post.id ? { ...p, view_count: (p.view_count || 0) + 1 } : p
        )
      )
    } catch (err) {
      console.error('게시글 상세 정보를 불러오는데 실패했습니다.', err)
      setError('게시글을 불러오는데 실패했습니다.')
      // 상세 정보를 가져오지 못해도 목록의 정보로 표시
      setSelectedPost(post)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (err) {
      return dateString
    }
  }

  return (
    <div className="inquiry-board">
      <div className="inquiry-board-header">
        <h2>{boardName}</h2>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading && posts.length === 0 ? (
        <div className="loading">로딩 중...</div>
      ) : posts.length === 0 ? (
        <div className="empty-message">게시글이 없습니다.</div>
      ) : (
        <div className="posts-list">
          {posts.map((post) => (
            <div key={post.id} className="post-item">
              <div 
                className="post-header" 
                onClick={() => handleViewPost(post)}
              >
                <h3 className="post-title">
                  {post.prefix && <span className="post-prefix">[{post.prefix}]</span>}
                  {post.title}
                </h3>
                <div className="post-meta">
                  {/* FAQ 게시판(ID: 1)에서는 글쓴이 이름 비노출 */}
                  {boardId !== 1 && <span className="post-author">{post.author_name}</span>}
                  <span className="post-date">{formatDate(post.created_at)}</span>
                  <span className="post-stats">
                    조회 {post.view_count}
                  </span>
                </div>
              </div>
              
              {selectedPost?.id === post.id && (
                <div className="post-detail">
                  <div 
                    className="post-content"
                    dangerouslySetInnerHTML={{ 
                      __html: selectedPost.content || '내용이 없습니다.' 
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="pagination">
        <button 
          onClick={() => setPage(prev => Math.max(1, prev - 1))} 
          disabled={page === 1}
        >
          이전
        </button>
        <span>페이지 {page}</span>
        <button 
          onClick={() => setPage(prev => prev + 1)} 
          disabled={posts.length < 10}
        >
          다음
        </button>
      </div>
    </div>
  )
}

export default InquiryBoard

