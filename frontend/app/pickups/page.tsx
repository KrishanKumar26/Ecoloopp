import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

export default function PickupsPage() {
  // Sample pickup data for demonstration
  const samplePickups = [
    {
      id: "1",
      itemDescription: "Samsung Galaxy S10 Smartphone",
      status: "completed" as const,
      scheduledAt: "2026-10-05T14:00:00Z",
      ecoPoints: 75,
    },
    {
      id: "2",
      itemDescription: "Dell Latitude E7450 Laptop",
      status: "accepted" as const,
      scheduledAt: "2026-10-09T10:30:00Z",
      ecoPoints: 75,
    },
    {
      id: "3",
      itemDescription: "HP DeskJet 2600 Printer",
      status: "pending" as const,
      scheduledAt: "2026-10-12T15:00:00Z",
      ecoPoints: 75,
    },
  ];

  const statusStyles = {
    pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
    accepted: "bg-blue-100 text-blue-800 border-blue-200",
    in_transit: "bg-purple-100 text-purple-800 border-purple-200",
    completed: "bg-green-100 text-green-800 border-green-200",
    cancelled: "bg-gray-100 text-gray-800 border-gray-200",
  };

  const statusLabels = {
    pending: "Pending",
    accepted: "Accepted",
    in_transit: "In Transit",
    completed: "Completed",
    cancelled: "Cancelled",
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Your Pickups</h1>
            <p className="text-lg text-gray-600">
              Track the status of your e-waste pickup requests
            </p>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-8">
            <p className="text-sm text-amber-800">
              ⚡ <strong>Sample Data:</strong> The pickups below are demonstration data. 
              Real pickup tracking will be available once the backend API is connected.
            </p>
          </div>

          <div className="space-y-4">
            {samplePickups.map((pickup) => (
              <div
                key={pickup.id}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-sm transition-shadow"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                  <div className="flex-1 mb-4 md:mb-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {pickup.itemDescription}
                      </h3>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium border ${
                          statusStyles[pickup.status]
                        }`}
                      >
                        {statusLabels[pickup.status]}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      Scheduled: {new Date(pickup.scheduledAt).toLocaleString('en-US', {
                        dateStyle: 'medium',
                        timeStyle: 'short',
                      })}
                    </p>
                    {pickup.status === "completed" && (
                      <p className="text-sm text-eco-green-600 font-medium mt-2">
                        ✓ {pickup.ecoPoints} EcoPoints awarded
                      </p>
                    )}
                  </div>

                  <div className="flex space-x-3">
                    {pickup.status === "pending" && (
                      <button
                        disabled
                        className="px-4 py-2 text-sm font-medium text-gray-400 bg-gray-100 rounded-md cursor-not-allowed"
                      >
                        Cancel (Not Implemented)
                      </button>
                    )}
                    {pickup.status === "accepted" && (
                      <div className="text-sm text-gray-600">
                        Awaiting collector arrival
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-2">📋 Implementation Note</h3>
            <p className="text-sm text-blue-800">
              This page will fetch real pickup data from <code className="bg-blue-100 px-1 rounded">GET /pickups</code> 
              and allow users to view OTP codes, track status changes (pending → accepted → in_transit → completed), 
              and cancel pickups if needed.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
