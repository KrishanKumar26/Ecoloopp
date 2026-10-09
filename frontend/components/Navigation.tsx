'use client';

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";

export default function Navigation() {
  const { user, isLoading, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

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

          {/* Auth Section */}
          <div className="flex items-center space-x-4">
            {isLoading ? (
              <div className="h-8 w-24 bg-gray-200 animate-pulse rounded"></div>
            ) : user ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  <div className="w-8 h-8 bg-eco-green-100 rounded-full flex items-center justify-center">
                    <span className="text-eco-green-700 font-bold">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className="hidden md:block">{user.name}</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setShowUserMenu(false)}
                    ></div>
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20 border border-gray-200">
                      <div className="px-4 py-2 border-b border-gray-200">
                        <p className="text-sm font-medium text-gray-900">{user.name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                        <p className="text-xs text-eco-green-600 mt-1">
                          🌱 {user.eco_points} EcoPoints
                        </p>
                      </div>
                      <button
                        onClick={() => {
                          logout();
                          setShowUserMenu(false);
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Sign out
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-eco-green-600 hover:bg-eco-green-700 transition-colors"
                >
                  Get Started
                </Link>
              </div>
            )}
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
