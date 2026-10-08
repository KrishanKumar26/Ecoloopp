interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  color?: 'green' | 'blue' | 'purple' | 'orange';
}

export default function StatCard({ title, value, subtitle, icon, color = 'green' }: StatCardProps) {
  const colorClasses = {
    green: 'bg-eco-green-50 text-eco-green-700 border-eco-green-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
  };

  return (
    <div className={`border rounded-lg p-6 ${colorClasses[color]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          {subtitle && (
            <p className="text-xs opacity-70 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="text-2xl ml-4">{icon}</div>
        )}
      </div>
    </div>
  );
}
