import React from 'react';
import { KeyRound, Info, Copy, Check } from 'lucide-react';

interface DemoOtpBannerProps {
  otpCode: string | null;
  mobile: string;
}

export const DemoOtpBanner: React.FC<DemoOtpBannerProps> = ({ otpCode, mobile }) => {
  const [copied, setCopied] = React.useState(false);

  if (!otpCode) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(otpCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-3.5 bg-amber-50 border border-amber-300 rounded-md text-slate-800 text-xs shadow-sm space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-bold text-amber-900">
          <KeyRound className="w-4 h-4 text-amber-700" />
          <span>DEMO OTP NOTIFICATION BANNER</span>
        </div>
        <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-amber-200 text-amber-900">
          Demo Mode Active
        </span>
      </div>

      <div className="flex items-center justify-between bg-white p-2.5 rounded border border-amber-200">
        <div>
          <span className="text-slate-500 font-medium">OTP Code for {mobile}: </span>
          <span className="font-mono font-bold text-base text-amber-900 tracking-wider ml-2">{otpCode}</span>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          className="px-2.5 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 font-semibold text-xs transition-colors flex items-center gap-1"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-700" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied' : 'Copy Code'}</span>
        </button>
      </div>

      <p className="text-[11px] text-amber-800/80 flex items-center gap-1">
        <Info className="w-3 h-3 text-amber-700 shrink-0" />
        <span>In demo mode, OTP codes are rendered directly for ease of evaluation.</span>
      </p>
    </div>
  );
};
