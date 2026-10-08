import Link from "next/link";

export default function Navigation() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and tagline */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-eco-green-600 rounded-lg">
                <span className="text-white text-xl font-bold">♻</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">EcoLoop</h1>
                <p className="text-xs text-gray-500">Turn Waste Into Value</p>
              </div>
            </Link>
          </div>

          {/* Navigation links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link 
              href="/" 
              className="text-gray-700 hover:text-eco-green-600 font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link 
              href="/scan" 
              className="text-gray-700 hover:text-eco-green-600 font-medium transition-colors"
            >
              Scan E-Waste
            </Link>
            <Link 
              href="/pickups" 
              className="text-gray-700 hover:text-eco-green-600 font-medium transition-colors"
            >
              Pickups
            </Link>
            <Link 
              href="/impact" 
              className="text-gray-700 hover:text-eco-green-600 font-medium transition-colors"
            >
              Impact
            </Link>
          </div>

          {/* CTA Button */}
          <div>
            <Link
              href="/scan"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-eco-green-600 hover:bg-eco-green-700 transition-colors"
            >
              Scan E-Waste
            </Link>
          </div>
        </div>

        {/* Mobile navigation */}
        <div className="md:hidden pb-3 flex space-x-4">
          <Link href="/" className="text-sm text-gray-700 hover:text-eco-green-600">
            Dashboard
          </Link>
          <Link href="/scan" className="text-sm text-gray-700 hover:text-eco-green-600">
            Scan
          </Link>
          <Link href="/pickups" className="text-sm text-gray-700 hover:text-eco-green-600">
            Pickups
          </Link>
          <Link href="/impact" className="text-sm text-gray-700 hover:text-eco-green-600">
            Impact
          </Link>
        </div>
      </div>
    </nav>
  );
}
