import Link from "next/link";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import StatCard from "@/components/StatCard";
import FeatureCard from "@/components/FeatureCard";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navigation />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-eco-green-50 to-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
            <div className="text-center max-w-3xl mx-auto">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                Turn Your E-Waste Into Environmental Impact
              </h1>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Most households have no easy way to dispose of electronics responsibly. 
                EcoLoop connects you with certified recyclers—snap a photo, get AI-powered 
                safety tips, schedule a free pickup, and earn EcoPoints for doing the right thing.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/scan"
                  className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-eco-green-600 hover:bg-eco-green-700 transition-colors"
                >
                  📸 Scan E-Waste Now
                </Link>
                <Link
                  href="#features"
                  className="inline-flex items-center justify-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                  Learn How It Works
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Demo Status Banner */}
        <section className="bg-amber-50 border-b border-amber-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-center space-x-2">
              <span className="text-amber-700 font-medium text-sm">
                ⚡ Demo Mode — Sample data shown below for demonstration purposes
              </span>
            </div>
          </div>
        </section>

        {/* Dashboard Preview Section */}
        <section className="py-12 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">Your Impact Dashboard</h2>
              <p className="text-gray-600">Track your environmental contribution in real-time</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="EcoPoints Balance"
                value="225"
                subtitle="75 points per verified pickup"
                icon="🌱"
                color="green"
              />
              <StatCard
                title="Verified Pickups"
                value="3"
                subtitle="Completed this month"
                icon="✅"
                color="blue"
              />
              <StatCard
                title="E-Waste Recycled"
                value="5.2 kg"
                subtitle="Total weight processed"
                icon="♻️"
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

            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                Sample data for demonstration • CO₂ calculations based on category-specific emission factors
              </p>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">How EcoLoop Works</h2>
              <p className="text-gray-600">A seamless journey from waste to value</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <FeatureCard
                icon="📸"
                title="AI E-Waste Identification"
                description="Upload a photo of your electronic waste. Our AI classifies the item, estimates weight, and provides a confidence score—all in under 3 seconds."
              />
              <FeatureCard
                icon="🔒"
                title="Safe Disposal Recommendations"
                description="Receive tailored safety tips for handling your e-waste. From lithium battery warnings to CRT monitor precautions, we keep you informed."
              />
              <FeatureCard
                icon="🗺️"
                title="Recycler Discovery"
                description="Find certified recyclers within 25 km. View ratings, accepted categories, distance, and available pickup slots before you book."
              />
              <FeatureCard
                icon="📅"
                title="Pickup Scheduling"
                description="Choose your preferred date and time. Track your pickup status from pending → accepted → in transit → completed."
              />
              <FeatureCard
                icon="🔐"
                title="OTP Verification"
                description="Secure handoff with a 6-digit OTP valid for 30 minutes. Only verified pickups award EcoPoints—no fake claims."
              />
              <FeatureCard
                icon="🌱"
                title="EcoPoints & Impact"
                description="Earn 75 EcoPoints per completed pickup. View your total CO₂ savings, items recycled, and leaderboard ranking."
              />
            </div>
          </div>
        </section>

        {/* MVP Flow Section */}
        <section className="py-16 bg-white border-t border-gray-200">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">The Complete Flow</h2>
              <p className="text-gray-600">From image upload to environmental impact</p>
            </div>

            <div className="space-y-6">
              {[
                { step: 1, title: "Image Upload", desc: "Snap a photo of your e-waste" },
                { step: 2, title: "AI Identification", desc: "Get instant classification and safety tips" },
                { step: 3, title: "Safety Recommendation", desc: "Learn how to handle your item safely" },
                { step: 4, title: "Recycler Selection", desc: "Choose from certified nearby recyclers" },
                { step: 5, title: "Pickup Scheduling", desc: "Book a convenient date and time" },
                { step: 6, title: "Collector Acceptance", desc: "Recycler confirms your request" },
                { step: 7, title: "OTP Verification", desc: "Secure handoff with one-time password" },
                { step: 8, title: "Award 75 EcoPoints", desc: "Earn rewards automatically" },
                { step: 9, title: "Impact Dashboard", desc: "Track your environmental contribution" },
              ].map((item) => (
                <div
                  key={item.step}
                  className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-eco-green-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {item.step}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{item.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-eco-green-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Make an Impact?
            </h2>
            <p className="text-eco-green-100 text-lg mb-8 max-w-2xl mx-auto">
              Join the movement for responsible e-waste disposal. Every item you recycle 
              reduces harmful emissions and conserves natural resources.
            </p>
            <Link
              href="/scan"
              className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-eco-green-600 bg-white hover:bg-gray-50 transition-colors"
            >
              Start Scanning E-Waste
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
