import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const STORAGE_KEY = 'shopbug_orders'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
      setOrders(data)
    } catch {
      setOrders([])
    }
    setLoaded(true)
  }, [])

  const handleClear = () => {
    localStorage.removeItem(STORAGE_KEY)
    setOrders([])
  }

  // Parse the items_snapshot JSON string stored on each order
  function parseItems(order) {
    try {
      return JSON.parse(order.items_snapshot)
    } catch {
      return []
    }
  }

  if (!loaded) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Your Orders</h1>
        <div className="card h-48 animate-pulse bg-gray-100" />
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <p className="mb-4 text-4xl">📦</p>
        <h1 className="mb-2 text-2xl font-bold text-gray-900">No orders yet</h1>
        <p className="mb-6 text-gray-500">
          When you place an order, it will appear here.
        </p>
        <Link to="/products" className="btn-primary">Browse Products</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Your Orders</h1>
        <button onClick={handleClear} className="btn-secondary text-xs">
          Clear history
        </button>
      </div>

      <div className="space-y-4">
        {orders
          .slice()
          .reverse()
          .map((order) => {
            const items = parseItems(order)
            return (
              <div key={order.id} className="card p-5">
                <div className="mb-3 flex items-center justify-between border-b border-gray-100 pb-3">
                  <div>
                    <span className="text-sm text-gray-500">Order #</span>
                    <span className="ml-1 font-bold text-gray-900">{order.id}</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(order.created_at).toLocaleString()}
                  </span>
                </div>

                {/* Items */}
                <div className="mb-3 space-y-1">
                  {items.map((item, i) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-gray-700">
                        {item.name} × {item.quantity}
                      </span>
                      <span className="text-gray-500">
                        ${(item.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Summary */}
                <div className="space-y-1 border-t border-gray-100 pt-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subtotal</span>
                    <span>${(order.subtotal ?? 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Discount</span>
                    <span>−${(order.discount_amount ?? 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tax</span>
                    <span>${(order.tax_amount ?? 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between border-t border-gray-100 pt-1 font-bold">
                    <span>Total</span>
                    <span className="text-brand-600">
                      ${(order.total_amount ?? 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
      </div>
    </div>
  )
}
