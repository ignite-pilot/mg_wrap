import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import Login from './pages/Login'
import OAuth2Callback from './pages/OAuth2Callback'
import StorageApplication from './pages/StorageApplication'
import Assets from './pages/Assets'
import Retrieval from './pages/Retrieval'
import Disposal from './pages/Disposal'
import TermsOfService from './pages/TermsOfService'
import PrivacyPolicy from './pages/PrivacyPolicy'
import { AuthProvider, useAuth } from './context/AuthContext'
import './App.css'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="loading">로딩 중...</div>
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

function AppRoutes() {
  const { user } = useAuth()
  
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/oauth2/callback" element={<OAuth2Callback />} />
      <Route
        path="/storage"
        element={
          <ProtectedRoute>
            <StorageApplication />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assets"
        element={
          <ProtectedRoute>
            <Assets />
          </ProtectedRoute>
        }
      />
      <Route
        path="/retrieval"
        element={
          <ProtectedRoute>
            <Retrieval />
          </ProtectedRoute>
        }
      />
      <Route
        path="/disposal"
        element={
          <ProtectedRoute>
            <Disposal />
          </ProtectedRoute>
        }
      />
      <Route path="/terms-of-service" element={<TermsOfService />} />
      <Route path="/privacy-policy" element={<PrivacyPolicy />} />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <div className="App">
          <Navbar />
          <AppRoutes />
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

