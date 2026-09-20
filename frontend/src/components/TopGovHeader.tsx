import React from 'react';
import { Globe, PhoneCall } from 'lucide-react';

export const TopGovHeader: React.FC = () => {
  return (
    <div className="bg-slate-900 text-slate-200 text-xs border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1.5 flex flex-wrap items-center justify-between gap-2">
        {/* Left Official Info */}
        <div className="flex items-center gap-3">
          <img src="/logo.jpg" alt="Aapnu Parivar Seal" className="w-5 h-5 rounded-full object-contain bg-white p-0.5 border border-slate-700" />
          <span className="font-semibold text-slate-300 flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-saffron"></span>
            Government of Gujarat | ગુજરાત સરકાર
          </span>
          <span className="text-slate-600 hidden sm:inline">|</span>
          <span className="text-slate-400 hidden sm:inline font-mono">
            Family ID & Beneficiary Portal
          </span>
        </div>

        {/* Right Accessibility & Options */}
        <div className="flex items-center gap-4 text-slate-300">
          <div className="flex items-center gap-1">
            <PhoneCall className="w-3.5 h-3.5 text-saffron" />
            <span>Toll-Free Helpline: <strong>1800-233-5500</strong></span>
          </div>

          <span className="text-slate-600">|</span>

          <div className="flex items-center gap-1 cursor-pointer">
            <Globe className="w-3.5 h-3.5 text-blue-400" />
            <select className="bg-slate-800 text-slate-100 border border-slate-700 rounded px-1.5 py-0.5 text-xs focus:outline-none cursor-pointer font-medium">
              <option value="en" className="bg-slate-900 text-slate-100">English</option>
              <option value="gu" className="bg-slate-900 text-slate-100">ગુજરાતી (Gujarati)</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};
