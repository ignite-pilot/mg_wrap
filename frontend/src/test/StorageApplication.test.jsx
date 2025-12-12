import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import StorageApplication from '../pages/StorageApplication'
import * as api from '../services/api'

// Mock API
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

// Mock AuthContext
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1, name: 'Test', email: 'test@test.com' } }),
}))

describe('StorageApplication', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.default.get.mockResolvedValue({
      data: { success: true, applications: [] }
    })
  })
  
  it('renders storage type selector (3.1, 3.2)', () => {
    render(
      <BrowserRouter>
        <StorageApplication />
      </BrowserRouter>
    )
    expect(screen.getByText('보관 유형 선택')).toBeInTheDocument()
    expect(screen.getByText('공간형 자산보관')).toBeInTheDocument()
    expect(screen.getByText('BOX형 자산보관')).toBeInTheDocument()
  })
  
  it('shows space input when space type is selected (3.1)', () => {
    render(
      <BrowserRouter>
        <StorageApplication />
      </BrowserRouter>
    )
    const spaceButton = screen.getByText('공간형 자산보관')
    fireEvent.click(spaceButton)
    expect(screen.getByLabelText(/평수/)).toBeInTheDocument()
  })
  
  it('shows box input when box type is selected (3.2)', () => {
    render(
      <BrowserRouter>
        <StorageApplication />
      </BrowserRouter>
    )
    const boxButton = screen.getByText('BOX형 자산보관')
    fireEvent.click(boxButton)
    expect(screen.getByLabelText(/BOX 수량/)).toBeInTheDocument()
  })
  
  it('validates input before estimate (3.3)', async () => {
    render(
      <BrowserRouter>
        <StorageApplication />
      </BrowserRouter>
    )
    const estimateButton = screen.getByText('견적 조회')
    fireEvent.click(estimateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/평수를 올바르게 입력해주세요/)).toBeInTheDocument()
    })
  })
  
  it('calls API for estimate (3.1)', async () => {
    api.default.post.mockResolvedValue({
      data: {
        success: true,
        estimated_price: 300000,
      },
    })
    
    render(
      <BrowserRouter>
        <StorageApplication />
      </BrowserRouter>
    )
    const spaceInput = screen.getByLabelText(/평수/)
    fireEvent.change(spaceInput, { target: { value: '5' } })
    
    const estimateButton = screen.getByText('견적 조회')
    fireEvent.click(estimateButton)
    
    await waitFor(() => {
      expect(api.default.post).toHaveBeenCalledWith(
        '/storage/estimate',
        expect.objectContaining({
          storage_type: 'space',
          months: 1,
          space_pyeong: 5,
        })
      )
    })
  })
  
  it('shows error message on API failure (11.1)', async () => {
    api.default.post.mockRejectedValue({
      response: {
        data: { error: 'API Error' },
      },
    })
    
    render(
      <BrowserRouter>
        <StorageApplication />
      </BrowserRouter>
    )
    const spaceInput = screen.getByLabelText(/평수/)
    fireEvent.change(spaceInput, { target: { value: '5' } })
    
    const estimateButton = screen.getByText('견적 조회')
    fireEvent.click(estimateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/API Error/)).toBeInTheDocument()
    })
  })
})

