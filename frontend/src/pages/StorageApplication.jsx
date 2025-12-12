import React, { useState, useEffect } from 'react'
import api from '../services/api'
import './StorageApplication.css'

function StorageApplication() {
  const [storageType, setStorageType] = useState('space')
  const [months, setMonths] = useState(1)
  const [spacePyeong, setSpacePyeong] = useState('')
  const [boxCount, setBoxCount] = useState('')
  const [estimatedPrice, setEstimatedPrice] = useState(null)
  const [loading, setLoading] = useState(false)
  const [applications, setApplications] = useState([])
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  useEffect(() => {
    loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      const response = await api.get('/storage/list')
      if (response.data.success) {
        setApplications(response.data.applications)
      }
    } catch (error) {
      console.error('Failed to load applications:', error)
    }
  }

  const handleEstimate = async () => {
    // 입력값 검증
    const spaceValue = storageType === 'space' ? parseInt(spacePyeong) : null
    const boxValue = storageType === 'box' ? parseInt(boxCount) : null
    
    if (storageType === 'space' && (!spacePyeong || isNaN(spaceValue) || spaceValue < 1)) {
      setError('평수를 올바르게 입력해주세요. (최소 1평)')
      return
    }
    
    if (storageType === 'box' && (!boxCount || isNaN(boxValue) || boxValue < 1)) {
      setError('BOX 수량을 올바르게 입력해주세요. (최소 1개)')
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const data = {
        storage_type: storageType,
        months: months,
        ...(storageType === 'space' ? { space_pyeong: spaceValue } : { box_count: boxValue })
      }
      const response = await api.post('/storage/estimate', data)
      if (response.data.success) {
        setEstimatedPrice(response.data.estimated_price)
      }
    } catch (error) {
      setError(error.response?.data?.error || '견적 조회 실패')
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async () => {
    if (!estimatedPrice) {
      setError('먼저 견적을 조회해주세요.')
      return
    }

    // 입력값 검증
    const spaceValue = storageType === 'space' ? parseInt(spacePyeong) : null
    const boxValue = storageType === 'box' ? parseInt(boxCount) : null
    
    if (storageType === 'space' && (!spacePyeong || isNaN(spaceValue) || spaceValue < 1)) {
      setError('평수를 올바르게 입력해주세요. (최소 1평)')
      return
    }
    
    if (storageType === 'box' && (!boxCount || isNaN(boxValue) || boxValue < 1)) {
      setError('BOX 수량을 올바르게 입력해주세요. (최소 1개)')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const data = {
        storage_type: storageType,
        months: months,
        ...(storageType === 'space' ? { space_pyeong: spaceValue } : { box_count: boxValue })
      }
      const response = await api.post('/storage/apply', data)
      if (response.data.success) {
        setSuccess('보관 신청이 완료되었습니다.')
        setEstimatedPrice(null)
        // 입력값 초기화
        setSpacePyeong('')
        setBoxCount('')
        loadApplications()
      }
    } catch (error) {
      setError(error.response?.data?.error || '신청 실패')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="storage-application-page">
      <div className="container">
        <h1>보관 신청</h1>

      <div className="card">
        <h2>보관 유형 선택</h2>
        <div className="storage-type-selector">
          <button
            className={`btn ${storageType === 'space' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setStorageType('space')
              setEstimatedPrice(null)
              setError(null)
            }}
          >
            공간형 자산보관
          </button>
          <button
            className={`btn ${storageType === 'box' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setStorageType('box')
              setEstimatedPrice(null)
              setError(null)
            }}
          >
            BOX형 자산보관
          </button>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>
              {storageType === 'space' ? '평수' : 'BOX 수량'}
            </label>
            <input
              type="number"
              min="1"
              placeholder={storageType === 'space' ? '평수를 입력하세요' : 'BOX 수량을 입력하세요'}
              value={storageType === 'space' ? spacePyeong : boxCount}
              onChange={(e) => {
                const value = e.target.value
                if (storageType === 'space') {
                  setSpacePyeong(value === '' ? '' : value)
                } else {
                  setBoxCount(value === '' ? '' : value)
                }
                setEstimatedPrice(null)
              }}
            />
          </div>

          <div className="form-group">
            <label>보관 개월수</label>
            <select
              value={months}
              onChange={(e) => {
                setMonths(parseInt(e.target.value))
                setEstimatedPrice(null)
              }}
            >
              <option value={1}>1개월</option>
              <option value={3}>3개월</option>
              <option value={6}>6개월</option>
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="btn btn-primary"
            onClick={handleEstimate}
            disabled={loading}
          >
            견적 조회
          </button>
        </div>

        {estimatedPrice && (
          <div className="estimate-result">
            <h3>이용 요금</h3>
            <p className="price">{estimatedPrice.toLocaleString()}원</p>
            <button
              className="btn btn-success"
              onClick={handleApply}
              disabled={loading}
            >
              최종 신청
            </button>
          </div>
        )}

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
      </div>

      <div className="card">
        <h2>신청 내역</h2>
        {applications.length === 0 ? (
          <p>신청 내역이 없습니다.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>유형</th>
                <th>단위</th>
                <th>개월수</th>
                <th>견적 금액</th>
                <th>상태</th>
                <th>신청일</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => (
                <tr key={app.id}>
                  <td>{app.storage_type === 'space' ? '공간형' : 'BOX형'}</td>
                  <td>{app.storage_type === 'space' ? `${app.space_pyeong}평` : `${app.box_count}개`}</td>
                  <td>{app.months}개월</td>
                  <td>{parseInt(app.estimated_price).toLocaleString()}원</td>
                  <td>
                    <span className={`badge badge-${app.status === 'approved' ? 'success' : 'info'}`}>
                      {app.status === 'approved' ? '승인됨' : app.status}
                    </span>
                  </td>
                  <td>{new Date(app.created_at).toLocaleDateString('ko-KR')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      </div>
    </div>
  )
}

export default StorageApplication

