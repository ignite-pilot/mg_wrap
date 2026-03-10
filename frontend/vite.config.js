import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // 개발 서버는 사용하지 않음 (Flask가 모든 것을 서빙)
  // 빌드만 수행하여 frontend/dist에 결과물 생성
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // 프로덕션 빌드 최적화
    minify: 'terser',
    sourcemap: false
  },
  // 개발 시에도 Flask 서버를 사용하므로 프록시 불필요
  // 단, 테스트를 위해 개발 서버 설정 유지 (선택사항)
  server: {
    port: 8400,
    // 단일 서비스이므로 프록시 제거
    // Flask가 모든 요청을 처리
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: true,
  }
})

