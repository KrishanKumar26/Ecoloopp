import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

export default function ScanPage() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Scan E-Waste</h1>
            <p className="text-lg text-gray-600">
              Upload a photo to identify your electronic waste and get safety recommendations
            </p>
          </div>

          <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <div className="mb-6">
              <span className="text-6xl">📸</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Image Upload Interface
            </h2>
            <p className="text-gray-600 mb-6">
              This feature will be implemented with camera/file upload functionality
            </p>
            <div className="inline-block px-6 py-3 bg-gray-100 text-gray-500 rounded-md cursor-not-allowed">
              Upload Image (Coming Soon)
            </div>
          </div>

          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-2">📋 Implementation Note</h3>
            <p className="text-sm text-blue-800">
              This page will include: image upload (camera/file), preview, AI classification display, 
              safety tips, confidence score, and a &ldquo;Schedule Pickup&rdquo; action once the backend AI service is connected.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
