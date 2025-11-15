import { useState, useEffect } from 'react'
import { roleService } from '../../services/api'
import RoleModal from './RoleModal'

function Roles() {
  const [roles, setRoles] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [selectedRole, setSelectedRole] = useState(null)

  useEffect(() => {
    loadRoles()
  }, [])

  const loadRoles = async () => {
    setIsLoading(true)
    setError('')
    try {
      const data = await roleService.getAll()
      setRoles(data)
    } catch (err) {
      setError('Failed to load roles: ' + (err.response?.data?.error || err.message))
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateRole = () => {
    setSelectedRole(null)
    setShowModal(true)
  }

  const handleEditRole = (role) => {
    setSelectedRole(role)
    setShowModal(true)
  }

  const handleDeleteRole = async (roleId) => {
    if (!window.confirm('Are you sure you want to delete this role?')) {
      return
    }

    try {
      await roleService.delete(roleId)
      setSuccess('Role deleted successfully')
      loadRoles()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to delete role: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleSaveRole = async (roleData) => {
    try {
      if (selectedRole) {
        await roleService.update(selectedRole.id, roleData)
        setSuccess('Role updated successfully')
      } else {
        await roleService.create(roleData)
        setSuccess('Role created successfully')
      }
      setShowModal(false)
      loadRoles()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      throw err
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Role Management</h1>
        <button
          onClick={handleCreateRole}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Create Role
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
        <div className="text-center py-8">Loading roles...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roles.map((role) => (
            <div key={role.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-800 mb-1">{role.name}</h3>
                    {role.is_system && (
                      <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-gray-100 text-gray-800">
                        System Role
                      </span>
                    )}
                  </div>
                  <div className="text-3xl">🔐</div>
                </div>

                <p className="text-gray-600 text-sm mb-4">
                  {role.description || 'No description'}
                </p>

                {role.permissions && Object.keys(role.permissions).length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Permissions:</h4>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(role.permissions).map(([key, value]) => (
                        <span
                          key={key}
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                            value
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {key}: {value ? '✓' : '✗'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-end space-x-2 pt-4 border-t">
                  <button
                    onClick={() => handleEditRole(role)}
                    className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                  >
                    Edit
                  </button>
                  {!role.is_system && (
                    <button
                      onClick={() => handleDeleteRole(role.id)}
                      className="text-red-600 hover:text-red-800 font-medium text-sm"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <RoleModal
          role={selectedRole}
          onClose={() => setShowModal(false)}
          onSave={handleSaveRole}
        />
      )}
    </div>
  )
}

export default Roles
