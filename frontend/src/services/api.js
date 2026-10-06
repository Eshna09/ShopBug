/**
 * Centralized API service layer for ShopBug frontend.
 *
 * All HTTP calls to the FastAPI backend go through this module so that
 * components never call fetch/axios directly.  The backend URL is read
 * from the VITE_API_URL environment variable (set in frontend/.env).
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

/** Build a query string from a flat key/value object, skipping nulls. */
function qs(params = {}) {
  const entries = Object.entries(params).filter(([, v]) => v !== null && v !== undefined)
  return new URLSearchParams(entries).toString()
}

/**
 * Thin wrapper around fetch that:
 *  - prefixes the backend BASE_URL
 *  - sets JSON headers for requests with a body
 *  - parses the JSON response
 *  - throws an Error with a useful message on non-2xx responses
 */
async function request(method, path, { body, query } = {}) {
  const url = `${BASE_URL}${path}${query ? `?${qs(query)}` : ''}`
  const options = {
    method,
    headers: {},
  }
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }

  let res
  try {
    res = await fetch(url, options)
  } catch (err) {
    throw new Error(
      'Unable to reach the server. Make sure the backend is running at ' + BASE_URL,
    )
  }

  let data = null
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    data = await res.json()
  }

  if (!res.ok) {
    const detail =
      (data && (data.detail || data.message)) ||
      `Request failed with status ${res.status}`
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }

  return data
}

/* --------------------------------------------------------------------- */
/* Authentication                                                         */
/* --------------------------------------------------------------------- */

export const authApi = {
  register(email, password) {
    return request('POST', '/auth/register', { body: { email, password } })
  },
  login(email, password) {
    return request('POST', '/auth/login', { body: { email, password } })
  },
}

/* --------------------------------------------------------------------- */
/* Products                                                              */
/* --------------------------------------------------------------------- */

export const productsApi = {
  list() {
    return request('GET', '/products/')
  },
  get(id) {
    return request('GET', `/products/${id}`)
  },
  search(query) {
    return request('GET', '/products/search', { query: { q: query } })
  },
  filterByCategory(category) {
    return request('GET', '/products/filter', { query: { category } })
  },
}

/* --------------------------------------------------------------------- */
/* Cart                                                                  */
/* --------------------------------------------------------------------- */

export const cartApi = {
  get(userId) {
    return request('GET', `/cart/${userId}`)
  },
  add(userId, productId, quantity) {
    return request('POST', '/cart/add', {
      body: { user_id: userId, product_id: productId, quantity },
    })
  },
  update(userId, productId, quantity) {
    return request('PUT', '/cart/update', {
      body: { user_id: userId, product_id: productId, quantity },
    })
  },
  remove(userId, productId) {
    return request('DELETE', `/cart/remove/${productId}`, {
      query: { user_id: userId },
    })
  },
}

/* --------------------------------------------------------------------- */
/* Discounts                                                             */
/* --------------------------------------------------------------------- */

export const discountApi = {
  apply(subtotal, discountId) {
    return request('POST', '/discounts/apply', {
      body: { subtotal, discount_id: discountId },
    })
  },
}

/* --------------------------------------------------------------------- */
/* Checkout                                                              */
/* --------------------------------------------------------------------- */

export const checkoutApi = {
  checkout(userId, discountId = null) {
    return request('POST', '/checkout/', {
      body: { user_id: userId, discount_id: discountId },
    })
  },
}

/* --------------------------------------------------------------------- */
/* Health                                                                */
/* --------------------------------------------------------------------- */

export const healthApi = {
  check() {
    return request('GET', '/health')
  },
}

export { BASE_URL }
