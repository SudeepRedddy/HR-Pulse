import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import api from '../api/client';

export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@hrpulse.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.post('/auth/login', { email, password });
      if (response.data?.access_token) {
        localStorage.setItem('hrpulse_token', response.data.access_token);
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('admin@hrpulse.com');
    setPassword('admin123');
    handleLogin();
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-hr-bg">
      <div className="w-[320px] text-center flex flex-col items-center">
        <h1 className="font-playfair text-[32px] font-normal tracking-tight text-hr-text flex items-baseline">
          HR<span className="font-inter font-light text-[32px] tracking-[-0.02em]">pulse</span>
        </h1>
        <div className="h-[1px] w-[40px] bg-hr-gold mt-2 mb-8"></div>
        
        <div className="w-full flex flex-col gap-4">
          <input 
            type="email" 
            placeholder="Work Email" 
            className="w-full border border-hr-border bg-white px-[14px] py-[10px] text-[14px] font-inter text-hr-text outline-none rounded-[2px] focus:border-hr-gold transition-colors placeholder:text-hr-text-hint"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input 
            type="password" 
            placeholder="Password" 
            className="w-full border border-hr-border bg-white px-[14px] py-[10px] text-[14px] font-inter text-hr-text outline-none rounded-[2px] focus:border-hr-gold transition-colors placeholder:text-hr-text-hint"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          
          {error && <p className="text-hr-danger text-[12px] font-inter">{error}</p>}
          
          <button 
            className="w-full bg-hr-black text-white font-inter font-medium text-[13px] py-[12px] px-[24px] rounded-[4px] mt-2 hover:opacity-85 transition-opacity"
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
          
          <button 
            className="w-full bg-white border border-hr-black text-hr-black font-inter font-medium text-[13px] py-[12px] px-[24px] rounded-[4px] hover:opacity-85 transition-opacity"
            onClick={handleDemoLogin}
          >
            Continue as Demo
          </button>
        </div>
        
        <p className="mt-8 font-inter font-light text-[12px] text-hr-text-hint">
          Secure HR Intelligence Platform
        </p>
      </div>
    </div>
  );
}
