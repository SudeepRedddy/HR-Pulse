import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import { Users, Briefcase, FileText, TrendingDown, Star } from 'lucide-react';
import api from '../api/client';
import { Card, PageHeader, LoadingSpinner } from '../components/ui';

export function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: async () => {
      const res = await api.get('/powerbi/summary');
      return res.data;
    },
  });

  if (isLoading) return <LoadingSpinner />;

  const summary = data || {
    total_employees: 0,
    open_roles: 0,
    total_candidates: 0,
    attrition_rate: 0,
    avg_satisfaction: 0,
    department_breakdown: {},
    salary_distribution: {},
  };

  const COLORS = ['#0A0A0A', '#C9A96E', '#6B7280', '#404040', '#9CA3AF', '#D1D5DB'];
  const departmentData = Object.entries(summary.department_breakdown).map(([name, value], index) => ({
    name,
    value,
    color: COLORS[index % COLORS.length]
  }));

  const salaryData = Object.entries(summary.salary_distribution).map(([name, value]) => ({
    name,
    employees: value
  }));

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader 
        title="Executive Analytics" 
        subtitle="Real-time workforce intelligence and hiring pipeline metrics."
      />

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="hover:border-hr-gold transition-colors duration-300">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">Headcount</h3>
            <Users className="w-4 h-4 text-hr-gold" />
          </div>
          <p className="text-4xl font-sans font-medium tracking-tight text-hr-black">{summary.total_employees}</p>
        </Card>
        
        <Card className="hover:border-hr-gold transition-colors duration-300">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">Open Roles</h3>
            <Briefcase className="w-4 h-4 text-hr-gold" />
          </div>
          <p className="text-4xl font-sans font-medium tracking-tight text-hr-black">{summary.open_roles}</p>
        </Card>

        <Card className="hover:border-hr-gold transition-colors duration-300">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">Candidates</h3>
            <FileText className="w-4 h-4 text-hr-gold" />
          </div>
          <p className="text-4xl font-sans font-medium tracking-tight text-hr-black">{summary.total_candidates}</p>
        </Card>

        <Card className="hover:border-hr-gold transition-colors duration-300">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">Attrition</h3>
            <TrendingDown className="w-4 h-4 text-hr-gold" />
          </div>
          <p className="text-4xl font-sans font-medium tracking-tight text-hr-black">{summary.attrition_rate}<span className="text-lg text-gray-400">%</span></p>
        </Card>

        <Card className="hover:border-hr-gold transition-colors duration-300">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">Satisfaction</h3>
            <Star className="w-4 h-4 text-hr-gold" />
          </div>
          <p className="text-4xl font-sans font-medium tracking-tight text-hr-black">{summary.avg_satisfaction}<span className="text-lg text-gray-400">/4</span></p>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Department Breakdown Chart */}
        <Card className="flex flex-col h-[400px]">
          <h3 className="text-sm font-semibold mb-6 uppercase tracking-wider text-gray-800">Department Distribution</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={departmentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {departmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ borderRadius: '4px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} 
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Salary Distribution Chart */}
        <Card className="flex flex-col h-[400px]">
          <h3 className="text-sm font-semibold mb-6 uppercase tracking-wider text-gray-800 flex justify-between items-center">
            Salary Bracket Distribution
            <span className="text-[10px] text-hr-gold tracking-widest bg-gray-50 py-1 px-2 rounded-full border border-hr-border">LIVE</span>
          </h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={salaryData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8E8E8" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 11}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 11}} />
                <RechartsTooltip 
                  cursor={{fill: '#F9FAFB'}}
                  contentStyle={{ borderRadius: '4px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} 
                />
                <Bar dataKey="employees" fill="#0A0A0A" barSize={40} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
