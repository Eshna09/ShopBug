"""
Reproduction test for B011.
App.jsx has the /cart and /orders routes swapped:
    <Route path="/cart"   element={<Orders />} />
    <Route path="/orders" element={<Cart />}   />

This test reads App.jsx and confirms the route assignment is incorrect.
"""
import re
from pathlib import Path

# Resolve from the tests/reproduction_tests/ directory up to the project root
# then into frontend/src/App.jsx
APP_JSX = Path(__file__).resolve().parents[2] / "frontend" / "src" / "App.jsx"


def test_B011():
    """
    Expected: path="/cart" renders <Cart />, path="/orders" renders <Orders />.
    Actual:   path="/cart" renders <Orders />, path="/orders" renders <Cart />.
    """
    assert APP_JSX.exists(), f"App.jsx not found at {APP_JSX}"
    src = APP_JSX.read_text(encoding="utf-8")

    # Find what each path renders
    cart_route   = re.search(r'path="/cart"\s+element=\{<(\w+)', src)
    orders_route = re.search(r'path="/orders"\s+element=\{<(\w+)', src)

    assert cart_route,   "Could not find path='/cart' route in App.jsx"
    assert orders_route, "Could not find path='/orders' route in App.jsx"

    cart_component   = cart_route.group(1)
    orders_component = orders_route.group(1)

    assert cart_component == "Cart", (
        f"Expected path='/cart' to render <Cart />, but it renders <{cart_component} /> — "
        f"routes are swapped (B011 is active)"
    )
    assert orders_component == "Orders", (
        f"Expected path='/orders' to render <Orders />, but it renders <{orders_component} /> — "
        f"routes are swapped (B011 is active)"
    )
