import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import heroAnimation from '../assets/240912_hero-animation.mp4'
import InquiryBoard from '../components/InquiryBoard'
import './Home.css'

function Home() {
  const { user } = useAuth()

  return (
    <div className="home">
      <div className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <p className="hero-tagline">짐을 맡기는 가장 쉬운 방법</p>
              <h1>
                포장, 배송, 보관까지<br/>
                <span className="hero-highlight">맡길랩</span>이 다 해드려요
              </h1>
            </div>
            <div className="hero-image">
              <div className="hero-video-container">
                <video
                  className="hero-video"
                  autoPlay
                  loop
                  muted
                  playsInline
                >
                  <source src={heroAnimation} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <div className="features">
            <div className="feature-card">
              <h3>공간형 자산보관</h3>
              <p>필요한 평수에 맞춰 유연하게 보관 공간을 제공합니다.</p>
            </div>
            <div className="feature-card">
              <h3>BOX형 자산보관</h3>
              <p>60L 표준 BOX를 활용한 효율적인 자산 보관 서비스입니다.</p>
            </div>
            <div className="feature-card">
              <h3>실시간 자산 관리</h3>
              <p>보관 자산을 실시간으로 확인하고 관리할 수 있습니다.</p>
            </div>
            <div className="feature-card">
              <h3>회수 및 폐기 신청</h3>
              <p>간편한 회수 신청과 폐기 처리를 지원합니다.</p>
            </div>
          </div>
        </div>
      </div>

      {!user && (
        <div className="hero-cta-section">
          <div className="container">
            <Link to="/login" className="btn-start">
              시작하기
            </Link>
          </div>
        </div>
      )}

      {user && (
        <div className="quick-actions-section">
          <div className="container">
            <div className="quick-actions">
              <h2>빠른 메뉴</h2>
              <div className="action-buttons">
                <Link to="/storage" className="action-btn action-btn-primary">보관 신청</Link>
                <Link to="/assets" className="action-btn action-btn-primary">보관 자산 관리</Link>
                <Link to="/retrieval" className="action-btn action-btn-secondary">회수 현황</Link>
                <Link to="/disposal" className="action-btn action-btn-secondary">폐기 현황</Link>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="pricing-section">
        <div className="container">
          <h2 className="pricing-title">요금 정책</h2>
          <div className="pricing-grid">
            <div className="pricing-card">
              <div className="pricing-card-header">
                <h3>공간형 자산보관</h3>
                <p className="pricing-subtitle">5평 기준</p>
              </div>
              <div className="pricing-table">
                <div className="pricing-row">
                  <span className="pricing-period">1개월</span>
                  <span className="pricing-price">300,000원</span>
                </div>
                <div className="pricing-row">
                  <span className="pricing-period">3개월</span>
                  <span className="pricing-price">800,000원</span>
                </div>
                <div className="pricing-row">
                  <span className="pricing-period">6개월</span>
                  <span className="pricing-price">1,500,000원</span>
                </div>
              </div>
            </div>

            <div className="pricing-card">
              <div className="pricing-card-header">
                <h3>BOX형 자산보관</h3>
                <p className="pricing-subtitle">BOX 1개 (60L) 기준</p>
              </div>
              <div className="pricing-table">
                <div className="pricing-row">
                  <span className="pricing-period">1개월</span>
                  <span className="pricing-price">30,000원</span>
                </div>
                <div className="pricing-row">
                  <span className="pricing-period">3개월</span>
                  <span className="pricing-price">80,000원</span>
                </div>
                <div className="pricing-row">
                  <span className="pricing-period">6개월</span>
                  <span className="pricing-price">150,000원</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="inquiry-section">
        <div className="container">
          <InquiryBoard />
        </div>
      </div>
    </div>
  )
}

export default Home

