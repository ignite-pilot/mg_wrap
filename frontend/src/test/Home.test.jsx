import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Home from '../pages/Home'
import { AuthProvider } from '../context/AuthContext'

// Mock AuthContext
const mockAuthContext = {
  user: null,
}

vi.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }) => children,
}))

describe('Home', () => {
  beforeEach(() => {
    mockAuthContext.user = null
  })
  
  it('renders hero section for non-logged in users (2.1)', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByText('짐을 맡기는 가장 쉬운 방법')).toBeInTheDocument()
    expect(screen.getByText(/포장, 배송, 보관까지/)).toBeInTheDocument()
    expect(screen.getByText('맡길랩')).toBeInTheDocument()
  })
  
  it('renders 4 feature cards (2.1)', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByText('공간형 자산보관')).toBeInTheDocument()
    expect(screen.getByText('BOX형 자산보관')).toBeInTheDocument()
    expect(screen.getByText('실시간 자산 관리')).toBeInTheDocument()
    expect(screen.getByText('회수 및 폐기 신청')).toBeInTheDocument()
  })
  
  it('shows start button for non-logged in users (2.1)', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByText('시작하기')).toBeInTheDocument()
  })
  
  it('shows quick actions for logged in users (2.2)', () => {
    mockAuthContext.user = { id: 1, name: 'Test User', email: 'test@example.com' }
    
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByText('빠른 메뉴')).toBeInTheDocument()
    expect(screen.getByText('보관 신청')).toBeInTheDocument()
    expect(screen.getByText('보관 자산 관리')).toBeInTheDocument()
    expect(screen.getByText('회수 현황')).toBeInTheDocument()
    expect(screen.getByText('폐기 현황')).toBeInTheDocument()
  })
  
  it('renders pricing section (2.1, 2.2)', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByText('요금 정책')).toBeInTheDocument()
  })
})

