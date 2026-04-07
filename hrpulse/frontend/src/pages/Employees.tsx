import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Search, 
  Plus, 
  ChevronRight, 
  User, 
  Briefcase, 
  MapPin, 
  TrendingUp,
  AlertTriangle,
  X,
  Loader2,
  CheckCircle2
} from 'lucide-react';
import api from '../api/client';
import { Card, PageHeader, Badge } from '../components/ui';

interface Employee {
  id: string;
  name: string;
  age: number;
  gender: string;
  department: string;
  job_role: string;
  tenure_years: number;
  salary: number;
  performance_rating: number;
  job_satisfaction: number;
  attrition: string;
}

export function Employees() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  
  const [newEmp, setNewEmp] = useState({
    name: '',
    age: 30,
    gender: 'Male',
    department: 'Engineering',
    job_role: 'Software Engineer',
    salary: 80000,
    tenure_years: 0
  });

  const { data, isLoading } = useQuery({
    queryKey: ['employees', searchTerm, deptFilter],
    queryFn: async () => {
      const res = await api.get('/employees', {
        params: { search: searchTerm || undefined, department: deptFilter || undefined, page_size: 100 }
      });
      return res.data;
    }
  });

  const { data: performance, isLoading: isPerfLoading } = useQuery({
    queryKey: ['performance', selectedEmployee?.id],
    queryFn: async () => {
      const res = await api.get(`/employees/${selectedEmployee!.id}/performance`);
      return res.data;
    },
    enabled: !!selectedEmployee
  });

  const { data: riskData, isLoading: isRiskLoading } = useQuery({
    queryKey: ['risk', selectedEmployee?.id],
    queryFn: async () => {
      const res = await api.get(`/employees/${selectedEmployee!.id}/risk`);
      return res.data;
    },
    enabled: !!selectedEmployee
  });

  const createMutation = useMutation({
    mutationFn: (emp: any) => api.post('/employees', emp),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setIsAddModalOpen(false);
      setNewEmp({ name: '', age: 30, gender: 'Male', department: 'Engineering', job_role: 'Software Engineer', salary: 80000, tenure_years: 0 });
    }
  });

  return (
    <div className="space-y-8 animate-fade-in relative">
      <PageHeader 
        title="Employee Directory" 
        subtitle="Manage your global talent pool and view AI-predicted performance dossiers."
        action={
          <button onClick={() => setIsAddModalOpen(true)} className="btn-primary flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add Member</span>
          </button>
        }
      />

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            type="text"
            placeholder="Search by name or role..."
            className="input-field pl-11"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select 
          className="input-field md:w-64"
          value={deptFilter}
          onChange={(e) => setDeptFilter(e.target.value)}
        >
          <option value="">All Departments</option>
          <option value="Engineering">Engineering</option>
          <option value="Sales">Sales</option>
          <option value="Marketing">Marketing</option>
          <option value="HR">HR</option>
          <option value="Finance">Finance</option>
          <option value="Operations">Operations</option>
        </select>
      </div>

      {/* Table */}
      <Card className="p-0 overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-gray-50 border-b border-hr-border">
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Employee</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Role & Dept</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Tenure</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500">Status</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-gray-500 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hr-border">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-400 italic">
                  Retrieving intelligence...
                </td>
              </tr>
            ) : data?.employees?.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-400 italic">
                  No employees found.
                </td>
              </tr>
            ) : data?.employees?.map((emp: Employee) => (
              <tr key={emp.id} className="hover:bg-gray-50/50 transition-colors group cursor-pointer" onClick={() => setSelectedEmployee(emp)}>
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-hr-black text-hr-gold rounded-full flex items-center justify-center font-serif text-sm">
                      {emp.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-hr-black">{emp.name}</div>
                      <div className="text-[10px] text-gray-400 uppercase tracking-tight">{emp.id}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-hr-black font-medium">{emp.job_role}</div>
                  <div className="text-xs text-gray-500">{emp.department}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-hr-black font-medium">{emp.tenure_years} yrs</div>
                </td>
                <td className="px-6 py-4">
                  <Badge variant={emp.attrition === 'Yes' ? 'warning' : 'success'}>
                    {emp.attrition === 'Yes' ? 'At Risk' : 'Active'}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="p-2 text-gray-400 hover:text-hr-black hover:bg-white rounded-full transition-all group-hover:shadow-sm">
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data && (
          <div className="px-6 py-3 bg-gray-50 border-t border-hr-border flex justify-between items-center">
            <span className="text-[10px] text-gray-400 uppercase tracking-widest">Showing {data.employees?.length || 0} of {data.total || 0} records</span>
          </div>
        )}
      </Card>

      {/* ── Add Employee Modal ── */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-hr-black/40 backdrop-blur-sm" onClick={() => setIsAddModalOpen(false)} />
          <Card className="relative w-full max-w-lg p-8 shadow-2xl">
            <div className="flex justify-between items-center mb-8">
              <h3 className="font-serif text-2xl text-hr-black">Onboard New Talent</h3>
              <button onClick={() => setIsAddModalOpen(false)} className="text-gray-400 hover:text-hr-black"><X className="w-6 h-6" /></button>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div className="col-span-2">
                <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Full Name</label>
                <input type="text" className="input-field" placeholder="e.g. Priya Sharma" value={newEmp.name} onChange={e => setNewEmp({...newEmp, name: e.target.value})} />
              </div>
              <div>
                <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Department</label>
                <select className="input-field" value={newEmp.department} onChange={e => setNewEmp({...newEmp, department: e.target.value})}>
                  {['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations'].map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Role</label>
                <input type="text" className="input-field" placeholder="Software Engineer" value={newEmp.job_role} onChange={e => setNewEmp({...newEmp, job_role: e.target.value})} />
              </div>
              <div>
                <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Salary ($)</label>
                <input type="number" className="input-field" value={newEmp.salary} onChange={e => setNewEmp({...newEmp, salary: parseInt(e.target.value) || 0})} />
              </div>
              <div>
                <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Age</label>
                <input type="number" className="input-field" value={newEmp.age} onChange={e => setNewEmp({...newEmp, age: parseInt(e.target.value) || 22})} />
              </div>
            </div>

            <div className="mt-10 flex space-x-3">
              <button onClick={() => setIsAddModalOpen(false)} className="flex-1 px-6 py-3 text-sm font-medium text-gray-500 border border-hr-border rounded-sm hover:bg-gray-50 transition-colors uppercase tracking-widest">Cancel</button>
              <button 
                onClick={() => createMutation.mutate(newEmp)}
                disabled={!newEmp.name || createMutation.isPending}
                className="flex-1 bg-hr-black text-white px-6 py-3 rounded-sm hover:bg-gray-800 transition-all font-medium text-sm flex items-center justify-center space-x-2 uppercase tracking-widest shadow-lg active:scale-95 disabled:opacity-50"
              >
                {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin text-hr-gold" /> : <CheckCircle2 className="w-4 h-4 text-hr-gold" />}
                <span>{createMutation.isPending ? 'Processing...' : 'Confirm Hire'}</span>
              </button>
            </div>
          </Card>
        </div>
      )}

      {/* ── Slide-over Dossier ── */}
      <div className={`fixed inset-y-0 right-0 w-full md:w-[480px] bg-white shadow-2xl z-50 transform transition-transform duration-500 ease-in-out border-l border-hr-border flex flex-col ${selectedEmployee ? 'translate-x-0' : 'translate-x-full'}`}>
        {selectedEmployee && (
          <>
            <div className="p-8 bg-hr-black text-white">
              <div className="flex justify-between items-start mb-6">
                <div className="w-16 h-16 bg-hr-gold text-hr-black rounded-full flex items-center justify-center font-serif text-2xl shadow-lg">
                  {selectedEmployee.name.split(' ').map(n => n[0]).join('')}
                </div>
                <button onClick={() => setSelectedEmployee(null)} className="text-gray-400 hover:text-white"><X className="w-6 h-6" /></button>
              </div>
              <h2 className="font-serif text-3xl mb-1">{selectedEmployee.name}</h2>
              <p className="text-hr-gold text-[10px] uppercase font-bold tracking-[0.3em]">{selectedEmployee.id} · {selectedEmployee.job_role}</p>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-10">
              {/* Personal */}
              <section className="space-y-4">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-500 flex items-center space-x-2">
                  <User className="w-3 h-3" /><span>Personal Details</span>
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-sm border border-hr-border">
                    <div className="text-[10px] text-gray-400 uppercase font-semibold mb-1">Age / Gender</div>
                    <div className="text-sm font-medium">{selectedEmployee.age} · {selectedEmployee.gender}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-sm border border-hr-border">
                    <div className="text-[10px] text-gray-400 uppercase font-semibold mb-1">Tenure</div>
                    <div className="text-sm font-medium">{selectedEmployee.tenure_years} Years</div>
                  </div>
                </div>
              </section>

              {/* Compensation */}
              <section className="space-y-4">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-500 flex items-center space-x-2">
                  <Briefcase className="w-3 h-3" /><span>Compensation</span>
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500 font-medium">Annual Salary</span>
                    <span className="font-bold text-hr-black">${selectedEmployee.salary.toLocaleString()}</span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-hr-black transition-all duration-700" style={{ width: `${Math.min((selectedEmployee.salary / 150000) * 100, 100)}%` }} />
                  </div>
                </div>
              </section>

              {/* Attrition Risk */}
              <section className="space-y-4">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-500 flex items-center space-x-2">
                  <AlertTriangle className="w-3 h-3" /><span>Attrition Risk Analysis</span>
                </h3>
                {isRiskLoading ? (
                  <div className="flex items-center space-x-3 text-xs text-gray-400 italic p-4">
                    <Loader2 className="w-4 h-4 animate-spin text-hr-gold" /><span>Running risk model...</span>
                  </div>
                ) : riskData && (
                  <div className="p-4 bg-gray-50 rounded-sm border border-hr-border space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-hr-black">Risk Level</span>
                      <Badge variant={riskData.risk_level === 'High' ? 'danger' : riskData.risk_level === 'Medium' ? 'warning' : 'success'}>
                        {riskData.risk_level} — {riskData.risk_percentage}%
                      </Badge>
                    </div>
                    {riskData.contributing_factors?.length > 0 && (
                      <div className="space-y-1 pt-2 border-t border-hr-border">
                        {riskData.contributing_factors.map((f: string, i: number) => (
                          <div key={i} className="text-xs text-gray-600 flex items-center space-x-2">
                            <div className="w-1 h-1 bg-gray-400 rounded-full" />
                            <span>{f}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    <p className="text-[10px] text-gray-400 italic pt-1">{riskData.recommendation}</p>
                  </div>
                )}
              </section>

              {/* ML Performance Predictor */}
              <section className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-[10px] font-bold uppercase tracking-widest text-hr-gold flex items-center space-x-2">
                    <TrendingUp className="w-3 h-3" /><span>ML Performance Predictor</span>
                  </h3>
                  <div className="flex items-center space-x-1">
                    {[1,2,3,4].map(star => (
                      <div key={star} className={`w-2 h-2 rounded-full ${star <= selectedEmployee.performance_rating ? 'bg-hr-gold' : 'bg-gray-200'}`} />
                    ))}
                  </div>
                </div>
                
                <div className="p-6 bg-hr-black rounded-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-3 opacity-10">
                    <TrendingUp className="w-12 h-12 text-hr-gold" />
                  </div>
                  {isPerfLoading ? (
                    <div className="flex items-center space-x-3 text-gray-500 text-xs italic py-4">
                      <Loader2 className="w-4 h-4 animate-spin text-hr-gold" />
                      <span>Running predictive simulation...</span>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-300 leading-relaxed font-light">
                      {performance?.performance_summary}
                    </p>
                  )}
                </div>
              </section>

              {/* Location */}
              <section className="space-y-4">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-500 flex items-center space-x-2">
                  <MapPin className="w-3 h-3" /><span>Assignment</span>
                </h3>
                <p className="text-sm font-medium text-hr-black">{selectedEmployee.department} Division · Primary Zone</p>
              </section>
            </div>

            <div className="p-8 border-t border-hr-border bg-gray-50">
              <button className="btn-primary w-full shadow-lg">Schedule Strategy Meeting</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
