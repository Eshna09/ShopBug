import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { productsApi } from '../services/api'
import ProductCard from '../components/ProductCard'

export default function Home() {
  const [featured, setFeatured] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    productsApi
      .list()
      .then((data) => {
        // Show up to 4 featured products
        setFeatured((data || []).slice(0, 4))
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchTerm.trim()) {
      navigate(`/products?q=${encodeURIComponent(searchTerm.trim())}`)
    } else {
      navigate('/products')
    }
  }

  return (
    <div>
      {/* Hero section */}
      <section className="bg-gradient-to-br from-brand-50 via-white to-brand-50">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              Welcome to <span className="text-brand-600">ShopBug</span> 🐛
            </h1>
            <p className="mt-4 text-lg text-gray-600">
              Your one-stop online shop for electronics, books, clothing, and more.
              Browse our catalog, add items to your cart, and check out in minutes.
            </p>

            {/* Search bar */}
            <form onSubmit={handleSearch} className="mx-auto mt-8 flex max-w-md gap-2">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search for products…"
                className="input"
              />
              <button type="submit" className="btn-primary shrink-0">
                Search
              </button>
            </form>

            <div className="mt-6">
              <Link to="/products" className="btn-secondary">
                Browse all products →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured products */}
      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Featured Products</h2>
          <Link to="/products" className="text-sm font-semibold text-brand-600 hover:text-brand-700">
            View all →
          </Link>
        </div>

        {loading && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="card h-72 animate-pulse bg-gray-100" />
            ))}
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-50 p-4 text-red-700">
            Failed to load products: {error}
          </div>
        )}

        {!loading && !error && featured.length === 0 && (
          <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
            <p className="text-gray-500">No products available yet. Check back soon!</p>
          </div>
        )}

        {!loading && !error && featured.length > 0 && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {featured.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
