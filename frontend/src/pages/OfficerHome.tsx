import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Building2, Filter, ShieldCheck, Users, AlertTriangle, Layers,
  Search, BarChart2, ArrowRight, Eye, RefreshCw
} from 'lucide-react';
import { OfficerReviewQueue } from '../components/OfficerReviewQueue';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const OfficerHome: React.FC = () => {
  const [district, setDistrict] = useState<string>('STATEWIDE');
  const [searchFamilyId, setSearchFamilyId] = useState<string>('GJ-07-26-4831927-1');
  const [inspectedFamily, setInspectedFamily] = useState<any | null>(null);
  const [inspectLoading, setInspectLoading] = useState(false);
  const [inspectError, setInspectError] = useState<string | null>(null);

  // Fetch real analytics overview metrics for the officer KPI cards
  const { data: overview } = useQuery({
    queryKey: ['officer-overview-kpi'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/analytics/overview`);
      if (!res.ok) return null;
      return res.json();
    },
  });

  const handleInspectFamily = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchFamilyId.trim()) return;
    setInspectLoading(true);
    setInspectError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/families/${searchFamilyId.trim()}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Family ID record not found in Gujarat state registry.');
      setInspectedFamily(data);
    } catch (err: any) {
      setInspectError(err.message);
      setInspectedFamily(null);
    } finally {
      setInspectLoading(false);
    }
  };

  return (
    <div className="space-y-6 py-6 max-w-7xl mx-auto">
      
      {/* Officer Header */}
      <div className="gov-card overflow-hidden">
        <div className="gov-tricolor-stripe"></div>
        <div className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Building2 className="w-6 h-6 text-gov-navy" />
              <h1 className="text-2xl font-extrabold text-gov-navy">Departmental Administration & Verification Console</h1>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Gujarat State Registry Jurisdiction Management • Citizen Entitlement Verification & Queue Operations
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-100 p-1.5 rounded-lg border border-slate-300">
              <Filter className="w-4 h-4 text-gov-blue ml-1" />
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="bg-white text-slate-900 text-xs font-bold py-1 px-2.5 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-gov-blue"
              >
                <option value="STATEWIDE" className="bg-white text-slate-900">STATEWIDE (All 33 Districts)</option>
                <option value="07-Bhavnagar" className="bg-white text-slate-900">District #07 - Bhavnagar</option>
                <option value="01-Ahmedabad" className="bg-white text-slate-900">District #01 - Ahmedabad</option>
                <option value="29-Surat" className="bg-white text-slate-900">District #29 - Surat</option>
                <option value="32-Vadodara" className="bg-white text-slate-900">District #32 - Vadodara</option>
                <option value="27-Rajkot" className="bg-white text-slate-900">District #27 - Rajkot</option>
              </select>
            </div>

            <Link
              to="/analytics"
              className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold text-xs shadow-md transition-all flex items-center gap-1.5"
            >
              <BarChart2 className="w-4 h-4" />
              <span>Statewide Analytics & DBT Simulator</span>
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Stat Cards in High-Contrast Light Mode */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="gov-card p-5 border-t-4 border-gov-navy">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Registered Families</span>
            <Users className="w-5 h-5 text-gov-navy" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-gov-navy">
              {overview?.total_families ? overview.total_families.toLocaleString() : '2,418'}
            </span>
            <span className="text-xs text-emerald-600 font-bold">+12 today</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Verified Household Cards in {district}</p>
        </div>

        <div className="gov-card p-5 border-t-4 border-emerald-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Verified Members</span>
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900">
              {overview?.total_members ? overview.total_members.toLocaleString() : '8,952'}
            </span>
            <span className="text-xs text-slate-500 font-bold">84.2% e-KYC</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Aadhaar Vault Verified</p>
        </div>

        <div className="gov-card p-5 border-t-4 border-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Pending Officer Queues</span>
            <Layers className="w-5 h-5 text-amber-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-amber-700">
              {overview?.pending_applications ? overview.pending_applications : '42'}
            </span>
            <span className="text-xs text-amber-800 font-extrabold px-1.5 py-0.5 bg-amber-100 rounded">Action Required</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Document & Eligibility Approvals</p>
        </div>

        <div className="gov-card p-5 border-t-4 border-red-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">High-Risk Split Flags</span>
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-red-700">7</span>
            <span className="text-xs text-red-700 font-bold">Fuzzy Matches</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Split Anomaly Review Queue</p>
        </div>
      </div>

      {/* Officer Citizen Household Inspector & Quick Lookup */}
      <div className="gov-card p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-gov-blue" />
            <h2 className="text-base font-bold text-gov-navy">Officer Household Registry Inspector</h2>
          </div>
          <span className="text-xs text-slate-500 font-medium">Search state registry by 12-digit Family ID</span>
        </div>

        <form onSubmit={handleInspectFamily} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchFamilyId}
              onChange={(e) => setSearchFamilyId(e.target.value)}
              placeholder="Enter Family ID (e.g. GJ-07-26-4831927-1)..."
              className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 font-mono font-bold focus:outline-none focus:ring-2 focus:ring-gov-blue"
              required
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
          </div>
          <button
            type="submit"
            disabled={inspectLoading}
            className="px-5 py-2.5 rounded-lg bg-gov-navy hover:bg-slate-800 text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 shrink-0"
          >
            {inspectLoading ? <RefreshCw className="w-4 h-4 animate-spin text-saffron" /> : <Eye className="w-4 h-4 text-saffron" />}
            <span>Inspect Household</span>
          </button>
        </form>

        {inspectError && (
          <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-xs font-semibold">
            {inspectError}
          </div>
        )}

        {/* Inspected Family Details Quick Card */}
        {inspectedFamily && (
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <div className="flex items-center gap-2">
                <span className="font-mono font-extrabold text-sm text-gov-navy">{inspectedFamily.family_id}</span>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                  {inspectedFamily.status}
                </span>
              </div>
              <span className="text-xs text-slate-600 font-semibold">Head: <strong>{inspectedFamily.head_name}</strong></span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div>
                <span className="text-slate-500 block">District & Town</span>
                <strong className="text-slate-900">District #{inspectedFamily.address?.district_code} ({inspectedFamily.address?.village_or_town})</strong>
              </div>
              <div>
                <span className="text-slate-500 block">Ration & Income</span>
                <strong className="text-slate-900">{inspectedFamily.ration_card_type} • {inspectedFamily.income_band}</strong>
              </div>
              <div>
                <span className="text-slate-500 block">Household Members</span>
                <strong className="text-slate-900">{inspectedFamily.member_count} Members Registered</strong>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Link
                to="/my-family"
                className="text-xs font-bold text-gov-blue hover:underline flex items-center gap-1"
              >
                <span>View Full Certificate Vault & Life Events</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Officer Confirmation & Verification Queue Component */}
      <div className="space-y-2">
        <h2 className="text-lg font-bold text-gov-navy px-1">Active Verification & Officer Approval Queues</h2>
        <OfficerReviewQueue />
      </div>

    </div>
  );
};
