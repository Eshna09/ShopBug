export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-2 sm:flex-row">
          <p className="flex items-center gap-1 text-sm text-gray-500">
            <span className="text-lg">🐛</span>
            Shop<span className="font-semibold text-gray-700">Bug</span>
          </p>
          <p className="text-sm text-gray-400">
            © {new Date().getFullYear()} ShopBug. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
