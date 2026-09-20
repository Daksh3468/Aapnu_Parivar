import React, { useState } from 'react';
import { ShieldCheck, Lock, CheckCircle2, AlertCircle, RefreshCw, KeyRound, X } from 'lucide-react';
import { DemoOtpBanner } from './DemoOtpBanner';

interface VerifyMemberModalProps {
  personId: string;
  memberName: string;
  onClose: () => void;
  onSuccess: () => void;
}

export const VerifyMemberModal: React.FC<VerifyMemberModalProps> = ({
  personId,
  memberName,
  onClose,
  onSuccess,
}) => {
  const [step, setStep] = useState<'AADHAAR' | 'OTP'>('AADHAAR');
  const [aadhaarNumber, setAadhaarNumber] = useState('123456789012');
  const [otpCode, setOtpCode] = useState('');
  const [demoOtp, setDemoOtp] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartEkyc = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`/api/v1/members/${personId}/verify/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ aadhaar_number: aadhaarNumber }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'e-KYC request failed');

      if (data.demo_otp) {
        setDemoOtp(data.demo_otp);
        setOtpCode(data.demo_otp); // Auto-fill demo OTP
      }
      setStep('OTP');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmEkyc = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`/api/v1/members/${personId}/verify/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ aadhaar_number: aadhaarNumber, otp_code: otpCode }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Verification confirmation failed');

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm">
      <div className="bg-white border border-slate-200 rounded-lg max-w-md w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-150 relative">
        
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center space-y-1">
          <div className="w-10 h-10 rounded-full bg-blue-50 text-gov-blue mx-auto flex items-center justify-center border border-blue-100">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-gov-navy">Aadhaar e-KYC Identity Verification</h2>
          <p className="text-xs text-slate-500">Member: <strong>{memberName}</strong></p>
        </div>

        {demoOtp && step === 'OTP' && (
          <DemoOtpBanner otpCode={demoOtp} mobile="Aadhaar Registered Mobile" />
        )}

        {error && (
          <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        {step === 'AADHAAR' ? (
          <form onSubmit={handleStartEkyc} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-gov-navy uppercase tracking-wider mb-1">
                Aadhaar Number (12 અંકનો આધાર કાર્ડ નંબર)
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={aadhaarNumber}
                  onChange={(e) => setAadhaarNumber(e.target.value)}
                  placeholder="Enter 12-digit Aadhaar..."
                  maxLength={12}
                  required
                  className="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded text-sm text-slate-900 font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-gov-blue"
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              </div>
              <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                <Lock className="w-3 h-3 text-emerald-600" />
                <span>Full Aadhaar is NEVER stored. Only HMAC-SHA-256 hash is kept.</span>
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded bg-gov-blue hover:bg-gov-hover text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2 shadow-sm"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
              <span>Send e-KYC OTP</span>
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirmEkyc} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-gov-navy uppercase tracking-wider mb-1">
                Enter 6-Digit e-KYC OTP Code
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  placeholder="Enter 6-digit OTP..."
                  maxLength={6}
                  required
                  className="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded text-sm text-slate-900 font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-gov-blue"
                />
                <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setStep('AADHAAR')}
                className="w-1/3 py-2.5 rounded bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-semibold"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading}
                className="w-2/3 py-2.5 rounded bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-1 shadow-sm"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                <span>Confirm & Verify Member</span>
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
};
