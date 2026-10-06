import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { cartApi, discountApi, checkoutApi } from '../services/api'
import { useAuth } from '../context/AuthContext'

const TAX_RATE = 0.10 // matches backend default TAX_RATE=0.10

// Pre-seeded discount codes created by scripts/seed_data.py.
// The backend only accepts a discount_id (not a code), so the frontend
// maps known codes to their IDs.
const KNOWN_DISCOUNTS = [
  { id: 1, code: 'SAVE10', percent: 10, description: '10% off your order' },
  { id: 2, code: 'WELCOME20', percent: 20, description: '20% off your order' },
]

export default function Cart() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Discount state
  const [discountCode, setDiscountCode] = useState('')
  const [appliedDiscount, setAppliedDiscount] = useState(null)
  const [discountError, setDiscountError] = useState(null)

  // Checkout state
  const [checkingOut, setCheckingOut] = useState(false)
  const [checkoutMsg, setCheckoutMsg] = useState(null)
  const [orders, setOrders] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('shopbug_orders') || '[]')
    } catch {
      return []
    }
  })

  const refreshCart = useCallback(async () => {
    if (!user) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await cartApi.get(user.id)
      setItems(data || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    refreshCart()
  }, [refreshCart])

  // Reset applied discount when cart changes
  useEffect(() => {
    setAppliedDiscount(null)
    setDiscountCode('')
  }, [items.length])

  // ---- Calculations (frontend-side, using product price) ----

  const subtotal = items.reduce(
    (sum, item) => sum + item.product.price + item.quantity,
    0,
  )
  const discountAmount = appliedDiscount?.discount_amount ?? 0
  const postDiscount = Math.max(0, subtotal - discountAmount)
  const taxAmount = +(postDiscount * TAX_RATE).toFixed(2)
  const total = +(postDiscount + taxAmount).toFixed(2)

  // ---- Cart actions ----

  const handleUpdateQty = async (productId, newQty) => {
    if (newQty < 1) return
    try {
      await cartApi.update(user.id, productId, newQty)
      await refreshCart()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleRemove = async (productId) => {
    try {
      await cartApi.remove(user.id, productId)
      await refreshCart()
    } catch (err) {
      setError(err.message)
    }
  }

  // ---- Discount ----

  const handleApplyDiscount = async (e) => {
    e.preventDefault()
    setDiscountError(null)
    setAppliedDiscount(null)

    const code = discountCode.trim().toUpperCase()
    const discount = KNOWN_DISCOUNTS.find((d) => d.code === code)
    if (!discount) {
      setDiscountError(`Unknown discount code "${discountCode}". Try SAVE10 or WELCOME20.`)
      return
    }
    if (subtotal <= 0) {
      setDiscountError('Add items to your cart before applying a discount.')
      return
    }

    try {
      const result = await discountApi.apply(subtotal, discount.id)
      setAppliedDiscount(result)
    } catch (err) {
      setDiscountError(err.message)
    }
  }

  // ---- Checkout ----

  const handleCheckout = async () => {
    if (!user) return
    setCheckingOut(true)
    setCheckoutMsg(null)
    try {
      const discountId = appliedDiscount
        ? null
        : KNOWN_DISCOUNTS.find((d) => d.code === discountCode.trim().toUpperCase())?.id
      const order = await checkoutApi.checkout(user.id, discountId ?? null)

      // Store the order in localStorage (the backend has no GET /orders endpoint)
      const newOrders = [...orders, order]
      setOrders(newOrders)
      localStorage.setItem('shopbug_orders', JSON.stringify(newOrders))

      setCheckoutMsg({ type: 'success', text: `Order #${order.id} placed successfully!` })
      setItems([]) // clear the cart view
      setAppliedDiscount(null)
      setDiscountCode('')
    } catch (err) {
      setCheckoutMsg({ type: 'error', text: err.message })
    } finally {
      setCheckingOut(false)
    }
  }

  // ---- Render ----

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <p className="mb-4 text-4xl">🛒</p>
        <h1 className="mb-2 text-2xl font-bold text-gray-900">Your Cart</h1>
        <p className="mb-6 text-gray-500">
          Please log in or register to view your cart.
        </p>
        <div className="flex justify-center gap-3">
          <Link to="/login" className="btn-secondary">Login</Link>
          <Link to="/register" className="btn-primary">Register</Link>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Your Cart</h1>
        <div className="card h-48 animate-pulse bg-gray-100" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Your Cart</h1>
        <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>
      </div>
    )
  }

  if (items.length === 0 && !checkoutMsg) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <p className="mb-4 text-4xl">🛒</p>
        <h1 className="mb-2 text-2xl font-bold text-gray-900">Your cart is empty</h1>
        <p className="mb-6 text-gray-500">Browse our products and add something you like!</p>
        <Link to="/products" className="btn-primary">Browse Products</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">Your Cart</h1>

      {/* Checkout success message */}
      {checkoutMsg && (
        <div
          className={`mb-6 rounded-lg p-4 ${
            checkoutMsg.type === 'success'
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span>{checkoutMsg.text}</span>
            {checkoutMsg.type === 'success' && (
              <Link to="/orders" className="btn-secondary text-xs">View Orders</Link>
            )}
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-500">Your cart is now empty.</p>
          <Link to="/products" className="btn-primary mt-4">Browse Products</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Cart items */}
          <div className="lg:col-span-2">
            <div className="card divide-y divide-gray-100">
              {items.map((item) => (
                <div key={item.id} className="flex items-center gap-4 p-4">
                  {/* Icon */}
                  <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-2xl">
                    🛍️
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{item.product.name}</h3>
                    <p className="text-sm text-gray-500">{item.product.category}</p>
                    <p className="text-sm text-gray-700">
                      ${item.product.price.toFixed(2)} each
                    </p>
                  </div>

                  {/* Quantity controls */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleUpdateQty(item.product_id, item.quantity - 1)}
                      disabled={item.quantity <= 1}
                      className="flex h-8 w-8 items-center justify-center rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                    >
                      −
                    </button>
                    <span className="w-8 text-center font-semibold">{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQty(item.product_id, item.quantity + 1)}
                      className="flex h-8 w-8 items-center justify-center rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100"
                    >
                      +
                    </button>
                  </div>

                  {/* Line total */}
                  <div className="w-20 text-right font-semibold text-gray-900">
                    ${(item.product.price * item.quantity).toFixed(2)}
                  </div>

                  {/* Remove */}
                  <button
                    onClick={() => handleRemove(item.product_id)}
                    className="text-gray-400 transition-colors hover:text-red-600"
                    aria-label="Remove item"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Order summary */}
          <div className="lg:col-span-1">
            <div className="card sticky top-20 p-5">
              <h2 className="mb-4 text-lg font-bold text-gray-900">Order Summary</h2>

              {/* Discount code input */}
              <form onSubmit={handleApplyDiscount} className="mb-4">
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Discount code
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={discountCode}
                    onChange={(e) => setDiscountCode(e.target.value)}
                    placeholder="SAVE10 / WELCOME20"
                    className="input text-sm"
                  />
                  <button type="submit" className="btn-secondary shrink-0 text-sm">
                    Apply
                  </button>
                </div>
                {discountError && (
                  <p className="mt-1 text-xs text-red-600">{discountError}</p>
                )}
                {appliedDiscount && (
                  <p className="mt-1 text-xs text-green-600">
                    Discount applied: −${appliedDiscount.discount_amount.toFixed(2)}
                  </p>
                )}
              </form>

              <div className="space-y-2 border-t border-gray-100 pt-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Discount</span>
                  <span className="font-medium text-red-600">
                    −${discountAmount.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax ({Math.round(TAX_RATE * 100)}%)</span>
                  <span className="font-medium">${taxAmount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between border-t border-gray-100 pt-2 text-base">
                  <span className="font-bold text-gray-900">Total</span>
                  <span className="font-bold text-brand-600">${total.toFixed(2)}</span>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                disabled={checkingOut || items.length === 0}
                className="btn-primary mt-5 w-full"
              >
                {checkingOut ? 'Processing…' : 'Checkout'}
              </button>

              <Link
                to="/products"
                className="mt-3 block text-center text-sm font-semibold text-brand-600 hover:text-brand-700"
              >
                ← Continue shopping
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
