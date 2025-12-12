import React from 'react'
import './PrivacyPolicy.css'

function PrivacyPolicy() {
  return (
    <div className="privacy-page">
      <div className="container">
        <div className="privacy-header">
          <h1>개인정보 처리방침</h1>
          <div className="privacy-date">2024. 11. 05.</div>
        </div>

        <div className="privacy-content">
          <section className="privacy-section">
            <h2>제1조 개인정보의 처리 목적</h2>
            <p>이그나이트 주식회사(이하 "회사")는 다음의 목적을 위하여 개인정보를 처리합니다. 처리하고 있는 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며, 이용 목적이 변경되는 경우에는 개인정보 보호법 제18조에 따라 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.</p>
            <ol>
              <li><strong>서비스 제공</strong>
                <ul>
                  <li>물품 보관 서비스 제공, 물품 수거 및 배송, 보관료 결제 및 환불 처리</li>
                  <li>회원 가입 및 관리, 본인 확인, 서비스 이용에 따른 본인 확인</li>
                </ul>
              </li>
              <li><strong>마케팅 및 광고 활용</strong>
                <ul>
                  <li>신규 서비스 개발 및 맞춤 서비스 제공, 이벤트 및 광고성 정보 제공 및 참여기회 제공</li>
                </ul>
              </li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제2조 개인정보의 처리 및 보유기간</h2>
            <ol>
              <li>회사는 법령에 따른 개인정보 보유·이용기간 또는 정보주체로부터 개인정보를 수집 시에 동의받은 개인정보 보유·이용기간 내에서 개인정보를 처리·보유합니다.</li>
              <li>각각의 개인정보 처리 및 보유 기간은 다음과 같습니다.
                <ul>
                  <li>회원 가입 및 관리: 회원 탈퇴 시까지 (단, 관계 법령 위반에 따른 수사·조사 등이 진행중인 경우에는 해당 수사·조사 종료 시까지)</li>
                  <li>서비스 제공: 서비스 이용 계약 종료 시까지</li>
                  <li>계약 또는 청약철회 등에 관한 기록: 5년</li>
                  <li>대금결제 및 재화 등의 공급에 관한 기록: 5년</li>
                  <li>소비자의 불만 또는 분쟁처리에 관한 기록: 3년</li>
                </ul>
              </li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제3조 개인정보의 제3자 제공</h2>
            <p>회사는 정보주체의 개인정보를 제1조(개인정보의 처리 목적)에서 명시한 범위 내에서만 처리하며, 정보주체의 동의, 법률의 특별한 규정 등 개인정보 보호법 제17조 및 제18조에 해당하는 경우에만 개인정보를 제3자에게 제공합니다.</p>
          </section>

          <section className="privacy-section">
            <h2>제4조 개인정보처리 위탁</h2>
            <p>회사는 원활한 개인정보 업무처리를 위하여 다음과 같이 개인정보 처리업무를 위탁하고 있습니다.</p>
            <ol>
              <li>물품 배송 서비스: 택배사 (배송 완료 시까지)</li>
              <li>결제 서비스: 결제 대행사 (결제 완료 시까지)</li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제5조 정보주체의 권리·의무 및 행사방법</h2>
            <ol>
              <li>정보주체는 회사에 대해 언제든지 다음 각 호의 개인정보 보호 관련 권리를 행사할 수 있습니다.
                <ul>
                  <li>개인정보 처리정지 요구권</li>
                  <li>개인정보 열람요구권</li>
                  <li>개인정보 정정·삭제요구권</li>
                  <li>개인정보 처리정지 요구권</li>
                </ul>
              </li>
              <li>제1항에 따른 권리 행사는 회사에 대해 서면, 전자우편, 모사전송(FAX) 등을 통하여 하실 수 있으며 회사는 이에 대해 지체 없이 조치하겠습니다.</li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제6조 처리하는 개인정보의 항목</h2>
            <p>회사는 다음의 개인정보 항목을 처리하고 있습니다.</p>
            <ol>
              <li><strong>회원 가입 및 관리</strong>
                <ul>
                  <li>필수항목: 이름, 이메일 주소, 전화번호, 주소</li>
                  <li>선택항목: 생년월일, 성별</li>
                </ul>
              </li>
              <li><strong>서비스 이용 과정에서 자동 수집되는 정보</strong>
                <ul>
                  <li>IP주소, 쿠키, MAC주소, 서비스 이용 기록, 방문 기록, 불량 이용 기록 등</li>
                </ul>
              </li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제7조 개인정보의 파기</h2>
            <ol>
              <li>회사는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는 지체없이 해당 개인정보를 파기합니다.</li>
              <li>개인정보 파기의 절차 및 방법은 다음과 같습니다.
                <ul>
                  <li>파기절차: 회사는 파기 사유가 발생한 개인정보를 선정하고, 회사의 개인정보 보호책임자의 승인을 받아 개인정보를 파기합니다.</li>
                  <li>파기방법: 회사는 전자적 파일 형태로 기록·저장된 개인정보는 기록을 재생할 수 없도록 파기하며, 종이 문서에 기록·저장된 개인정보는 분쇄기로 분쇄하거나 소각하여 파기합니다.</li>
                </ul>
              </li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제8조 개인정보 보호책임자</h2>
            <p>회사는 개인정보 처리에 관한 업무를 총괄해서 책임지고, 개인정보 처리와 관련한 정보주체의 불만처리 및 피해구제 등을 위하여 아래와 같이 개인정보 보호책임자를 지정하고 있습니다.</p>
            <div className="privacy-contact">
              <p><strong>개인정보 보호책임자</strong></p>
              <ul>
                <li>성명: 조윤식</li>
                <li>직책: 대표이사</li>
                <li>연락처: support@mg-wrap.com</li>
              </ul>
            </div>
          </section>

          <section className="privacy-section">
            <h2>제9조 개인정보의 안전성 확보 조치</h2>
            <p>회사는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다.</p>
            <ol>
              <li>관리적 조치: 내부관리계획 수립·시행, 정기적 직원 교육 등</li>
              <li>기술적 조치: 개인정보처리시스템 등의 접근권한 관리, 접근통제시스템 설치, 고유식별정보 등의 암호화, 보안프로그램 설치</li>
              <li>물리적 조치: 전산실, 자료보관실 등의 접근통제</li>
            </ol>
          </section>

          <section className="privacy-section">
            <h2>제10조 개인정보 처리방침 변경</h2>
            <p>이 개인정보 처리방침은 2024년 11월 5일부터 적용되며, 법령 및 방침에 따른 변경내용의 추가, 삭제 및 정정이 있는 경우에는 변경사항의 시행 7일 전부터 공지사항을 통하여 고지할 것입니다.</p>
          </section>

          <div className="privacy-enforcement">
            <p><strong>(시행일)</strong> 이 개인정보 처리방침은 2024년 11월 5일부터 시행합니다.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PrivacyPolicy

