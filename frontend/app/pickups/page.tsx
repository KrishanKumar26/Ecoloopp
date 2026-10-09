'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';
import { getPickups, cancelPickup, completePickup, type Pickup } from '@/lib/api';
import { getToken } from '@/lib/auth';

export default function PickupsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isLoading } = useAuth();

  const [pickups, setPickups] = useState<Pickup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const [completingId, setCompletingId] = useState<string | null>(null);
  const [otpInput, setOtpInput] = useState<{ [key: string]: string }>({});

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [isLoading, user, router]);

  // Load pickups
  useEffect(() => {
    if (user) {
      loadPickups();
    }
  }, [user]);

  const loadPickups = async () => {
    const token = getToken();
    if (!token) {
      setError('Not authenticated');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await getPickups(token);
      setPickups(response.pickups);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load pickups');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (pickupId: string) => {
    const reason = prompt('Please enter a reason for cancellation:');
    if (!reason) return;

    const token = getToken();
    if (!token) return;

    try {
      setCancellingId(pickupId);
      await cancelPickup(token, pickupId, reason);
      await loadPickups();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to cancel pickup');
    } finally {
      setCancellingId(null);
    }
  };

  const handleComplete = async (pickupId: string) => {
    const otp = otpInput[pickupId];
    if (!otp || otp.length !== 6) {
      alert('Please enter a valid 6-digit OTP');
      return;
    }

    const token = getToken();
    if (!token) return;

    try {
      setCompletingId(pickupId);
      const result = await completePickup(token, pickupId, otp);
      alert(result.message || 'Pickup completed successfully!');
      setOtpInput({ ...otpInput, [pickupId]: '' });
      await loadPickups();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to complete pickup');
    } finally {
      setCompletingId(null);
    }
  };

  const statusStyles = {
    pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    accepted: 'bg-blue-100 text-blue-800 border-blue-200',
    in_transit: 'bg-purple-100 text-purple-800 border-purple-200',
    completed: 'bg-green-100 text-green-800 border-green-200',
    cancelled: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  const statusLabels = {
    pending: 'Pending',
    accepted: 'Accepted',
    in_transit: 'In Transit',
    completed: 'Completed',
    cancelled: 'Cancelled',
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

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="mb-12 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Your Pickups</h1>
              <p className="text-lg text-gray-600">
                Track the status of your e-waste pickup requests
              </p>
            </div>
            <button
              onClick={() => router.push('/scan')}
              className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
            >
              Schedule New Pickup
            </button>
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
              <p className="text-gray-600">Loading pickups...</p>
            </div>
          ) : pickups.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No pickups yet</h3>
              <p className="text-gray-600 mb-6">Schedule your first e-waste pickup to get started</p>
              <button
                onClick={() => router.push('/scan')}
                className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
              >
                Schedule Pickup
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {pickups.map((pickup) => (
                <div
                  key={pickup.pickup_id}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-sm transition-shadow"
                >
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                    <div className="flex-1 mb-4 md:mb-0">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {pickup.item_description}
                        </h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium border ${
                            statusStyles[pickup.status as keyof typeof statusStyles] || statusStyles.pending
                          }`}
                        >
                          {statusLabels[pickup.status as keyof typeof statusLabels] || pickup.status}
                        </span>
                      </div>

                      <div className="space-y-1 text-sm text-gray-600">
                        <p>
                          <span className="font-medium">Scheduled:</span>{' '}
                          {new Date(pickup.scheduled_at).toLocaleString('en-US', {
                            dateStyle: 'medium',
                            timeStyle: 'short',
                          })}
                        </p>
                        <p>
                          <span className="font-medium">Address:</span>{' '}
                          {pickup.address.street}, {pickup.address.city}, {pickup.address.state} {pickup.address.pincode}
                        </p>

                        {pickup.otp && (
                          <p className="mt-2">
                            <span className="font-medium">Your OTP:</span>{' '}
                            <span className="font-mono font-bold text-green-600 text-lg">{pickup.otp}</span>
                            <span className="text-xs ml-2">(Expires: {new Date(pickup.otp_expires_at!).toLocaleString()})</span>
                          </p>
                        )}

                        {pickup.cancellation_reason && (
                          <p className="mt-2 text-red-600">
                            <span className="font-medium">Cancellation reason:</span> {pickup.cancellation_reason}
                          </p>
                        )}

                        {pickup.eco_points_awarded && (
                          <p className="text-green-600 font-medium mt-2">
                            ✓ 75 EcoPoints awarded
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col space-y-2 min-w-[200px]">
                      {pickup.status === 'pending' && (
                        <button
                          onClick={() => handleCancel(pickup.pickup_id)}
                          disabled={cancellingId === pickup.pickup_id}
                          className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          {cancellingId === pickup.pickup_id ? 'Cancelling...' : 'Cancel Pickup'}
                        </button>
                      )}

                      {pickup.status === 'accepted' && (
                        <>
                          <button
                            onClick={() => handleCancel(pickup.pickup_id)}
                            disabled={cancellingId === pickup.pickup_id}
                            className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            {cancellingId === pickup.pickup_id ? 'Cancelling...' : 'Cancel Pickup'}
                          </button>
                          <div className="text-sm text-gray-600 text-center py-2">
                            Awaiting collector arrival
                          </div>
                        </>
                      )}

                      {(pickup.status === 'pending' || pickup.status === 'accepted') && pickup.otp && (
                        <div className="border-t pt-3">
                          <label className="text-xs text-gray-500 block mb-1">Complete with OTP:</label>
                          <div className="flex gap-2">
                            <input
                              type="text"
                              maxLength={6}
                              placeholder="Enter OTP"
                              value={otpInput[pickup.pickup_id] || ''}
                              onChange={(e) => setOtpInput({ ...otpInput, [pickup.pickup_id]: e.target.value.replace(/\D/g, '') })}
                              className="flex-1 px-3 py-1 border border-gray-300 rounded-md text-sm"
                            />
                            <button
                              onClick={() => handleComplete(pickup.pickup_id)}
                              disabled={completingId === pickup.pickup_id}
                              className="px-3 py-1 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {completingId === pickup.pickup_id ? '...' : 'Complete'}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
