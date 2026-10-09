'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import StatCard from '@/components/StatCard';
import { useAuth } from '@/contexts/AuthContext';
import { getEcoPointsStats, getEcoPointsTransactions, type EcoPointTransaction } from '@/lib/api';
import { getToken } from '@/lib/auth';

export default function ImpactPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  const [stats, setStats] = useState<any>(null);
  const [transactions, setTransactions] = useState<EcoPointTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [isLoading, user, router]);

  // Load stats and transactions
  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    const token = getToken();
    if (!token) {
      setError('Not authenticated');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const [statsData, transactionsData] = await Promise.all([
        getEcoPointsStats(token),
        getEcoPointsTransactions(token, 10),
      ]);

      setStats(statsData);
      setTransactions(transactionsData.transactions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Navigation />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <svg className="animate-spin h-12 w-12 text-green-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-gray-600">Loading...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Calculate estimated CO2 savings (70kg per pickup as estimate)
  const estimatedCO2 = stats ? (stats.pickups_completed * 70) : 0;

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

          {error && (
            <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <svg className="animate-spin h-12 w-12 text-green-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-600">Loading your impact...</p>
            </div>
          ) : (
            <>
              {/* Personal Impact Stats */}
              <div className="mb-12">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Personal Impact</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatCard
                    title="EcoPoints Balance"
                    value={stats?.current_balance?.toString() || '0'}
                    subtitle={`From ${stats?.pickups_completed || 0} pickups`}
                    icon="🌱"
                    color="green"
                  />
                  <StatCard
                    title="Pickups Completed"
                    value={stats?.pickups_completed?.toString() || '0'}
                    subtitle="Total completed"
                    icon="♻️"
                    color="blue"
                  />
                  <StatCard
                    title="Total Earned"
                    value={stats?.total_earned?.toString() || '0'}
                    subtitle="Lifetime points"
                    icon="⚡"
                    color="purple"
                  />
                  <StatCard
                    title="Your Rank"
                    value={`#${stats?.rank || 0}`}
                    subtitle="Community leaderboard"
                    icon="�"
                    color="orange"
                  />
                </div>

                <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Understanding EcoPoints</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    You earn <strong>75 EcoPoints</strong> for each completed pickup that is verified with OTP.
                    Points are awarded only when the pickup status is marked as "completed" - not for pending or
                    accepted pickups. This ensures fair rewards for actual e-waste recycling.
                  </p>
                  <p className="text-sm text-gray-600 mt-3">
                    <strong>Estimated CO₂ Impact:</strong> Each pickup saves approximately 70kg of CO₂ emissions
                    compared to landfill disposal. Your {stats?.pickups_completed || 0} completed pickups have
                    saved an estimated <strong>{estimatedCO2}kg of CO₂</strong>!
                  </p>
                </div>
              </div>

              {/* Recent Transactions */}
              {transactions.length > 0 && (
                <div className="mb-12">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Transactions</h2>
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Date
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Reason
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Points
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {transactions.map((transaction) => (
                            <tr key={transaction.transaction_id}>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">
                                  {new Date(transaction.created_at).toLocaleDateString('en-US', {
                                    month: 'short',
                                    day: 'numeric',
                                    year: 'numeric',
                                  })}
                                </div>
                              </td>
                              <td className="px-6 py-4">
                                <div className="text-sm text-gray-900">
                                  {transaction.reason}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-right">
                                <div className={`text-sm font-semibold ${transaction.points > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {transaction.points > 0 ? '+' : ''}{transaction.points}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Empty State */}
              {stats?.pickups_completed === 0 && (
                <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
                  <div className="text-6xl mb-4">🌱</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Start Your Impact Journey</h3>
                  <p className="text-gray-600 mb-6">
                    Complete your first pickup to start earning EcoPoints and making a difference!
                  </p>
                  <button
                    onClick={() => router.push('/scan')}
                    className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
                  >
                    Schedule First Pickup
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
