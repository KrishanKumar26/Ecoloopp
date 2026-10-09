'use client';

import { useState, useRef, ChangeEvent, FormEvent, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';
import { classifyItem, ClassificationResult } from '@/lib/api';
import { getToken } from '@/lib/auth';

export default function ScanPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [itemName, setItemName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClassificationResult | null>(null);

  // Redirect to login if not authenticated (after loading completes)
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [isLoading, user, router]);

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

  // Return null if not authenticated (will redirect via useEffect)
  if (!user) {
    return null;
  }

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid image file (JPG, JPEG, PNG, or WEBP)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!itemName.trim()) {
      setError('Please enter an item name');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const token = getToken();
      if (!token) {
        setError('Not authenticated. Please log in again.');
        router.push('/login');
        return;
      }

      const classificationResult = await classifyItem(token, {
        item_name: itemName,
        image: selectedFile || undefined,
      });

      setResult(classificationResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Classification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setItemName('');
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSchedulePickup = () => {
    // Navigate to schedule pickup page with classification context
    if (result) {
      const params = new URLSearchParams({
        classification_id: result.classification_id,
        item_name: result.item_name,
        category: result.category,
      });
      router.push(`/pickups/schedule?${params.toString()}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              E-Waste Classification
            </h1>
            <p className="text-lg text-gray-600">
              Identify your electronic waste and get safety recommendations
            </p>
          </div>

          {/* Baseline Classifier Warning */}
          <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="font-semibold text-yellow-900 mb-1">
                  Baseline Classifier
                </h3>
                <p className="text-sm text-yellow-800">
                  This is a <strong>keyword-matching baseline classifier</strong>, not a trained ML model.
                  Results are based on simple pattern matching. Confidence scores are estimates.
                  For accurate classification, verify with local e-waste guidelines.
                </p>
              </div>
            </div>
          </div>

          {!result ? (
            <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8">
              {/* Item Name Input */}
              <div className="mb-6">
                <label htmlFor="itemName" className="block text-sm font-medium text-gray-700 mb-2">
                  Item Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="itemName"
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  placeholder="e.g., iPhone 12, Dell Laptop, LCD Monitor"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                />
              </div>

              {/* Image Upload */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Image (Optional)
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept="image/jpeg,image/jpg,image/png,image/webp"
                    className="hidden"
                    id="fileInput"
                  />
                  <label
                    htmlFor="fileInput"
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 cursor-pointer transition-colors"
                  >
                    Choose File
                  </label>
                  {selectedFile && (
                    <span className="text-sm text-gray-600">
                      {selectedFile.name}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Supported formats: JPG, JPEG, PNG, WEBP (max 10MB)
                </p>
              </div>

              {/* Image Preview */}
              {previewUrl && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preview
                  </label>
                  <div className="relative w-full max-w-md mx-auto">
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="w-full h-64 object-contain border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Classifying...
                    </span>
                  ) : (
                    'Classify Item'
                  )}
                </button>
                {(itemName || selectedFile) && (
                  <button
                    type="button"
                    onClick={handleReset}
                    disabled={loading}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 transition-colors"
                  >
                    Reset
                  </button>
                )}
              </div>
            </form>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-8">
              {/* Success Header */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                  <span className="text-3xl">✓</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Classification Complete
                </h2>
                <p className="text-gray-600">
                  {result.item_name}
                </p>
              </div>

              {/* Classification Results */}
              <div className="space-y-6">
                {/* Category */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Category</h3>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {result.category.replace('_', ' ')}
                  </p>
                </div>

                {/* Confidence */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Confidence</h3>
                  {typeof result.confidence === 'number' &&
                   !isNaN(result.confidence) &&
                   isFinite(result.confidence) ? (
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-green-600 h-3 rounded-full transition-all"
                          style={{ width: `${Math.min(100, Math.max(0, result.confidence * 100))}%` }}
                        ></div>
                      </div>
                      <span className="text-lg font-semibold text-gray-900">
                        {(result.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  ) : (
                    <p className="text-gray-600">Not available</p>
                  )}
                </div>

                {/* Estimated Weight */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Estimated Weight</h3>
                  {typeof result.estimated_weight_kg === 'number' &&
                   !isNaN(result.estimated_weight_kg) &&
                   isFinite(result.estimated_weight_kg) ? (
                    <p className="text-lg font-semibold text-gray-900">
                      {result.estimated_weight_kg.toFixed(2)} kg
                    </p>
                  ) : (
                    <p className="text-gray-600">Not available</p>
                  )}
                </div>

                {/* Safety Tips */}
                {result.safety_tips.length > 0 && (
                  <div className="border-b border-gray-200 pb-4">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Safety Tips</h3>
                    <ul className="space-y-2">
                      {result.safety_tips.map((tip, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-green-600 mt-1">•</span>
                          <span className="text-gray-700">{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Special Care Warning */}
                {result.special_care_warning && (
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">⚠️</span>
                      <div>
                        <h3 className="font-semibold text-orange-900 mb-1">
                          Special Care Required
                        </h3>
                        <p className="text-sm text-orange-800">
                          {result.special_care_warning}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex gap-4">
                <button
                  onClick={handleSchedulePickup}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
                >
                  Schedule Pickup
                </button>
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Classify Another Item
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
