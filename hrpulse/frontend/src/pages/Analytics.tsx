import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import {
  TrendingUp, TrendingDown, ShieldAlert, Award, DollarSign,
  Users, AlertTriangle
} from 'lucide-react';
import api from '../api/client';
import { Card, PageHeader, LoadingSpinner, Badge } from '../components/ui';

/* ──── colour tokens (monochrome luxury palette) ──── */
const C = {
  black: '#0A0A0A',
  gold: '#C9A96E',
  gray: '#6B7280',
  grayLight: '#9CA3AF',
  grayLighter: '#D1D5DB',
  surface: '#F5F5F5',
};

/* ──── tiny stat card ──── */
function Stat({ label, value, sub, icon: Icon }: { label: string; value: string | number; sub?: string; icon: any }) {
  return (
    <Card className="hover:border-hr-gold transition-colors duration-300">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">{label}</h3>
        <Icon className="w-4 h-4 text-hr-gold" />
      </div>
      <p className="text-4xl font-sans font-medium tracking-tight text-hr-black">{value}</p>
      {sub && <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-wider">{sub}</p>}
    </Card>
  );
}

/* ════════════════════════════════════════════════════ */
/*  MAIN PAGE                                         */
/* ════════════════════════════════════════════════════ */
export function Analytics() {
  const [activeTab, setActiveTab] = useState<'overview' | 'retention' | 'departments' | 'promotions' | 'salary'>('overview');

  /* ── data queries ───────────────────────── */
  const { data: forecast, isLoading: loadF } = useQuery({
    queryKey: ['forecast'],
    queryFn: async () => (await api.get('/predictions/workforce-forecast')).data,
  });

  const { data: retention, isLoading: loadR } = useQuery({
    queryKey: ['retention'],
    queryFn: async () => (await api.get('/predictions/retention-risk')).data,
  });

  const { data: deptHealth, isLoading: loadD } = useQuery({
    queryKey: ['deptHealth'],
    queryFn: async () => (await api.get('/predictions/department-health')).data,
  });

  const { data: promos, isLoading: loadP } = useQuery({
    queryKey: ['promos'],
    queryFn: async () => (await api.get('/predictions/promotion-readiness')).data,
  });

  const { data: salary, isLoading: loadS } = useQuery({
    queryKey: ['salary'],
    queryFn: async () => (await api.get('/predictions/salary-insights')).data,
  });

  const isLoading = loadF || loadR || loadD || loadP || loadS;

  if (isLoading) return <LoadingSpinner />;

  /* ── derived chart data ─────────────────── */
  const heatmapData = forecast?.department_heatmap
    ? Object.entries(forecast.department_heatmap).map(([dept, v]: [string, any]) => ({
        name: dept,
        risk: v.avg_risk,
        headcount: v.headcount,
        highRisk: v.high_risk_count,
      }))
    : [];

  const deptChartData = deptHealth?.departments?.map((d: any) => ({
    department: d.department,
    Health: d.health_score,
    Satisfaction: (d.avg_satisfaction / 4) * 100,
    Performance: (d.avg_performance / 4) * 100,
  })) || [];

  const salaryBrackets = salary?.salary_brackets
    ? Object.entries(salary.salary_brackets).map(([name, value]) => ({ name, value }))
    : [];

  const deptSalaryData = salary?.department_analysis
    ? Object.entries(salary.department_analysis).map(([dept, v]: [string, any]) => ({
        name: dept,
        avg: v.avg_salary,
        delta: v.vs_company_avg,
      }))
    : [];

  const CHART_COLORS = [C.black, C.gold, C.gray, '#404040', C.grayLight, C.grayLighter];

  /* ── tabs ───────────────────────────────── */
  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'retention', label: 'Retention Risk' },
    { key: 'departments', label: 'Departments' },
    { key: 'promotions', label: 'Promotions' },
    { key: 'salary', label: 'Salary Insights' },
  ] as const;

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title="Analytics & Predictions"
        subtitle="AI-driven workforce intelligence — attrition forecasts, department health, promotion pipeline, and salary equity."
      />

      {/* ── Tab Bar ── */}
      <div className="flex space-x-1 border-b border-hr-border">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-6 py-3 text-sm font-medium transition-all ${
              activeTab === t.key
                ? 'border-b-2 border-hr-gold text-hr-black'
                : 'text-gray-500 hover:text-hr-black'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ════════════ OVERVIEW TAB ════════════ */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* ── KPI Row ──────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Stat label="Headcount" value={forecast?.total_employees ?? '—'} icon={Users} />
            <Stat label="Attrition Rate" value={`${forecast?.current_attrition_rate ?? 0}%`} icon={TrendingDown} />
            <Stat
              label="Predicted Exits"
              value={forecast?.predicted_exits_next_quarter ?? 0}
              sub="Next quarter"
              icon={ShieldAlert}
            />
            <Stat
              label="High Risk"
              value={forecast?.high_risk_employees ?? 0}
              sub="Employees"
              icon={AlertTriangle}
            />
            <Stat
              label="Hiring Need"
              value={forecast?.recommended_hires ?? 0}
              sub="Recommended"
              icon={TrendingUp}
            />
          </div>

          {/* ── Charts Row ────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Department Risk Heatmap */}
            <Card className="flex flex-col h-[380px]">
              <h3 className="text-sm font-semibold mb-6 uppercase tracking-wider text-gray-800 flex justify-between items-center">
                Department Risk Heatmap
                <span className="text-[10px] text-hr-gold tracking-widest bg-gray-50 py-1 px-2 rounded-full border border-hr-border">
                  AI MODEL
                </span>
              </h3>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={heatmapData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8E8E8" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 11 }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 11 }} unit="%" />
                    <RechartsTooltip
                      cursor={{ fill: '#F9FAFB' }}
                      contentStyle={{ borderRadius: '4px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }}
                    />
                    <Bar dataKey="risk" fill={C.black} barSize={36} radius={[4, 4, 0, 0]} name="Avg Risk %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Salary Brackets */}
            <Card className="flex flex-col h-[380px]">
              <h3 className="text-sm font-semibold mb-6 uppercase tracking-wider text-gray-800">
                Salary Distribution
              </h3>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={salaryBrackets}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={95}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {salaryBrackets.map((_: any, i: number) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{ borderRadius: '4px', border: '1px solid #e5e7eb', fontSize: '12px' }}
                    />
                    <Legend verticalAlign="bottom" height={36} iconType="circle" />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* ════════════ RETENTION RISK TAB ════════════ */}
      {activeTab === 'retention' && (
        <div className="space-y-6">
          {/* Summary pills */}
          <div className="flex space-x-4">
            <div className="px-5 py-3 bg-red-50 border border-red-200 rounded-sm text-sm font-medium text-red-700">
              High: {retention?.total_high_risk ?? 0}
            </div>
            <div className="px-5 py-3 bg-amber-50 border border-amber-200 rounded-sm text-sm font-medium text-amber-700">
              Medium: {retention?.total_medium_risk ?? 0}
            </div>
            <div className="px-5 py-3 bg-green-50 border border-green-200 rounded-sm text-sm font-medium text-green-700">
              Low: {retention?.total_low_risk ?? 0}
            </div>
          </div>

          <Card className="p-0 overflow-hidden">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50 border-b border-hr-border">
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Employee</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Department</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Tenure</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Risk Score</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Contributing Factors</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hr-border">
                {retention?.top_at_risk?.map((r: any) => (
                  <tr key={r.employee_id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-9 h-9 bg-hr-black text-hr-gold rounded-full flex items-center justify-center font-serif text-xs">
                          {r.name.split(' ').map((n: string) => n[0]).join('')}
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-hr-black">{r.name}</div>
                          <div className="text-[10px] text-gray-400">{r.job_role}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{r.department}</td>
                    <td className="px-6 py-4 text-sm text-hr-black font-medium">{r.tenure_years} yrs</td>
                    <td className="px-6 py-4">
                      <Badge variant={r.risk_level === 'High' ? 'danger' : r.risk_level === 'Medium' ? 'warning' : 'success'}>
                        {r.risk_level} — {r.risk_score}%
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {r.factors?.slice(0, 3).map((f: string, i: number) => (
                          <span key={i} className="text-[10px] px-2 py-0.5 bg-gray-100 text-gray-600 rounded-sm border border-gray-200">
                            {f}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* ════════════ DEPARTMENTS TAB ════════════ */}
      {activeTab === 'departments' && (
        <div className="space-y-8">
          {/* Department Health Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {deptHealth?.departments?.map((d: any) => (
              <Card key={d.department} className="hover:border-hr-gold transition-colors duration-300">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-serif">{d.department}</h4>
                    <p className="text-[10px] text-gray-400 uppercase tracking-widest">{d.headcount} employees</p>
                  </div>
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center font-serif text-xl border-2 ${
                    d.health_score >= 60 ? 'border-green-300 text-green-700 bg-green-50' :
                    d.health_score >= 40 ? 'border-amber-300 text-amber-700 bg-amber-50' :
                    'border-red-300 text-red-700 bg-red-50'
                  }`}>
                    {Math.round(d.health_score)}
                  </div>
                </div>

                <div className="space-y-3 pt-4 border-t border-hr-border">
                  <MetricBar label="Satisfaction" value={d.avg_satisfaction} max={4} />
                  <MetricBar label="Performance" value={d.avg_performance} max={4} />
                  <MetricBar label="Work-Life Balance" value={d.avg_work_life_balance} max={4} />
                  <div className="flex justify-between text-xs text-gray-500 pt-2">
                    <span>Overtime: {d.overtime_pct}%</span>
                    <span>Attrition: {d.attrition_pct}%</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Comparative Chart */}
          <Card className="flex flex-col h-[380px]">
            <h3 className="text-sm font-semibold mb-6 uppercase tracking-wider text-gray-800">
              Department Comparison
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptChartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8E8E8" />
                  <XAxis dataKey="department" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 11 }} />
                  <RechartsTooltip
                    cursor={{ fill: '#F9FAFB' }}
                    contentStyle={{ borderRadius: '4px', border: '1px solid #e5e7eb', fontSize: '12px' }}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Bar dataKey="Health" fill={C.black} barSize={18} radius={[3, 3, 0, 0]} />
                  <Bar dataKey="Satisfaction" fill={C.gold} barSize={18} radius={[3, 3, 0, 0]} />
                  <Bar dataKey="Performance" fill={C.gray} barSize={18} radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}

      {/* ════════════ PROMOTIONS TAB ════════════ */}
      {activeTab === 'promotions' && (
        <div className="space-y-6">
          <div className="flex items-center space-x-3 mb-2">
            <Award className="w-5 h-5 text-hr-gold" />
            <p className="text-sm text-gray-600">
              <span className="font-semibold text-hr-black">{promos?.total_ready ?? 0}</span> employees identified as promotion-ready based on tenure, performance, and manager endorsement.
            </p>
          </div>

          <Card className="p-0 overflow-hidden">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50 border-b border-hr-border">
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Employee</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Department</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Tenure</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Rating</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Readiness</th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Reasons</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hr-border">
                {promos?.promotion_candidates?.map((p: any) => (
                  <tr key={p.employee_id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-9 h-9 bg-hr-black text-hr-gold rounded-full flex items-center justify-center font-serif text-xs">
                          {p.name.split(' ').map((n: string) => n[0]).join('')}
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-hr-black">{p.name}</div>
                          <div className="text-[10px] text-gray-400">{p.job_role}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{p.department}</td>
                    <td className="px-6 py-4 text-sm font-medium">{p.tenure_years} yrs</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-1">
                        {[1, 2, 3, 4].map((star) => (
                          <div
                            key={star}
                            className={`w-2 h-2 rounded-full ${star <= p.performance_rating ? 'bg-hr-gold' : 'bg-gray-200'}`}
                          />
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-hr-black rounded-full transition-all duration-700"
                            style={{ width: `${p.readiness_score}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-hr-black">{p.readiness_score}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {p.reasons?.slice(0, 2).map((r: string, i: number) => (
                          <span key={i} className="text-[10px] px-2 py-0.5 bg-gray-100 text-gray-600 rounded-sm border border-gray-200">
                            {r}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* ════════════ SALARY INSIGHTS TAB ════════════ */}
      {activeTab === 'salary' && (
        <div className="space-y-8">
          {/* KPI Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Stat label="Avg Salary" value={`$${(salary?.overall_avg_salary ?? 0).toLocaleString()}`} icon={DollarSign} />
            <Stat label="Median Salary" value={`$${(salary?.overall_median_salary ?? 0).toLocaleString()}`} icon={DollarSign} />
            <Stat label="Total Employees" value={salary?.total_employees ?? 0} icon={Users} />
            <Stat
              label="Underpaid Flagged"
              value={salary?.underpaid_employees?.length ?? 0}
              sub="High performers"
              icon={AlertTriangle}
            />
          </div>

          {/* Department Salary Chart */}
          <Card className="flex flex-col h-[380px]">
            <h3 className="text-sm font-semibold mb-6 uppercase tracking-wider text-gray-800">
              Avg Salary by Department
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptSalaryData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8E8E8" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 11 }} />
                  <RechartsTooltip
                    cursor={{ fill: '#F9FAFB' }}
                    contentStyle={{ borderRadius: '4px', border: '1px solid #e5e7eb', fontSize: '12px' }}
                    formatter={(value: any) => [`$${Number(value).toLocaleString()}`, 'Avg Salary']}
                  />
                  <Bar dataKey="avg" fill={C.black} barSize={40} radius={[4, 4, 0, 0]} name="Avg Salary" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Underpaid Employees */}
          {salary?.underpaid_employees?.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-hr-gold" />
                <span>Compensation Equity Flags</span>
              </h3>
              <Card className="p-0 overflow-hidden">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-gray-50 border-b border-hr-border">
                      <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Employee</th>
                      <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Department</th>
                      <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Salary</th>
                      <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Dept Avg</th>
                      <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Gap</th>
                      <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Rating</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-hr-border">
                    {salary.underpaid_employees.map((u: any) => (
                      <tr key={u.employee_id} className="hover:bg-gray-50/50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="text-sm font-semibold text-hr-black">{u.name}</div>
                          <div className="text-[10px] text-gray-400">{u.job_role}</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{u.department}</td>
                        <td className="px-6 py-4 text-sm font-medium">${u.salary.toLocaleString()}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">${u.dept_avg.toLocaleString()}</td>
                        <td className="px-6 py-4">
                          <Badge variant="danger">-{u.gap_pct}%</Badge>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-1">
                            {[1, 2, 3, 4].map((star) => (
                              <div
                                key={star}
                                className={`w-2 h-2 rounded-full ${star <= u.performance_rating ? 'bg-hr-gold' : 'bg-gray-200'}`}
                              />
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ── helper component: metric bar ─────────── */
function MetricBar({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="flex items-center space-x-3">
      <span className="text-[10px] text-gray-500 w-28 shrink-0 uppercase tracking-wider">{label}</span>
      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full bg-hr-black rounded-full transition-all duration-700" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-medium text-hr-black w-10 text-right">{value}/{max}</span>
    </div>
  );
}
