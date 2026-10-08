export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-3 mb-4 md:mb-0">
            <div className="flex items-center justify-center w-8 h-8 bg-eco-green-600 rounded-lg">
              <span className="text-white text-lg font-bold">♻</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">EcoLoop</h2>
              <p className="text-xs text-gray-500">Every item recycled makes a difference</p>
            </div>
          </div>
          
          <div className="text-center md:text-right">
            <p className="text-sm text-gray-600">
              Built for responsible e-waste disposal
            </p>
            <p className="text-xs text-gray-500 mt-1">
              © 2026 EcoLoop — Hackathon MVP
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
