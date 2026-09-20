import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchHealthCheck } from '../api/client';
import { useAuth, isOfficerRole } from '../context/AuthContext';
import {
  UserPlus, CheckCircle2, AlertCircle, RefreshCw, Server, ArrowRight,
  LogIn, Building2, BarChart2, Users, Layers
} from 'lucide-react';

export const CitizenHome: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  const isOfficer = isAuthenticated && user && isOfficerRole(user.role);
  const isCitizen = isAuthenticated && user && !isOfficer;

  const { data: health, isLoading, isError, refetch } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealthCheck,
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-8 py-6">
      
      {/* Logged In Citizen Welcome Banner */}
      {isCitizen && (
        <section className="gov-card p-6 bg-gradient-to-r from-slate-900 to-slate-800 text-white space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Citizen Portal Logged In
                </span>
                <span className="text-xs text-amber-300 font-mono font-extrabold bg-slate-900 px-2.5 py-0.5 rounded border border-amber-500/40">
                  Family ID: {user?.family_id || 'GJ-07-26-4831927-1'}
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-white">Welcome to Your Household Portal</h2>
              <p className="text-xs text-slate-300">
                Manage household family members, review document certificates, evaluate scheme entitlements, and track live applications.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2 shrink-0">
              <Link
                to="/my-family"
                className="px-4 py-2.5 rounded bg-saffron hover:bg-saffron-dark text-white font-bold text-xs shadow-sm flex items-center justify-center gap-2 transition-colors"
              >
                <Users className="w-4 h-4" />
                <span>Go to My Household</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/my-family?action=split"
                className="px-4 py-2.5 rounded bg-slate-700 hover:bg-slate-600 text-white font-bold text-xs shadow-sm flex items-center justify-center gap-2 transition-colors border border-slate-600"
              >
                <Layers className="w-4 h-4 text-amber-400" />
                <span>Split Household</span>
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Logged In Officer Welcome Banner */}
      {isOfficer && (
        <section className="gov-card p-6 bg-slate-900 text-white space-y-3 border-t-4 border-saffron">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Department Officer Session
                </span>
                <span className="text-xs text-slate-300 font-mono">{user?.login_id}</span>
              </div>
              <h2 className="text-xl font-extrabold text-white">Departmental Verification & Administrative Portal</h2>
              <p className="text-xs text-slate-300">
                Process citizen certificate verifications, eligibility overrides, household split anomaly scores, and DBT simulations.
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Link
                to="/officer"
                className="px-4 py-2 rounded bg-gov-blue hover:bg-gov-hover text-white font-bold text-xs flex items-center gap-1.5 transition-colors"
              >
                <Building2 className="w-4 h-4 text-saffron" />
                <span>Departmental Console</span>
              </Link>
              <Link
                to="/analytics"
                className="px-4 py-2 rounded bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs flex items-center gap-1.5 transition-colors"
              >
                <BarChart2 className="w-4 h-4" />
                <span>Statewide Analytics</span>
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Official State Hero Banner */}
      <section className="gov-card overflow-hidden bg-white border border-slate-200">
        <div className="gov-tricolor-stripe"></div>
        <div className="p-6 sm:p-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 text-slate-800 text-xs font-semibold border border-slate-200">
              <img src="/logo.jpg" alt="Logo" className="w-4 h-4 rounded-full object-contain" />
              <span>Gujarat State Household Identity & Welfare Beneficiary Gateway</span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-gov-navy tracking-tight leading-tight">
              One Family. One ID. Every Welfare Benefit.
            </h1>

            <p className="text-slate-600 text-base leading-relaxed">
              <strong>Aapnu Parivar (આપણું પરિવાર)</strong> provides single-window entitlement access across Gujarat State and Central Government welfare schemes with automated eligibility rules and zero redundant paperwork.
            </p>

            {/* Main Action CTAs */}
            <div className="pt-2 flex flex-wrap items-center gap-3">
              {!isAuthenticated && (
                <Link
                  to="/login"
                  className="px-5 py-2.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-extrabold text-sm shadow-md transition-all flex items-center justify-center gap-2 h-[42px] shrink-0"
                >
                  <LogIn className="w-4 h-4 text-amber-400" />
                  <span>Sign In to Portal</span>
                </Link>
              )}

              <Link
                to="/register"
                className="px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-sm shadow-md transition-all flex items-center justify-center gap-2 h-[42px] shrink-0"
              >
                <UserPlus className="w-4 h-4 text-amber-400" />
                <span>New Registration</span>
              </Link>

              <Link
                to="/schemes"
                className="px-5 py-2.5 rounded-lg bg-white border-2 border-slate-900 text-slate-900 hover:bg-slate-100 font-extrabold text-sm shadow-xs transition-all flex items-center justify-center gap-2 h-[42px] shrink-0"
              >
                <Layers className="w-4 h-4 text-slate-900" />
                <span>Explore Schemes</span>
              </Link>
            </div>
          </div>

          {/* Right Logo Display Card */}
          <div className="hidden lg:block shrink-0">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-2xl shadow-md text-center space-y-2">
              <img
                src="/logo.jpg"
                alt="Aapnu Parivar State Emblem"
                className="w-44 h-44 object-contain mx-auto rounded-xl bg-white p-1"
              />
              <span className="text-[11px] font-bold text-gov-navy uppercase tracking-wider block">
                Official Gujarat State Registry
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* System Infrastructure Status Section */}
      <section className="gov-card">
        <div className="gov-card-header flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-gov-navy" />
            <h2 className="text-base font-bold text-gov-navy">Platform Infrastructure & Service Status</h2>
          </div>

          <button
            onClick={() => refetch()}
            className="p-1.5 rounded bg-white border border-slate-200 text-slate-600 hover:text-gov-navy hover:bg-slate-50 transition-colors text-xs flex items-center gap-1.5 font-medium"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-gov-blue' : ''}`} />
            <span>Refresh Status</span>
          </button>
        </div>

        <div className="p-5">
          {isLoading ? (
            <div className="p-4 rounded bg-slate-50 border border-slate-200 text-slate-600 text-sm flex items-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-gov-blue" />
              <span>Checking backend server connectivity...</span>
            </div>
          ) : isError ? (
            <div className="p-4 rounded bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
              <div>
                <p className="font-semibold">Backend Gateway Disconnected</p>
                <p className="text-xs text-red-600">FastAPI API server not responding at <code>http://127.0.0.1:8000</code>.</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-sm">
              <div className="p-3.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium block">API Gateway</span>
                <div className="flex items-center gap-1.5 mt-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span className="font-bold text-slate-900 uppercase text-xs">{health?.status} (v{health?.version})</span>
                </div>
              </div>

              <div className="p-3.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium block">Database Layer</span>
                <div className="flex items-center gap-1.5 mt-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span className="font-bold text-slate-900 capitalize text-xs">{health?.database}</span>
                </div>
              </div>

              <div className="p-3.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium block">Environment</span>
                <span className="font-semibold text-slate-800 text-xs mt-1 block capitalize">{health?.environment}</span>
              </div>

              <div className="p-3.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium block">Data Classification</span>
                <span className="font-semibold text-amber-800 text-xs mt-1 block">Synthetic Gujarat Registry</span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Core Objectives Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="gov-card p-6 space-y-3">
          <div className="w-9 h-9 rounded bg-blue-50 text-gov-blue font-bold flex items-center justify-center text-sm border border-blue-100">
            01
          </div>
          <h3 className="text-base font-bold text-gov-navy">Unified Family Identity</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Permanent 12-digit Family ID with Verhoeff check-digit protection, linking verified household members to single active memberships.
          </p>
        </div>

        <div className="gov-card p-6 space-y-3">
          <div className="w-9 h-9 rounded bg-amber-50 text-amber-800 font-bold flex items-center justify-center text-sm border border-amber-100">
            02
          </div>
          <h3 className="text-base font-bold text-gov-navy">Automated Rules Engine</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Evaluation of scheme requirements based on verified income bands, land holdings, social categories, and document status.
          </p>
        </div>

        <div className="gov-card p-6 space-y-3">
          <div className="w-9 h-9 rounded bg-emerald-50 text-emerald-800 font-bold flex items-center justify-center text-sm border border-emerald-100">
            03
          </div>
          <h3 className="text-base font-bold text-gov-navy">Lifecycle & Lineage</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Append-only tracking of birth, death, and household splits with automated risk scoring and officer confirmation workflows.
          </p>
        </div>
      </section>

    </div>
  );
};
