import { useState, useEffect } from 'react'
import { pluginService } from '../../services/api'

function PluginConfigModal({ plugin, onClose, onSave }) {
  const [config, setConfig] = useState({})
  const [configJson, setConfigJson] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [useJsonEditor, setUseJsonEditor] = useState(false)

  useEffect(() => {
    loadConfig()
  }, [plugin])

  const loadConfig = async () => {
    setIsLoading(true)
    try {
      const data = await pluginService.getConfig(plugin.id)
      setConfig(data.config || {})
      setConfigJson(JSON.stringify(data.config || {}, null, 2))
    } catch (err) {
      console.error('Failed to load config:', err)
      setConfig({})
      setConfigJson('{}')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      let configToSave = config

      if (useJsonEditor) {
        try {
          configToSave = JSON.parse(configJson)
        } catch (err) {
          setError('Invalid JSON format')
          setIsSubmitting(false)
          return
        }
      }

      await onSave(configToSave)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save configuration')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleConfigChange = (key, value) => {
    const newConfig = { ...config, [key]: value }
    setConfig(newConfig)
    setConfigJson(JSON.stringify(newConfig, null, 2))
  }

  const handleJsonChange = (value) => {
    setConfigJson(value)
    try {
      const parsed = JSON.parse(value)
      setConfig(parsed)
      setError('')
    } catch (err) {
      // Don't update config if JSON is invalid
    }
  }

  const addConfigKey = () => {
    const key = prompt('Enter configuration key:')
    if (key && key.trim()) {
      handleConfigChange(key.trim(), '')
    }
  }

  const removeConfigKey = (key) => {
    const newConfig = { ...config }
    delete newConfig[key]
    setConfig(newConfig)
    setConfigJson(JSON.stringify(newConfig, null, 2))
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6">
          <div className="text-center py-8">Loading configuration...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">
            Configure {plugin.name}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Configure settings for this plugin
          </p>
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={useJsonEditor}
              onChange={(e) => setUseJsonEditor(e.target.checked)}
              className="mr-2"
            />
            JSON Editor
          </label>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {useJsonEditor ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Configuration (JSON)
              </label>
              <textarea
                value={configJson}
                onChange={(e) => handleJsonChange(e.target.value)}
                rows={15}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
          ) : (
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Configuration Settings
                </label>
                <button
                  type="button"
                  onClick={addConfigKey}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  + Add Setting
                </button>
              </div>

              <div className="border border-gray-300 rounded-lg p-4 space-y-3 max-h-96 overflow-y-auto">
                {Object.entries(config).map(([key, value]) => (
                  <div key={key} className="flex items-start gap-2">
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {key}
                      </label>
                      <input
                        type="text"
                        value={typeof value === 'object' ? JSON.stringify(value) : value}
                        onChange={(e) => {
                          let newValue = e.target.value
                          // Try to parse as JSON for object values
                          if (typeof value === 'object') {
                            try {
                              newValue = JSON.parse(e.target.value)
                            } catch {
                              newValue = e.target.value
                            }
                          }
                          handleConfigChange(key, newValue)
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeConfigKey(key)}
                      className="mt-7 text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}

                {Object.keys(config).length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No configuration settings. Click "Add Setting" to add configuration.
                  </p>
                )}
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PluginConfigModal
