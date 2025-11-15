import { useState, useEffect } from 'react'
import { stockService } from '../../services/api'
import StockItemModal from './StockItemModal'

function StockInventory() {
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    setError('')
    try {
      const [itemsData, statsData] = await Promise.all([
        stockService.getAll(),
        stockService.getStats(),
      ])
      setItems(itemsData)
      setStats(statsData)
    } catch (err) {
      setError('Failed to load inventory: ' + (err.response?.data?.error || err.message))
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateItem = () => {
    setSelectedItem(null)
    setShowModal(true)
  }

  const handleEditItem = (item) => {
    setSelectedItem(item)
    setShowModal(true)
  }

  const handleDeleteItem = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return
    }

    try {
      await stockService.delete(itemId)
      setSuccess('Item deleted successfully')
      loadData()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to delete item: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleSaveItem = async (itemData) => {
    try {
      if (selectedItem) {
        await stockService.update(selectedItem.id, itemData)
        setSuccess('Item updated successfully')
      } else {
        await stockService.create(itemData)
        setSuccess('Item created successfully')
      }
      setShowModal(false)
      loadData()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      throw err
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Stock Inventory</h1>
        <button
          onClick={handleCreateItem}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Add Item
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

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-500 text-sm mb-1">Total Items</p>
            <p className="text-3xl font-bold text-blue-600">{stats.total_items}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-500 text-sm mb-1">Total Quantity</p>
            <p className="text-3xl font-bold text-green-600">{stats.total_quantity}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-500 text-sm mb-1">Total Value</p>
            <p className="text-3xl font-bold text-purple-600">${stats.total_value.toFixed(2)}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-500 text-sm mb-1">Low Stock Items</p>
            <p className="text-3xl font-bold text-red-600">{stats.low_stock_count}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-8">Loading inventory...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
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
              {items.map((item) => {
                const totalValue = item.quantity * item.price
                const isLowStock = item.quantity < (item.min_quantity || 10)

                return (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{item.name}</div>
                      {item.description && (
                        <div className="text-sm text-gray-500">{item.description}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.sku || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`text-sm font-medium ${
                          isLowStock ? 'text-red-600' : 'text-gray-900'
                        }`}
                      >
                        {item.quantity}
                      </span>
                      {item.min_quantity && (
                        <span className="text-xs text-gray-500 ml-1">
                          (min: {item.min_quantity})
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${item.price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${totalValue.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          isLowStock
                            ? 'bg-red-100 text-red-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {isLowStock ? 'Low Stock' : 'In Stock'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleEditItem(item)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteItem(item.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                )
              })}

              {items.length === 0 && (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                    No items in inventory. Click "Add Item" to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <StockItemModal
          item={selectedItem}
          onClose={() => setShowModal(false)}
          onSave={handleSaveItem}
        />
      )}
    </div>
  )
}

export default StockInventory
