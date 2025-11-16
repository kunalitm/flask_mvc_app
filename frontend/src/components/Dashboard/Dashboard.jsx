import { useState, useEffect } from 'react'
import { authService, userService, roleService, pluginService, stockService } from '../../services/api'
import { Link } from 'react-router-dom'

function Dashboard() {
  const [currentUser, setCurrentUser] = useState(null)
  const [stats, setStats] = useState({
    users: 0,
    roles: 0,
    plugins: 0,
    enabledPlugins: 0,
    stockItems: 0,
  })
  const [stockStats, setStockStats] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setIsLoading(true)
    try {
      const [user, usersData, rolesData, pluginsData, enabledPlugins] = await Promise.all([
        authService.getCurrentUser(),
        userService.getAll(1, 1),
        roleService.getAll(),
        pluginService.getAll(),
        pluginService.getEnabled(),
      ])

      setCurrentUser(user)
      setStats({
        users: usersData.total || 0,
        roles: rolesData.roles?.length || 0,
        plugins: pluginsData.plugins?.length || 0,
        enabledPlugins: enabledPlugins.plugins?.length || 0,
        stockItems: 0,
      })

      // Try to load stock stats if plugin is enabled
      try {
        const stockData = await stockService.getStats()
        setStockStats(stockData)
        setStats(prev => ({ ...prev, stockItems: stockData.total_items || 0 }))
      } catch (err) {
        // Stock plugin might not be enabled
        console.log('Stock plugin not available')
      }
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl text-gray-600">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Welcome back, {currentUser?.username || 'User'}!
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Link to="/users" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Users</p>
              <p className="text-3xl font-bold text-blue-600">{stats.users}</p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </Link>

        <Link to="/roles" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Roles</p>
              <p className="text-3xl font-bold text-green-600">{stats.roles}</p>
            </div>
            <div className="text-4xl">🔐</div>
          </div>
        </Link>

        <Link to="/plugins" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Active Plugins</p>
              <p className="text-3xl font-bold text-purple-600">
                {stats.enabledPlugins}/{stats.plugins}
              </p>
            </div>
            <div className="text-4xl">🔌</div>
          </div>
        </Link>

        <Link to="/inventory" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Stock Items</p>
              <p className="text-3xl font-bold text-orange-600">{stats.stockItems}</p>
            </div>
            <div className="text-4xl">📦</div>
          </div>
        </Link>
      </div>

      {/* Stock Stats (if available) */}
      {stockStats && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Inventory Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-gray-500 text-sm">Total Quantity</p>
              <p className="text-2xl font-bold text-gray-800">{stockStats.total_quantity || 0}</p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <p className="text-gray-500 text-sm">Total Value</p>
              <p className="text-2xl font-bold text-gray-800">
                ${(stockStats.total_value || 0).toFixed(2)}
              </p>
            </div>
            <div className="border-l-4 border-red-500 pl-4">
              <p className="text-gray-500 text-sm">Low Stock Items</p>
              <p className="text-2xl font-bold text-gray-800">{stockStats.low_stock_count || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* User Info Card */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Your Profile</h2>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-600">Username:</span>
            <span className="font-medium">{currentUser?.username}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Email:</span>
            <span className="font-medium">{currentUser?.email || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Roles:</span>
            <span className="font-medium">
              {currentUser?.roles?.map(r => r.name).join(', ') || 'None'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Status:</span>
            <span className={`font-medium ${currentUser?.is_active ? 'text-green-600' : 'text-red-600'}`}>
              {currentUser?.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
