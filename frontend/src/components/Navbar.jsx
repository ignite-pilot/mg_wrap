import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import logoImage from '../assets/logo.png'
import './Navbar.css'

function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <nav className="navbar">
      <div className="container">
        <div className="navbar-content">
          <Link to="/" className="navbar-brand">
            <div className="navbar-logo">
              <img src={logoImage} alt="맡길랩 로고" className="logo-image" />
              <span className="logo-enterprise">엔터프라이즈</span>
            </div>
          </Link>
          <div className="navbar-menu">
            {user ? (
              <>
                <Link 
                  to="/storage" 
                  className={`navbar-link ${isActive('/storage') ? 'active' : ''}`}
                >
                  보관 신청
                </Link>
                <Link 
                  to="/assets" 
                  className={`navbar-link ${isActive('/assets') ? 'active' : ''}`}
                >
                  보관 자산
                </Link>
                <Link 
                  to="/retrieval" 
                  className={`navbar-link ${isActive('/retrieval') ? 'active' : ''}`}
                >
                  회수 현황
                </Link>
                <Link 
                  to="/disposal" 
                  className={`navbar-link ${isActive('/disposal') ? 'active' : ''}`}
                >
                  폐기 현황
                </Link>
                <span className="navbar-user">{user.name}님</span>
                <button onClick={handleLogout} className="navbar-logout-btn">
                  로그아웃
                </button>
              </>
            ) : (
              <Link to="/login" className="navbar-login-btn">로그인</Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

