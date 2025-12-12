import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Footer from '../components/Footer'

describe('Footer', () => {
  it('renders company information (7.2)', () => {
    render(
      <BrowserRouter>
        <Footer />
      </BrowserRouter>
    )
    expect(screen.getByText('IGNITE')).toBeInTheDocument()
    expect(screen.getByText(/사업자 등록번호/)).toBeInTheDocument()
    expect(screen.getByText(/대표/)).toBeInTheDocument()
  })
  
  it('renders service links (7.2, 8.1, 8.2)', () => {
    render(
      <BrowserRouter>
        <Footer />
      </BrowserRouter>
    )
    expect(screen.getByText('서비스이용약관')).toBeInTheDocument()
    expect(screen.getByText('개인정보처리방침')).toBeInTheDocument()
  })
  
  it('has correct links (7.2)', () => {
    render(
      <BrowserRouter>
        <Footer />
      </BrowserRouter>
    )
    const termsLink = screen.getByText('서비스이용약관')
    const privacyLink = screen.getByText('개인정보처리방침')
    
    expect(termsLink.closest('a')).toHaveAttribute('href', '/terms-of-service')
    expect(privacyLink.closest('a')).toHaveAttribute('href', '/privacy-policy')
  })
})

