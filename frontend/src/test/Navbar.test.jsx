import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { AuthProvider } from '../context/AuthContext'

// Mock useNavigate and useLocation
const mockNavigate = vi.fn()
const mockLocation = { pathname: '/' }

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  }
})

// Mock AuthContext
const mockAuthContext = {
  user: null,
  logout: vi.fn(),
}

vi.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }) => children,
}))

describe('Navbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthContext.user = null
  })
  
  it('renders logo and enterprise text (7.1)', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
    expect(screen.getByAltText('맡길랩 로고')).toBeInTheDocument()
    expect(screen.getByText('엔터프라이즈')).toBeInTheDocument()
  })
  
  it('shows login button when user is not logged in (1.1, 7.1)', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
    expect(screen.getByText('로그인')).toBeInTheDocument()
  })
  
  it('shows user menu when user is logged in (7.1)', () => {
    mockAuthContext.user = { id: 1, name: 'Test User', email: 'test@example.com' }
    
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
    expect(screen.getByText('Test User님')).toBeInTheDocument()
    expect(screen.getByText('로그아웃')).toBeInTheDocument()
    expect(screen.getByText('보관 신청')).toBeInTheDocument()
    expect(screen.getByText('보관 자산')).toBeInTheDocument()
    expect(screen.getByText('회수 현황')).toBeInTheDocument()
    expect(screen.getByText('폐기 현황')).toBeInTheDocument()
  })
})

