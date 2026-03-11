import React, { useState, useEffect } from 'react'
import DatePicker from 'react-datepicker'
import { ko } from 'date-fns/locale'
import 'react-datepicker/dist/react-datepicker.css'
import api from '../services/api'
import './Assets.css'

const ASSET_CATEGORIES = {
  'office_supplies': '사무용품',
  'documents': '서류',
  'equipment': '장비',
  'furniture': '가구',
  'clothing': '의류',
  'appliances': '가전',
  'other': '기타'
}

function Assets() {
  const [assets, setAssets] = useState([])
  const [applications, setApplications] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    application_date: '',
    asset_category: 'office_supplies',
    special_notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [selectedApplication, setSelectedApplication] = useState('')

  useEffect(() => {
    loadApplications()
    loadAssets()
  }, [])

  useEffect(() => {
    if (selectedApplication) {
      loadAssets(selectedApplication)
    } else {
      loadAssets()
    }
  }, [selectedApplication])

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

  const loadAssets = async (applicationId = null) => {
    try {
      const params = applicationId ? { storage_application_id: applicationId } : {}
      const response = await api.get('/assets/list', { params })
      if (response.data.success) {
        setAssets(response.data.assets)
      }
    } catch (error) {
      console.error('Failed to load assets:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!selectedApplication) {
      setError('보관 신청을 선택해주세요.')
      return
    }
    
    setLoading(true)
    setError(null)
    setSuccess(null)

    const submitData = {
      ...formData,
      storage_application_id: selectedApplication
    }

    try {
      const response = await api.post('/assets/create', submitData)
      if (response.data.success) {
        setSuccess('자산이 등록되었습니다.')
        setShowForm(false)
        setFormData({
          application_date: '',
          asset_category: 'office_supplies',
          special_notes: ''
        })
        loadAssets(selectedApplication || null)
      }
    } catch (error) {
      setError(error.response?.data?.error || '등록 실패')
    } finally {
      setLoading(false)
    }
  }

  const handleExcelUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const applicationId = formData.storage_application_id || selectedApplication
    if (!applicationId) {
      setError('보관 신청을 선택해주세요.')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    const formDataToSend = new FormData()
    formDataToSend.append('file', file)
    formDataToSend.append('storage_application_id', applicationId)

    try {
      const response = await api.post('/assets/upload', formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (response.data.success) {
        setSuccess(`${response.data.created_count}개의 자산이 등록되었습니다.`)
        loadAssets(selectedApplication || null)
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || '업로드 실패'
      setError(errorMessage)
      console.error('Excel upload error:', error)
    } finally {
      setLoading(false)
      // 파일 입력 초기화
      e.target.value = ''
    }
  }

  const handleRetrievalRequest = async (assetId) => {
    if (!window.confirm('회수 신청하시겠습니까?')) return

    try {
      const response = await api.post('/retrieval/request', { asset_id: assetId })
      if (response.data.success) {
        setSuccess('회수 신청이 완료되었습니다.')
        loadAssets(selectedApplication || null)
      }
    } catch (error) {
      setError(error.response?.data?.error || '회수 신청 실패')
    }
  }

  const handleDisposalRequest = async (assetId) => {
    if (!window.confirm('폐기 신청하시겠습니까?')) return

    try {
      const response = await api.post('/disposal/request', { asset_id: assetId })
      if (response.data.success) {
        setSuccess('폐기 신청이 완료되었습니다.')
        loadAssets(selectedApplication || null)
      }
    } catch (error) {
      setError(error.response?.data?.error || '폐기 신청 실패')
    }
  }

  return (
    <div className="assets-page">
      <div className="container">
        <h1>보관 자산 현황</h1>

      <div className="card">
        <div className="assets-header">
          <div className="form-group" style={{ maxWidth: '300px' }}>
            <label>보관 신청 선택</label>
            <select
              value={selectedApplication}
              onChange={(e) => setSelectedApplication(e.target.value)}
            >
              <option value="">전체</option>
              {applications.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.storage_type === 'space' ? '공간형' : 'BOX형'} - {new Date(app.created_at).toLocaleDateString('ko-KR')}
                </option>
              ))}
            </select>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              setShowForm(!showForm)
              if (!showForm) {
                setSuccess(null)
                setError(null)
              }
            }}
          >
            {showForm ? '취소' : '자산 등록'}
          </button>
        </div>

        {showForm && (
          <div className="asset-form">
            <h3>자산 등록</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>보관 신청일 *</label>
                <DatePicker
                  selected={formData.application_date ? new Date(formData.application_date) : null}
                  onChange={(date) => {
                    const dateString = date ? date.toISOString().split('T')[0] : ''
                    setFormData({ ...formData, application_date: dateString })
                  }}
                  dateFormat="yyyy년 MM월 dd일"
                  placeholderText="날짜를 선택하세요"
                  className="date-picker-input"
                  locale={ko}
                  required
                  isClearable
                  showYearDropdown
                  showMonthDropdown
                  dropdownMode="select"
                  yearDropdownItemNumber={15}
                  scrollableYearDropdown
                />
              </div>

              <div className="form-group">
                <label>자산 분류 *</label>
                <select
                  value={formData.asset_category}
                  onChange={(e) => setFormData({ ...formData, asset_category: e.target.value })}
                  required
                >
                  {Object.entries(ASSET_CATEGORIES).map(([key, value]) => (
                    <option key={key} value={key}>{value}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>특이사항</label>
                <textarea
                  value={formData.special_notes}
                  onChange={(e) => setFormData({ ...formData, special_notes: e.target.value })}
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  등록
                </button>
              </div>
            </form>

            <div className="excel-upload">
              <h4>엑셀 일괄 업로드</h4>
              <p>
                엑셀 파일 형식: 보관 신청일, 자산 분류, 특이사항
                {' '}
                <a href="/sample_assets.xlsx" download className="excel-download-link">
                  샘플 파일 다운로드
                </a>
              </p>
              <label htmlFor="excel-file-input" className="excel-file-label">
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleExcelUpload}
                  disabled={loading}
                  id="excel-file-input"
                  style={{ display: 'none' }}
                />
                <span className="btn btn-primary">파일 선택</span>
              </label>
            </div>
          </div>
        )}

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
      </div>

      <div className="card">
        <h2>자산 목록</h2>
        {assets.length === 0 ? (
          <p>등록된 자산이 없습니다.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>자산번호</th>
                <th>보관 신청일</th>
                <th>보관 시작일</th>
                <th>자산 분류</th>
                <th>특이사항</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.asset_number}</td>
                  <td>{new Date(asset.application_date).toLocaleDateString('ko-KR')}</td>
                  <td>{asset.storage_start_date ? new Date(asset.storage_start_date).toLocaleDateString('ko-KR') : '-'}</td>
                  <td>{ASSET_CATEGORIES[asset.asset_category] || asset.asset_category}</td>
                  <td>{asset.special_notes || '-'}</td>
                  <td>
                    <span className={`badge badge-${getStatusBadge(asset.status)}`}>
                      {getStatusText(asset.status)}
                    </span>
                  </td>
                  <td>
                    {asset.status === 'stored' && (
                      <>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleRetrievalRequest(asset.id)}
                        >
                          회수 신청
                        </button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDisposalRequest(asset.id)}
                          style={{ marginLeft: '5px' }}
                        >
                          폐기 신청
                        </button>
                      </>
                    )}
                  </td>
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

function getStatusText(status) {
  const statusMap = {
    'stored': '보관중',
    'retrieval_requested': '회수 신청',
    'retrieval_cancelled': '회수 취소',
    'retrieved': '회수 완료',
    'disposal_requested': '폐기 신청',
    'disposal_cancelled': '폐기 취소',
    'disposed': '폐기 완료'
  }
  return statusMap[status] || status
}

function getStatusBadge(status) {
  if (status === 'stored') return 'success'
  if (status.includes('requested')) return 'warning'
  if (status.includes('cancelled')) return 'info'
  if (status.includes('completed') || status.includes('retrieved') || status.includes('disposed')) return 'success'
  return 'info'
}

export default Assets

