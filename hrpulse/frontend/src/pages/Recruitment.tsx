import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, Plus, Trash2, FileText, CheckCircle, Loader2 } from 'lucide-react';
import api from '../api/client';
import { Card, PageHeader, LoadingSpinner } from '../components/ui';

export function Recruitment() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'jobs' | 'candidates'>('jobs');
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string>('');

  // Fetch Jobs
  const { data: jobs, isLoading: isJobsLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const res = await api.get('/recruitment/jobs');
      return res.data;
    },
  });

  // Fetch Candidates
  const { data: candidates, isLoading: isCandidatesLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: async () => {
      const res = await api.get('/recruitment/candidates');
      return res.data;
    },
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader 
        title="Recruitment Portal" 
        subtitle="Manage open roles and evaluate incoming talent with AI-assisted resume screening."
      />

      <div className="flex space-x-1 border-b border-hr-border mb-6">
        <button 
          onClick={() => setActiveTab('jobs')}
          className={`px-6 py-3 text-sm font-medium transition-all ${activeTab === 'jobs' ? 'border-b-2 border-hr-gold text-hr-black' : 'text-gray-500 hover:text-hr-black'}`}
        >
          Active Job Roles
        </button>
        <button 
          onClick={() => setActiveTab('candidates')}
          className={`px-6 py-3 text-sm font-medium transition-all ${activeTab === 'candidates' ? 'border-b-2 border-hr-gold text-hr-black' : 'text-gray-500 hover:text-hr-black'}`}
        >
          Candidate Pipeline
        </button>
      </div>

      {activeTab === 'jobs' ? (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-serif">Open Positions</h3>
            <button 
              onClick={() => setIsJobModalOpen(true)}
              className="btn-primary flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" /> Post New Job
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {isJobsLoading ? (
              <LoadingSpinner />
            ) : jobs?.length === 0 ? (
              <p className="text-gray-500 italic text-sm col-span-2 py-12 text-center border-2 border-dashed border-hr-border rounded-lg">No active job roles. Start by posting a new one.</p>
            ) : (
              jobs?.map((job: any) => (
                <JobCard 
                  key={job.id} 
                  job={job} 
                  onUploadClick={() => {
                    setSelectedJobId(job.id);
                    setIsUploadModalOpen(true);
                  }}
                  onDelete={() => queryClient.invalidateQueries({ queryKey: ['jobs'] })}
                />
              ))
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <h3 className="text-lg font-serif">Applicants & AI Evaluations</h3>
          <Card className="p-0 overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-hr-surface border-b border-hr-border text-xs uppercase tracking-widest text-gray-500">
                  <th className="px-6 py-4 font-medium">Candidate</th>
                  <th className="px-6 py-4 font-medium">Job ID</th>
                  <th className="px-6 py-4 font-medium">Exp</th>
                  <th className="px-6 py-4 font-medium">AI Recommendation</th>
                  <th className="px-6 py-4 text-right font-medium">Applied</th>
                </tr>
              </thead>
              <tbody>
                {isCandidatesLoading ? (
                  <tr><td colSpan={5} className="p-8 text-center"><LoadingSpinner /></td></tr>
                ) : candidates?.length === 0 ? (
                  <tr><td colSpan={5} className="px-6 py-12 text-center text-gray-500 text-sm">No applications received yet.</td></tr>
                ) : (
                  candidates?.map((cand: any) => (
                    <tr key={cand.id} className="border-b border-hr-border hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center text-sm font-serif border border-hr-border mr-4">
                            {cand.name.charAt(0)}
                          </div>
                          <div className="font-medium text-sm">{cand.name}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-xs font-mono text-gray-500">{cand.job_id?.substring(0, 8)}...</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{cand.experience_years}y</td>
                      <td className="px-6 py-4">
                        <div className="max-w-xs">
                          <p className="text-xs italic text-gray-700 leading-tight">"{cand.ai_evaluation}"</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right text-xs text-gray-400">
                        {new Date(cand.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* Post Job Modal */}
      {isJobModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <Card className="max-w-lg w-full p-8 space-y-6 animate-scale-in shadow-2xl">
            <h2 className="text-2xl font-serif">Post New Role</h2>
            <JobForm onClose={() => setIsJobModalOpen(false)} onSuccess={() => {
              setIsJobModalOpen(false);
              queryClient.invalidateQueries({ queryKey: ['jobs'] });
            }} />
          </Card>
        </div>
      )}

      {/* Resume Upload Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <Card className="max-w-md w-full p-8 space-y-6 animate-scale-in shadow-2xl">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-serif">Upload Resume</h2>
              <button onClick={() => setIsUploadModalOpen(false)} className="text-gray-400 hover:text-black">
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
            <UploadForm 
              jobId={selectedJobId} 
              onClose={() => setIsUploadModalOpen(false)} 
              onSuccess={() => {
                setIsUploadModalOpen(false);
                setActiveTab('candidates');
                queryClient.invalidateQueries({ queryKey: ['candidates'] });
              }} 
            />
          </Card>
        </div>
      )}
    </div>
  );
}

function JobCard({ job, onUploadClick, onDelete }: { job: any, onUploadClick: () => void, onDelete: () => void }) {
  const mutation = useMutation({
    mutationFn: async () => api.delete(`/recruitment/jobs/${job.id}`),
    onSuccess: onDelete,
  });

  return (
    <Card className="p-6 border border-hr-border hover:border-hr-gold transition-all group flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <span className="text-[10px] tracking-[0.2em] font-sans uppercase text-hr-gold bg-gold/5 px-2 py-1 rounded">Active Role</span>
          <button onClick={() => mutation.mutate()} className="text-gray-300 hover:text-red-500 transition-colors">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
        <h4 className="text-xl font-serif mb-1">{job.title}</h4>
        <p className="text-xs text-gray-500 uppercase tracking-widest mb-6">{job.department}</p>
        
        <div className="space-y-4 mb-8">
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-2 font-semibold">Priority Questions</p>
            <ul className="space-y-2">
              {(job.interview_questions ? JSON.parse(job.interview_questions) : ['General role inquiry']).slice(0, 2).map((q: string, i: number) => (
                <li key={i} className="text-xs text-gray-600 flex items-start italic">
                  <CheckCircle className="w-3 h-3 mr-2 mt-0.5 text-hr-gold shrink-0" />
                  "{q}"
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      
      <button 
        onClick={onUploadClick}
        className="w-full mt-auto btn-secondary border-dashed border-gray-300 group-hover:border-hr-gold transition-all flex items-center justify-center text-xs uppercase tracking-widest py-3"
      >
        <Upload className="w-3 h-3 mr-2" /> Upload Applicant Resume
      </button>
    </Card>
  );
}

function JobForm({ onClose, onSuccess }: { onClose: () => void, onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    required_skills: '',
    interview_questions: '',
    description: ''
  });

  const mutation = useMutation({
    mutationFn: (data: any) => api.post('/recruitment/jobs', {
      ...data,
      required_skills: JSON.stringify(data.required_skills.split(',').map((s: string) => s.trim())),
      interview_questions: JSON.stringify(data.interview_questions.split('\n').filter((q: string) => q.trim() !== ''))
    }),
    onSuccess,
  });

  return (
    <div className="space-y-4">
      <div>
        <label className="text-[10px] text-gray-400 uppercase tracking-widest mb-1 block">Job Title</label>
        <input 
          type="text" 
          value={formData.title}
          onChange={e => setFormData({...formData, title: e.target.value})}
          className="input-field w-full" 
          placeholder="e.g. Senior Software Engineer" 
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-[10px] text-gray-400 uppercase tracking-widest mb-1 block">Department</label>
          <input 
            type="text" 
            value={formData.department}
            onChange={e => setFormData({...formData, department: e.target.value})}
            className="input-field w-full" 
            placeholder="Engineering" 
          />
        </div>
        <div>
          <label className="text-[10px] text-gray-400 uppercase tracking-widest mb-1 block">Skills (Comma Seperated)</label>
          <input 
            type="text" 
            value={formData.required_skills}
            onChange={e => setFormData({...formData, required_skills: e.target.value})}
            className="input-field w-full" 
            placeholder="React, Python, AWS" 
          />
        </div>
      </div>
      <div>
        <label className="text-[10px] text-gray-400 uppercase tracking-widest mb-1 block">Interview Questions (One per line)</label>
        <textarea 
          rows={3}
          value={formData.interview_questions}
          onChange={e => setFormData({...formData, interview_questions: e.target.value})}
          className="input-field w-full" 
          placeholder="What is your largest project experience?" 
        />
      </div>
      <div className="flex space-x-4 pt-4">
        <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
        <button 
          onClick={() => mutation.mutate(formData)} 
          disabled={mutation.isPending}
          className="btn-primary flex-1 flex items-center justify-center"
        >
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Role'}
        </button>
      </div>
    </div>
  );
}

function UploadForm({ jobId, onClose, onSuccess }: { jobId: string, onClose: () => void, onSuccess: () => void }) {
  const [name, setName] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const mutation = useMutation({
    mutationFn: (formData: FormData) => api.post('/recruitment/candidates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess,
  });

  const handleSubmit = () => {
    if (!name || !file) return;
    const formData = new FormData();
    formData.append('name', name);
    formData.append('job_id', jobId);
    formData.append('resume', file);
    mutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div className="relative p-8 bg-hr-surface border border-dashed border-hr-border rounded flex items-center justify-center flex-col space-y-3 hover:border-hr-gold transition-colors group cursor-pointer overflow-hidden">
        <Upload className="w-10 h-10 text-hr-gold mb-2 group-hover:scale-110 transition-transform" />
        <p className="text-sm font-medium text-hr-black">Drop resume here or click to browse</p>
        <p className="text-[10px] text-gray-400 uppercase tracking-widest font-semibold">Supports PDF, DOCX, TXT</p>
        <input 
          type="file" 
          className="absolute inset-0 opacity-0 cursor-pointer z-10" 
          onChange={e => setFile(e.target.files?.[0] || null)}
        />
        {file && (
          <div className="mt-4 p-2 bg-hr-white border border-hr-gold/30 rounded flex items-center shadow-sm animate-fade-in relative z-20">
            <FileText className="w-4 h-4 text-hr-gold mr-2" />
            <span className="text-xs font-semibold text-hr-black truncate max-w-[200px]">{file.name}</span>
          </div>
        )}
      </div>
      
      <div>
        <label className="text-[10px] text-gray-400 uppercase tracking-widest mb-1 block">Full Applicant Name</label>
        <input 
          type="text" 
          value={name}
          onChange={e => setName(e.target.value)}
          className="input-field w-full" 
          placeholder="John Doe" 
        />
      </div>

      <div className="flex space-x-4 pt-2">
        <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
        <button 
          onClick={handleSubmit} 
          disabled={mutation.isPending || !name || !file}
          className="btn-primary flex-1 flex items-center justify-center"
        >
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Start Evaluation'}
        </button>
      </div>
      
      {mutation.isPending && (
        <p className="text-[10px] text-center text-hr-gold animate-pulse tracking-widest uppercase">AI is analyzing candidate fit...</p>
      )}
    </div>
  );
}
