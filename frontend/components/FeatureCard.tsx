interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

export default function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:border-eco-green-300 hover:shadow-sm transition-all">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 text-3xl">{icon}</div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );
}
