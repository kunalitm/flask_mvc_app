import { useState, useEffect } from 'react'
import { userService, roleService } from '../../services/api'
import UserModal from './UserModal'

function Users() {
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [pagination, setPagination] = useState({
    page: 1,
    perPage: 10,
    total: 0,
  })

  useEffect(() => {
    loadUsers()
    loadRoles()
  }, [pagination.page])

  const loadUsers = async () => {
    setIsLoading(true)
    setError('')
    try {
      const data = await userService.getAll(pagination.page, pagination.perPage)
      setUsers(data.users || [])
      setPagination(prev => ({ ...prev, total: data.total || 0 }))
    } catch (err) {
      setError('Failed to load users: ' + (err.response?.data?.error || err.message))
    } finally {
      setIsLoading(false)
    }
  }

  const loadRoles = async () => {
    try {
      const data = await roleService.getAll()
      // API returns { roles: [...] }, extract the array
      setRoles(data.roles || [])
    } catch (err) {
      console.error('Failed to load roles:', err)
    }
  }

  const handleCreateUser = () => {
    setSelectedUser(null)
    setShowModal(true)
  }

  const handleEditUser = (user) => {
    setSelectedUser(user)
    setShowModal(true)
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return
    }

    try {
      await userService.delete(userId)
      setSuccess('User deleted successfully')
      loadUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to delete user: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleSaveUser = async (userData) => {
    try {
      if (selectedUser) {
        await userService.update(selectedUser.id, userData)
        setSuccess('User updated successfully')
      } else {
        await userService.create(userData)
        setSuccess('User created successfully')
      }
      setShowModal(false)
      loadUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      throw err
    }
  }

  const handleAssignRole = async (userId, roleId) => {
    try {
      await userService.assignRole(userId, roleId)
      setSuccess('Role assigned successfully')
      loadUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to assign role: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleRemoveRole = async (userId, roleId) => {
    if (!window.confirm('Are you sure you want to remove this role?')) {
      return
    }

    try {
      await userService.removeRole(userId, roleId)
      setSuccess('Role removed successfully')
      loadUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to remove role: ' + (err.response?.data?.error || err.message))
    }
  }

  const totalPages = Math.ceil(pagination.total / pagination.perPage)

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">User Management</h1>
        <button
          onClick={handleCreateUser}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Create User
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
        <div className="text-center py-8">Loading users...</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Username
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Roles
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{user.username}</div>
                      {user.first_name && (
                        <div className="text-sm text-gray-500">
                          {user.first_name} {user.last_name}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email || 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {user.roles?.map((role) => (
                          <span
                            key={role.id}
                            className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {role.name}
                            <button
                              onClick={() => handleRemoveRole(user.id, role.id)}
                              className="ml-1 text-blue-600 hover:text-blue-800"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                        <select
                          onChange={(e) => {
                            if (e.target.value) {
                              handleAssignRole(user.id, e.target.value)
                              e.target.value = ''
                            }
                          }}
                          className="text-xs border border-gray-300 rounded px-2 py-1"
                        >
                          <option value="">+ Add Role</option>
                          {roles
                            .filter(r => !user.roles?.find(ur => ur.id === r.id))
                            .map((role) => (
                              <option key={role.id} value={role.id}>
                                {role.name}
                              </option>
                            ))}
                        </select>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleEditUser(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-4">
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
                className="px-4 py-2 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {pagination.page} of {totalPages}
              </span>
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page === totalPages}
                className="px-4 py-2 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {showModal && (
        <UserModal
          user={selectedUser}
          onClose={() => setShowModal(false)}
          onSave={handleSaveUser}
        />
      )}
    </div>
  )
}

export default Users
