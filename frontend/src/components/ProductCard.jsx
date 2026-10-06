import { useState } from 'react'
import { cartApi } from '../services/api'
import { useAuth } from '../context/AuthContext'

/**
 * Displays a single product as a card with name, price, category, stock,
 * and an "Add to Cart" button.  Shows loading and success/error states
 * for the add-to-cart action.
 */
export default function ProductCard({ product }) {
  const { user } = useAuth()
  const [adding, setAdding] = useState(false)
  const [msg, setMsg] = useState(null)

  const handleAdd = async () => {
    if (!user) {
      setMsg({ type: 'error', text: 'Please log in or register first.' })
      return
    }
    setAdding(true)
    setMsg(null)
    try {
      await cartApi.add(product.id, user.id, 1)
      setMsg({ type: 'success', text: 'Added to cart!' })
    } catch (err) {
      setMsg({ type: 'error', text: err.message })
    } finally {
      setAdding(false)
      setTimeout(() => setMsg(null), 3000)
    }
  }

  return (
    <div className="card flex flex-col overflow-hidden transition-shadow hover:shadow-md">
      {/* Placeholder image area */}
      <div className="flex h-36 items-center justify-center bg-gradient-to-br from-brand-50 to-brand-100">
        <span className="text-4xl">
          {product.category === 'Electronics'
            ? '💻'
            : product.category === 'Books'
              ? '📚'
              : product.category === 'Clothing'
                ? '👕'
                : product.category === 'Home'
                  ? '🏠'
                  : product.category === 'Sports'
                    ? '⚽'
                    : product.category === 'Toys'
                      ? '🎮'
                      : '🛍️'}
        </span>
      </div>

      <div className="flex flex-1 flex-col p-4">
        <div className="mb-1 flex items-start justify-between gap-2">
          <h3 className="font-semibold text-gray-900">{product.name}</h3>
          <span className="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
            {product.category}
          </span>
        </div>

        <p className="mb-3 text-sm text-gray-500">
          {product.stock > 0
            ? `In stock: ${product.stock}`
            : 'Out of stock'}
        </p>

        <div className="mt-auto">
          <div className="mb-3 text-lg font-bold text-brand-600">
            ${product.price.toFixed(2)}
          </div>

          {msg && (
            <div
              className={`mb-2 rounded-md px-2 py-1 text-xs ${
                msg.type === 'success'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              {msg.text}
            </div>
          )}

          <button
            onClick={handleAdd}
            disabled={adding || product.stock <= 0}
            className="btn-primary w-full"
          >
            {adding ? 'Adding…' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  )
}
