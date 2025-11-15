import { useState, useEffect } from 'react'
import { pluginService } from '../../services/api'
import PluginConfigModal from './PluginConfigModal'

function Plugins() {
  const [plugins, setPlugins] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showConfigModal, setShowConfigModal] = useState(false)
  const [selectedPlugin, setSelectedPlugin] = useState(null)

  useEffect(() => {
    loadPlugins()
  }, [])

  const loadPlugins = async () => {
    setIsLoading(true)
    setError('')
    try {
      const data = await pluginService.getAll()
      setPlugins(data)
    } catch (err) {
      setError('Failed to load plugins: ' + (err.response?.data?.error || err.message))
    } finally {
      setIsLoading(false)
    }
  }

  const handleTogglePlugin = async (plugin) => {
    try {
      if (plugin.is_enabled) {
        await pluginService.disable(plugin.id)
        setSuccess(`Plugin "${plugin.name}" disabled successfully`)
      } else {
        await pluginService.enable(plugin.id)
        setSuccess(`Plugin "${plugin.name}" enabled successfully`)
      }
      loadPlugins()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to toggle plugin: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleReloadPlugin = async (plugin) => {
    try {
      await pluginService.reload(plugin.id)
      setSuccess(`Plugin "${plugin.name}" reloaded successfully`)
      loadPlugins()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to reload plugin: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleConfigurePlugin = (plugin) => {
    setSelectedPlugin(plugin)
    setShowConfigModal(true)
  }

  const handleSaveConfig = async (config) => {
    try {
      await pluginService.updateConfig(selectedPlugin.id, config)
      setSuccess(`Plugin "${selectedPlugin.name}" configured successfully`)
      setShowConfigModal(false)
      loadPlugins()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      throw err
    }
  }

  const handleDiscoverPlugins = async () => {
    try {
      const result = await pluginService.discover()
      setSuccess(`Discovery complete! Found ${result.discovered?.length || 0} new plugins`)
      loadPlugins()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to discover plugins: ' + (err.response?.data?.error || err.message))
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Plugin Management</h1>
        <button
          onClick={handleDiscoverPlugins}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          🔍 Discover Plugins
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-8">Loading plugins...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plugins.map((plugin) => (
            <div
              key={plugin.id}
              className={`bg-white rounded-lg shadow hover:shadow-lg transition-shadow border-l-4 ${
                plugin.is_enabled ? 'border-green-500' : 'border-gray-300'
              }`}
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-xl font-bold text-gray-800">{plugin.name}</h3>
                      {plugin.is_system && (
                        <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                          System
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">v{plugin.version}</p>
                  </div>
                  <div className="text-3xl">🔌</div>
                </div>

                <p className="text-gray-600 text-sm mb-2">
                  {plugin.description || 'No description'}
                </p>

                {plugin.author && (
                  <p className="text-gray-500 text-xs mb-4">
                    By: {plugin.author}
                  </p>
                )}

                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-700 font-medium">Status:</span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      plugin.is_enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {plugin.is_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>

                {plugin.last_enabled && (
                  <p className="text-xs text-gray-500 mb-4">
                    Last enabled: {new Date(plugin.last_enabled).toLocaleString()}
                  </p>
                )}

                <div className="flex flex-col gap-2 pt-4 border-t">
                  <button
                    onClick={() => handleTogglePlugin(plugin)}
                    className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                      plugin.is_enabled
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {plugin.is_enabled ? 'Disable' : 'Enable'}
                  </button>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleConfigurePlugin(plugin)}
                      className="flex-1 py-2 px-4 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 font-medium transition-colors"
                    >
                      Configure
                    </button>
                    {plugin.is_enabled && (
                      <button
                        onClick={() => handleReloadPlugin(plugin)}
                        className="flex-1 py-2 px-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
                      >
                        Reload
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {plugins.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              <p className="text-lg mb-2">No plugins found</p>
              <p className="text-sm">Click "Discover Plugins" to scan for available plugins</p>
            </div>
          )}
        </div>
      )}

      {showConfigModal && (
        <PluginConfigModal
          plugin={selectedPlugin}
          onClose={() => setShowConfigModal(false)}
          onSave={handleSaveConfig}
        />
      )}
    </div>
  )
}

export default Plugins
