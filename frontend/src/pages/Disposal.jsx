import React, { useState, useEffect } from 'react'
import api from '../services/api'
import './Disposal.css'

const STATUS_MAP = {
  'preparing': { text: '폐기 준비중', badge: 'warning' },
  'completed': { text: '폐기 완료', badge: 'success' },
  'cancelled': { text: '취소됨', badge: 'danger' }
}

const ASSET_CATEGORIES = {
  'office_supplies': '사무용품',
  'documents': '서류',
  'equipment': '장비',
  'furniture': '가구',
  'clothing': '의류',
  'appliances': '가전',
  'other': '기타'
}

function Disposal() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  useEffect(() => {
    loadRequests()
  }, [])

  const loadRequests = async () => {
    try {
      const response = await api.get('/disposal/list')
      if (response.data.success) {
        // 취소된 항목 제외
        const filteredRequests = response.data.disposal_requests.filter(
          request => request.status !== 'cancelled'
        )
        setRequests(filteredRequests)
      }
    } catch (error) {
      console.error('Failed to load disposal requests:', error)
    }
  }

  const handleCancel = async (requestId) => {
    if (!window.confirm('폐기를 취소하시겠습니까?')) return

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await api.post(`/disposal/${requestId}/cancel`)
      if (response.data.success) {
        setSuccess('폐기가 취소되었습니다.')
        loadRequests()
      }
    } catch (error) {
      setError(error.response?.data?.error || '취소 실패')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="disposal-page">
      <div className="container">
        <h1>폐기 현황</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        {requests.length === 0 ? (
          <p>폐기 신청 내역이 없습니다.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>자산번호</th>
                <th>보관 신청일</th>
                <th>보관 시작일</th>
                <th>자산 분류</th>
                <th>특이사항</th>
                <th>신청일</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => {
                const status = STATUS_MAP[request.status] || { text: request.status, badge: 'info' }
                return (
                  <tr key={request.id}>
                    <td>{request.asset?.asset_number}</td>
                    <td>{request.asset?.application_date ? new Date(request.asset.application_date).toLocaleDateString('ko-KR') : '-'}</td>
                    <td>{request.asset?.storage_start_date ? new Date(request.asset.storage_start_date).toLocaleDateString('ko-KR') : '-'}</td>
                    <td>{request.asset?.asset_category ? ASSET_CATEGORIES[request.asset.asset_category] || request.asset.asset_category : '-'}</td>
                    <td>{request.asset?.special_notes || '-'}</td>
                    <td>{new Date(request.requested_at).toLocaleDateString('ko-KR')}</td>
                    <td>
                      <span className={`badge badge-${status.badge}`}>
                        {status.text}
                      </span>
                    </td>
                    <td>
                      {request.status === 'preparing' && (
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleCancel(request.id)}
                          disabled={loading}
                        >
                          폐기 취소
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
      </div>
    </div>
  )
}

export default Disposal

