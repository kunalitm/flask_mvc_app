import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './components/Auth/Login'
import Layout from './components/Layout/Layout'
import Dashboard from './components/Dashboard/Dashboard'
import Users from './components/Users/Users'
import Roles from './components/Roles/Roles'
import Plugins from './components/Plugins/Plugins'
import StockInventory from './components/Stock/StockInventory'
import { authService } from './services/api'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = authService.getToken()
    if (token) {
      setIsAuthenticated(true)
    }
    setIsLoading(false)
  }, [])

  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    authService.logout()
    setIsAuthenticated(false)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout onLogout={handleLogout}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/users" element={<Users />} />
                  <Route path="/roles" element={<Roles />} />
                  <Route path="/plugins" element={<Plugins />} />
                  <Route path="/inventory" element={<StockInventory />} />
                </Routes>
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </Router>
  )
}

export default App
