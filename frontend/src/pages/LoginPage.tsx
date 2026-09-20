import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth, isOfficerRole } from '../context/AuthContext';
import { UserCheck, Lock, AlertCircle, RefreshCw, Building2, User, Mail, ShieldCheck } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loginToken } = useAuth();

  // Unified Single Field Login State
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const roleParam = searchParams.get('role') || searchParams.get('mode');
    if (roleParam === 'officer') {
      setLoginId('admin@gujarat.gov.in');
      setPassword('');
    }
  }, [searchParams]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          login_id: loginId.trim(),
          password: password,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed');

      const role = data.role || 'CITIZEN';
      const isOfficer = isOfficerRole(role);

      loginToken(data.access_token, data.refresh_token, {
        user_id: data.user_id,
        login_id: loginId.trim(),
        role: role,
        status: 'ACTIVE',
        person_id: data.person_id,
        family_id: data.family_id,
      });

      // Smart Auto-Routing based on detected role
      if (isOfficer) {
        navigate('/officer');
      } else {
        navigate('/my-family');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const isEmailInput = loginId.includes('@');

  return (
    <div className="max-w-md mx-auto py-10 space-y-6">
      <div className="gov-card p-6 space-y-6">
        
        {/* Header Branding */}
        <div className="text-center space-y-2">
          <img
            src="/logo.jpg"
            alt="Aapnu Parivar Official State Logo"
            className="w-24 h-24 mx-auto rounded-xl object-contain bg-white p-1 shadow-md border border-slate-200"
          />
          <h1 className="text-xl font-extrabold text-gov-navy">Unified State Common Login Portal</h1>
          <p className="text-xs text-slate-500 font-medium">
            Gujarat Household Identity & Entitlements • Citizen & Officer Gateway
          </p>
        </div>

        {/* Input Identifier Type Badge */}
        <div className="p-3 rounded-lg bg-slate-100 border border-slate-200 text-xs flex items-center justify-between">
          <span className="text-slate-600 font-medium">Sign-in Identifier Type:</span>
          {isEmailInput ? (
            <span className="font-extrabold text-gov-navy px-2 py-0.5 rounded bg-amber-100 border border-amber-300 flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5 text-gov-navy" />
              <span>Officer Official Email / Gmail</span>
            </span>
          ) : (
            <span className="font-extrabold text-gov-blue px-2 py-0.5 rounded bg-blue-50 border border-blue-200 flex items-center gap-1">
              <UserCheck className="w-3.5 h-3.5 text-gov-blue" />
              <span>Citizen Mobile Number</span>
            </span>
          )}
        </div>

        {error && (
          <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLoginSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-gov-navy uppercase tracking-wider mb-1">
              Mobile Number OR Official Email / Gmail
            </label>
            <div className="relative">
              <input
                type="text"
                value={loginId}
                onChange={(e) => setLoginId(e.target.value)}
                placeholder="Enter 10-digit mobile or admin@gujarat.gov.in..."
                required
                className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-gov-blue"
              />
              {isEmailInput ? (
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              ) : (
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              )}
            </div>
          </div>

          <div>
            <label className="block font-bold text-gov-navy uppercase tracking-wider mb-1">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password..."
                required
                className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-gov-blue"
              />
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-lg font-extrabold text-sm transition-all flex items-center justify-center gap-2 shadow-md text-white bg-gov-navy hover:bg-slate-800 cursor-pointer"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin text-saffron" /> : <ShieldCheck className="w-4 h-4 text-saffron" />}
            <span>{isEmailInput ? 'Sign In as Department Officer' : 'Sign In to Family Dashboard'}</span>
          </button>
        </form>

      </div>
    </div>
  );
};
