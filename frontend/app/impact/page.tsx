import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import StatCard from "@/components/StatCard";

export default function ImpactPage() {
  // Sample leaderboard data
  const sampleLeaderboard = [
    { rank: 1, name: "Alex Chen", ecoPoints: 1250 },
    { rank: 2, name: "Sarah Martinez", ecoPoints: 980 },
    { rank: 3, name: "Jordan Kim", ecoPoints: 825 },
    { rank: 4, name: "Taylor Brown", ecoPoints: 675 },
    { rank: 5, name: "Morgan Lee", ecoPoints: 540 },
    { rank: 6, name: "Casey Wilson", ecoPoints: 450 },
    { rank: 7, name: "Jamie Davis", ecoPoints: 375 },
    { rank: 8, name: "Riley Johnson", ecoPoints: 300 },
    { rank: 9, name: "Drew Anderson", ecoPoints: 225 },
    { rank: 10, name: "You", ecoPoints: 225 },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Environmental Impact</h1>
            <p className="text-lg text-gray-600">
              Track your contribution to a cleaner planet
            </p>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-8">
            <p className="text-sm text-amber-800">
              ⚡ <strong>Sample Data:</strong> Statistics and leaderboard shown below are for demonstration. 
              Real impact data will be calculated from verified pickups via the backend API.
            </p>
          </div>

          {/* Personal Impact Stats */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Personal Impact</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="EcoPoints Balance"
                value="225"
                subtitle="Earned from 3 pickups"
                icon="🌱"
                color="green"
              />
              <StatCard
                title="Items Recycled"
                value="5"
                subtitle="Lifetime total"
                icon="♻️"
                color="blue"
              />
              <StatCard
                title="Weight Recycled"
                value="5.2 kg"
                subtitle="Total e-waste processed"
                icon="⚖️"
                color="purple"
              />
              <StatCard
                title="CO₂e Avoided"
                value="91 kg"
                subtitle="Estimated emissions saved"
                icon="🌍"
                color="orange"
              />
            </div>

            <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Understanding CO₂ Impact</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                CO₂ savings are calculated using category-specific emission factors. For example, 
                recycling a mobile phone (avg. 0.18 kg) saves approximately <strong>12.6 kg CO₂e</strong> 
                compared to landfill disposal. These estimates are based on industry research and include 
                avoided mining, manufacturing, and disposal emissions.
              </p>
              <p className="text-xs text-gray-500 mt-3">
                Note: Calculations are estimates for demonstration purposes and may not reflect exact real-world measurements.
              </p>
            </div>
          </div>

          {/* Global Impact */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Global Community Impact</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard
                title="Total Pickups"
                value="1,024"
                subtitle="Completed globally"
                icon="📦"
                color="green"
              />
              <StatCard
                title="Total CO₂e Avoided"
                value="4,301 kg"
                subtitle="Community contribution"
                icon="🌍"
                color="blue"
              />
              <StatCard
                title="Active Users"
                value="287"
                subtitle="Making a difference"
                icon="👥"
                color="purple"
              />
            </div>
          </div>

          {/* Leaderboard */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Top Contributors</h2>
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rank
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        EcoPoints
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {sampleLeaderboard.map((user) => (
                      <tr
                        key={user.rank}
                        className={user.name === "You" ? "bg-eco-green-50" : ""}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {user.rank <= 3 ? (
                              <span className="text-xl">
                                {user.rank === 1 ? "🥇" : user.rank === 2 ? "🥈" : "🥉"}
                              </span>
                            ) : (
                              <span className="text-sm font-medium text-gray-900">
                                #{user.rank}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {user.name}
                            {user.name === "You" && (
                              <span className="ml-2 text-xs text-eco-green-600">(You)</span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm font-semibold text-gray-900">
                            {user.ecoPoints.toLocaleString()}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-2">📋 Implementation Note</h3>
            <p className="text-sm text-blue-800">
              This page will fetch real data from <code className="bg-blue-100 px-1 rounded">GET /dashboard/user/:user_id</code> and{" "}
              <code className="bg-blue-100 px-1 rounded">GET /dashboard/global</code>. 
              CO₂ calculations use the emission factors documented in AI_CONTEXT.md.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
