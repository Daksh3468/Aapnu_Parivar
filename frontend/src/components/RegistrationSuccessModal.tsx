import React, { useState } from 'react';
import { CheckCircle2, Copy, Check, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface RegistrationSuccessModalProps {
  familyId: string;
  headName: string;
  memberCount: number;
  onClose: () => void;
}

export const RegistrationSuccessModal: React.FC<RegistrationSuccessModalProps> = ({
  familyId,
  headName,
  memberCount,
  onClose,
}) => {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(familyId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm">
      <div className="bg-white border border-slate-200 rounded-lg max-w-lg w-full p-6 shadow-2xl space-y-6 animate-in fade-in zoom-in-95 duration-150">
        
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-gov-navy">Registration Successfully Submitted!</h2>
          <p className="text-xs text-slate-500">Gujarat Family Identity Record Created in State Registry</p>
        </div>

        {/* Issued Family ID Banner */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-md text-center space-y-2">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Issued 12-Digit Family ID (તમારો ફેમિલી આઈડી)
          </span>
          
          <div className="flex items-center justify-center gap-3">
            <span className="font-mono font-extrabold text-2xl text-gov-navy tracking-widest">{familyId}</span>
            <button
              onClick={handleCopy}
              className="p-2 rounded bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 transition-colors"
              title="Copy Family ID"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Household Summary */}
        <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-3 rounded border border-slate-200">
          <div>
            <span className="text-slate-500 block">Family Head:</span>
            <strong className="text-slate-900">{headName}</strong>
          </div>
          <div>
            <span className="text-slate-500 block">Total Household Members:</span>
            <strong className="text-slate-900">{memberCount} Person(s)</strong>
          </div>
        </div>

        <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-100">
          <button
            onClick={() => { onClose(); navigate('/'); }}
            className="w-full py-2.5 rounded bg-gov-blue hover:bg-gov-hover text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2 shadow-sm"
          >
            <span>Proceed to Citizen Home</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
