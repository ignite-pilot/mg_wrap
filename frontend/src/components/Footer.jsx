import React from 'react'
import { Link } from 'react-router-dom'
import './Footer.css'

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-info">
        <div className="footer-content">
          <div className="footer-left">
            <div className="footer-company">IGNITE</div>
            <div className="footer-details">
              <p>사업자 등록번호 : 324-81-02747</p>
              <p>통신판매업 신고번호: 제2024-성남분당B-1334호</p>
              <p>대표 : 조윤식</p>
              <p>소재지 : 경기도 성남시 분당구 황새울로258번길 41, 4층 (수내동)</p>
              <p>고객센터 : support@mg-wrap.com</p>
            </div>
            <div className="footer-copyright">
              © IGNITE Corp. All Rights Reserved.
            </div>
          </div>
          <div className="footer-right">
            <Link to="/terms-of-service" className="footer-link">서비스이용약관</Link>
            <span className="footer-separator">|</span>
            <Link to="/privacy-policy" className="footer-link">개인정보처리방침</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer

