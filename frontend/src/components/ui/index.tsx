import React from 'react';

export function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`card p-6 ${className}`}>{children}</div>;
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="mb-8 flex items-start justify-between">
      <div>
        <h2 className="text-3xl font-serif text-hr-black mb-1">{title}</h2>
        {subtitle && <p className="text-sm text-gray-500 tracking-wide">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export function Badge({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'default' | 'success' | 'warning' | 'danger' }) {
  const styles = {
    default: 'bg-gray-50 text-gray-700 border-gray-200',
    success: 'bg-green-50 text-green-700 border-green-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger:  'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <span className={`inline-flex px-2.5 py-0.5 text-[10px] tracking-wider uppercase font-semibold border rounded-sm ${styles[variant]}`}>
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const isHighRisk = status.toLowerCase() === 'high' || status.toLowerCase() === 'high risk';
  const isMedRisk = status.toLowerCase() === 'medium' || status.toLowerCase() === 'moderate';

  return (
    <span
      className={`px-2 py-1 text-[10px] tracking-wider uppercase font-medium border ${
        isHighRisk
          ? 'bg-red-50 text-red-700 border-red-200'
          : isMedRisk
          ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
          : 'bg-green-50 text-green-700 border-green-200'
      }`}
    >
      {status}
    </span>
  );
}

export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-4">
      <div className="w-8 h-8 border-2 border-hr-border border-t-hr-gold rounded-full animate-spin"></div>
      <p className="text-xs tracking-widest text-gray-400 uppercase">Synchronizing...</p>
    </div>
  );
}
