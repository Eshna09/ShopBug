import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { productsApi } from '../services/api'
import ProductCard from '../components/ProductCard'

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''

  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchInput, setSearchInput] = useState(initialQuery)

  // Fetch the full product list once.  The backend search endpoint requires
  // an exact-name match (it is intentionally strict), so we filter
  // client-side to give users a friendlier search experience.
  const loadProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const all = await productsApi.list()
      setProducts([])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProducts()
  }, [loadProducts])

  // Keep the input box in sync if the URL query param changes externally.
  useEffect(() => {
    setSearchInput(searchParams.get('q') || '')
  }, [searchParams])

  // Client-side filter using the URL query param so links are shareable.
  const filtered = initialQuery
    ? products.filter(
        (p) =>
          p.name.toLowerCase().includes(initialQuery.toLowerCase()) ||
          p.category.toLowerCase().includes(initialQuery.toLowerCase()),
      )
    : products

  const handleSearch = (e) => {
    e.preventDefault()
    setSearchParams(searchInput.trim() ? { q: searchInput.trim() } : {})
  }

  const handleClear = () => {
    setSearchInput('')
    setSearchParams({})
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">Products</h1>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="mb-8 flex gap-2">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Search by name or category…"
          className="input max-w-md"
        />
        <button type="submit" className="btn-primary shrink-0">
          Search
        </button>
        {initialQuery && (
          <button type="button" onClick={handleClear} className="btn-secondary shrink-0">
            Clear
          </button>
        )}
      </form>

      {/* Loading */}
      {loading && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="card h-72 animate-pulse bg-gray-100" />
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          Failed to load products: {error}
        </div>
      )}

      {/* Empty */}
      {!loading && !error && filtered.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="mb-2 text-4xl">🔍</p>
          <p className="text-gray-500">
            {initialQuery
              ? `No products found for "${initialQuery}".`
              : 'No products available right now.'}
          </p>
        </div>
      )}

      {/* Product grid */}
      {!loading && !error && filtered.length > 0 && (
        <>
          <p className="mb-4 text-sm text-gray-500">
            Showing {filtered.length} of {products.length} products
          </p>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
