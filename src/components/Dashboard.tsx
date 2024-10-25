import React from 'react';
import { BarChart, Users, Database } from 'lucide-react';

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <DashboardCard icon={<Database className="w-8 h-8" />} title="Total Databases" value="9" />
        <DashboardCard icon={<Users className="w-8 h-8" />} title="Active Connections" value="24" />
        <DashboardCard icon={<BarChart className="w-8 h-8" />} title="Queries Today" value="1,204" />
      </div>
    </div>
  );
};

const DashboardCard: React.FC<{ icon: React.ReactNode; title: string; value: string }> = ({ icon, title, value }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {icon}
          <h2 className="text-xl font-semibold">{title}</h2>
        </div>
        <span className="text-3xl font-bold">{value}</span>
      </div>
    </div>
  );
};

export default Dashboard;