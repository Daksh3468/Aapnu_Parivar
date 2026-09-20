import React from 'react';
import { Lock } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t-4 border-saffron mt-auto text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Aapnu Parivar Logo" className="w-10 h-10 rounded-lg object-contain bg-white p-0.5 border border-slate-700 shadow-xs" />
            <div>
              <p className="font-bold text-sm text-white">Aapnu Parivar Portal (આપણું પરિવાર)</p>
              <p className="text-slate-400">Department of Social Justice and Empowerment, Government of Gujarat</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-slate-400">
            <span className="flex items-center gap-1.5 bg-slate-800 px-3 py-1.5 rounded border border-slate-700 text-emerald-400 font-medium">
              <Lock className="w-3.5 h-3.5" /> 100% Synthetic Demo Environment
            </span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-400">
          <p>© 2026 Government of Gujarat. Designed for State Welfare Beneficiary Management.</p>
          <div className="flex items-center gap-4 font-medium">
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <span>•</span>
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <span>•</span>
            <a href="#" className="hover:text-white transition-colors">Accessibility Statement</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
