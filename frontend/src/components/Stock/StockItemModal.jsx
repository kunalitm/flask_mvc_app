import { useState, useEffect } from 'react'

function StockItemModal({ item, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sku: '',
    quantity: 0,
    price: 0,
    min_quantity: 10,
  })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (item) {
      setFormData({
        name: item.name || '',
        description: item.description || '',
        sku: item.sku || '',
        quantity: item.quantity || 0,
        price: item.price || 0,
        min_quantity: item.min_quantity || 10,
      })
    }
  }, [item])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      // Convert numeric fields
      const dataToSend = {
        ...formData,
        quantity: parseInt(formData.quantity, 10),
        price: parseFloat(formData.price),
        min_quantity: parseInt(formData.min_quantity, 10),
      }
      await onSave(dataToSend)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save item')
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">
            {item ? 'Edit Item' : 'Add Item'}
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
              Item Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              SKU
            </label>
            <input
              type="text"
              name="sku"
              value={formData.sku}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity *
              </label>
              <input
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                required
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Quantity
              </label>
              <input
                type="number"
                name="min_quantity"
                value={formData.min_quantity}
                onChange={handleChange}
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                required
                min="0"
                step="0.01"
                className="w-full pl-7 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
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

export default StockItemModal
