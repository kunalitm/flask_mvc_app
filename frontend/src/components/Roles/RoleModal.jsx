import { useState, useEffect } from 'react'

function RoleModal({ role, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: {},
  })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Common permission keys
  const commonPermissions = [
    'can_create_users',
    'can_edit_users',
    'can_delete_users',
    'can_manage_roles',
    'can_manage_plugins',
    'can_view_reports',
  ]

  useEffect(() => {
    if (role) {
      setFormData({
        name: role.name || '',
        description: role.description || '',
        permissions: role.permissions || {},
      })
    } else {
      // Initialize with default permissions set to false
      const defaultPermissions = {}
      commonPermissions.forEach(perm => {
        defaultPermissions[perm] = false
      })
      setFormData(prev => ({ ...prev, permissions: defaultPermissions }))
    }
  }, [role])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await onSave(formData)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save role')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  const handlePermissionChange = (permissionKey, value) => {
    setFormData(prev => ({
      ...prev,
      permissions: {
        ...prev.permissions,
        [permissionKey]: value,
      },
    }))
  }

  const addCustomPermission = () => {
    const key = prompt('Enter permission key (e.g., can_do_something):')
    if (key && key.trim()) {
      handlePermissionChange(key.trim(), false)
    }
  }

  const removePermission = (key) => {
    setFormData(prev => {
      const newPermissions = { ...prev.permissions }
      delete newPermissions[key]
      return { ...prev, permissions: newPermissions }
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">
            {role ? 'Edit Role' : 'Create Role'}
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

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              disabled={role?.is_system}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Permissions
              </label>
              <button
                type="button"
                onClick={addCustomPermission}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                + Add Custom
              </button>
            </div>

            <div className="border border-gray-300 rounded-lg p-4 space-y-2 max-h-64 overflow-y-auto">
              {Object.entries(formData.permissions).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <label className="flex items-center flex-1">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => handlePermissionChange(key, e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{key}</span>
                  </label>
                  {!commonPermissions.includes(key) && (
                    <button
                      type="button"
                      onClick={() => removePermission(key)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}

              {Object.keys(formData.permissions).length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  No permissions defined. Click "Add Custom" to add permissions.
                </p>
              )}
            </div>
          </div>

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
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RoleModal
