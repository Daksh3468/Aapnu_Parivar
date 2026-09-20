import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import {
  Users, IndianRupee, Activity,
  RefreshCw, Play,
  AlertTriangle, Baby, HeartCrack, Scissors,
} from 'lucide-react';

// ─── API helpers ────────────────────────────────────────────────────────────

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

async function apiFetch<T>(path: string, token?: string, opts?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

// ─── Types ──────────────────────────────────────────────────────────────────

interface OverviewData {
  snapshot_date: string;
  total_families: number;
  active_families: number;
  total_members: number;
  verified_families: number;
  bpl_families: number;
  total_scheme_applications: number;
  approved_applications: number;
  disbursed_applications: number;
  rejected_applications: number;
  pending_applications: number;
  total_disbursed_amount_inr: number;
  total_births_recorded: number;
  total_deaths_recorded: number;
  total_splits_this_month: number;
  district_breakdown: Record<string, { families: number; disbursed_inr: number }>;
  scheme_application_counts: Record<string, number>;
  monthly_trend: Array<{ month: string; applications: number; disbursed_inr: number }>;
  refreshed_at: string | null;
}

interface SimRun {
  run_id: string;
  simulation_label: string;
  simulation_date: string;
  benefit_amount_inr: number;
  scheme_filter?: string;
  income_band_filter?: string;
  ration_card_filter?: string;
  eligible_family_count: number;
  total_projected_disbursement_inr: number;
  district_breakdown?: Record<string, { count: number; amount_inr: number }>;
  scheme_breakdown?: Record<string, number>;
  status: string;
  error_message?: string;
  created_at: string;
}

// ─── Color palette (Government theme) ───────────────────────────────────────
const NAVY = '#0f172a';
const AMBER = '#d97706';
const EMERALD = '#059669';
const ROSE = '#e11d48';
const INDIGO = '#4f46e5';
const SLATE = '#64748b';

const DISTRICT_COLORS = [
  '#059669', '#d97706', '#4f46e5', '#e11d48', '#0891b2',
  '#7c3aed', '#1e40af', '#ca8a04', '#be123c', '#0369a1',
];

// ─── Utility ─────────────────────────────────────────────────────────────────
const fmt = (n: number) =>
  n >= 10_000_000 ? `₹${(n / 10_000_000).toFixed(2)} Cr`
    : n >= 100_000 ? `₹${(n / 100_000).toFixed(2)} L`
    : `₹${n.toLocaleString('en-IN')}`;

// ─── Sub-components ──────────────────────────────────────────────────────────

interface KPICardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const KPICard: React.FC<KPICardProps> = ({ icon, label, value, sub, color = NAVY, trend }) => (
  <div style={{
    background: 'white',
    border: `1px solid #e2e8f0`,
    borderTop: `4px solid ${color}`,
    borderRadius: 12,
    padding: '20px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    boxShadow: '0 1px 6px rgba(15,23,42,0.06)',
    transition: 'box-shadow 0.2s',
    cursor: 'default',
  }}
  onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 16px rgba(15,23,42,0.12)')}
  onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 1px 6px rgba(15,23,42,0.06)')}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div style={{ color: 'white', background: color, borderRadius: 8, padding: 10 }}>{icon}</div>
      {trend && (
        <span style={{
          fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 99,
          background: trend === 'up' ? '#d1fae5' : trend === 'down' ? '#fee2e2' : '#f1f5f9',
          color: trend === 'up' ? EMERALD : trend === 'down' ? ROSE : SLATE,
        }}>
          {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '–'}
        </span>
      )}
    </div>
    <div style={{ fontSize: 28, fontWeight: 800, color: NAVY, letterSpacing: -1 }}>{value}</div>
    <div style={{ fontSize: 13, fontWeight: 600, color: SLATE }}>{label}</div>
    {sub && <div style={{ fontSize: 11, color: '#94a3b8' }}>{sub}</div>}
  </div>
);

// ─── Simulation Modal ─────────────────────────────────────────────────────────

interface SimModalProps {
  token: string;
  onClose: () => void;
  onResult: (run: SimRun) => void;
}

const INCOME_BANDS = ['LT_1L', '1L_2_5L', '2_5L_5L', '5L_8L', 'GT_8L'];
const RATION_CARDS = ['AAY', 'PHH', 'NON_NFSA', 'NONE'];

const SimModal: React.FC<SimModalProps> = ({ token, onClose, onResult }) => {
  const [label, setLabel] = useState('Gujarat Q4 Disbursement Projection');
  const [amount, setAmount] = useState(6000);
  const [scheme, setScheme] = useState('');
  const [income, setIncome] = useState('');
  const [ration, setRation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiFetch<SimRun>('/analytics/simulate', token, {
        method: 'POST',
        body: JSON.stringify({
          simulation_label: label,
          benefit_amount_inr: amount,
          scheme_filter: scheme || undefined,
          income_band_filter: income || undefined,
          ration_card_filter: ration || undefined,
        }),
      });
      onResult(result);
      onClose();
    } catch (err: unknown) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.6)', zIndex: 9999,
      display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)',
    }}>
      <div style={{
        background: 'white', borderRadius: 16, padding: '32px 36px', width: 480,
        boxShadow: '0 24px 64px rgba(15,23,42,0.24)', maxHeight: '90vh', overflowY: 'auto',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: NAVY, margin: 0 }}>DBT Simulation</h2>
            <p style={{ fontSize: 12, color: SLATE, margin: '4px 0 0' }}>
              Read-only projection — citizen data is never mutated
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 20, color: SLATE }}>✕</button>
        </div>

        {[
          { label: 'Simulation Label', el: <input value={label} onChange={e => setLabel(e.target.value)} style={inputStyle} /> },
          { label: 'Benefit Amount per Household (₹)', el: <input type="number" value={amount} onChange={e => setAmount(Number(e.target.value))} style={inputStyle} min={0} /> },
          { label: 'Scheme Filter (optional)', el: <input value={scheme} onChange={e => setScheme(e.target.value)} placeholder="e.g. Kisan Samman Nidhi" style={inputStyle} /> },
          {
            label: 'Income Band Filter (optional)', el: (
              <select value={income} onChange={e => setIncome(e.target.value)} style={inputStyle}>
                <option value="" style={{ background: '#ffffff', color: '#0f172a' }}>— All Income Bands —</option>
                {INCOME_BANDS.map(b => <option key={b} value={b} style={{ background: '#ffffff', color: '#0f172a' }}>{b}</option>)}
              </select>
            )
          },
          {
            label: 'Ration Card Filter (optional)', el: (
              <select value={ration} onChange={e => setRation(e.target.value)} style={inputStyle}>
                <option value="" style={{ background: '#ffffff', color: '#0f172a' }}>— All Ration Cards —</option>
                {RATION_CARDS.map(r => <option key={r} value={r} style={{ background: '#ffffff', color: '#0f172a' }}>{r}</option>)}
              </select>
            )
          },
        ].map(({ label: l, el }) => (
          <div key={l} style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: NAVY, marginBottom: 6 }}>{l}</label>
            {el}
          </div>
        ))}

        {error && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '8px 12px', color: ROSE, fontSize: 13, marginBottom: 16 }}>{error}</div>}

        <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
          <button onClick={onClose} style={{ flex: 1, padding: '10px 0', border: '1.5px solid #cbd5e1', borderRadius: 8, background: 'white', color: '#334155', fontWeight: 600, cursor: 'pointer', fontSize: 14 }}>
            Cancel
          </button>
          <button onClick={run} disabled={loading || !label || amount <= 0} style={{
            flex: 2, padding: '10px 0', borderRadius: 8, border: 'none',
            background: loading ? '#94a3b8' : EMERALD, color: 'white', fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, fontSize: 14,
          }}>
            {loading ? <><RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Running…</> : <><Play size={14} /> Run Simulation</>}
          </button>
        </div>
      </div>
    </div>
  );
};

const inputStyle: React.CSSProperties = {
  width: '100%', boxSizing: 'border-box',
  border: '1.5px solid #cbd5e1', borderRadius: 8, padding: '9px 12px',
  fontSize: 14, color: '#0f172a', background: '#ffffff', outline: 'none',
  fontFamily: 'inherit',
};

// ─── Main Analytics Dashboard Page ───────────────────────────────────────────

export const AnalyticsDashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [simRuns, setSimRuns] = useState<SimRun[]>([]);
  const [latestSim, setLatestSim] = useState<SimRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showSimModal, setShowSimModal] = useState(false);
  const [error, setError] = useState('');

  // Get authentication token from localStorage
  const token: string | null = localStorage.getItem('access_token') || localStorage.getItem('officer_token');

  const loadOverview = useCallback(async () => {
    try {
      const data = await apiFetch<OverviewData>('/analytics/overview');
      setOverview(data);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  const loadSimRuns = useCallback(async () => {
    if (!token) return;
    try {
      const runs = await apiFetch<SimRun[]>('/analytics/simulations?limit=10', token);
      setSimRuns(runs);
      if (runs.length > 0) setLatestSim(runs[0]);
    } catch {
      // Non-officers won't see this
    }
  }, [token]);

  useEffect(() => {
    setLoading(true);
    Promise.all([loadOverview(), loadSimRuns()]).finally(() => setLoading(false));
  }, [loadOverview, loadSimRuns]);

  const handleForceRefresh = async () => {
    if (!token) return;
    setRefreshing(true);
    try {
      const data = await apiFetch<OverviewData>('/analytics/refresh', token, { method: 'POST' });
      setOverview(data);
    } catch (e) {
      setError(String(e));
    } finally {
      setRefreshing(false);
    }
  };

  const handleSimResult = (run: SimRun) => {
    setLatestSim(run);
    setSimRuns(prev => [run, ...prev]);
  };

  // Derived chart data
  const districtData = overview
    ? Object.entries(overview.district_breakdown).map(([name, v]) => ({
        name: name.length > 12 ? name.slice(0, 12) + '…' : name,
        families: v.families,
        disbursed: Math.round(v.disbursed_inr / 100000),
      }))
    : [];

  const schemeData = overview
    ? Object.entries(overview.scheme_application_counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
        .map(([name, count]) => ({ name: name.length > 18 ? name.slice(0, 18) + '…' : name, count }))
    : [];

  const appStatusData = overview ? [
    { name: 'Approved', value: overview.approved_applications, color: EMERALD },
    { name: 'Disbursed', value: overview.disbursed_applications, color: INDIGO },
    { name: 'Pending', value: overview.pending_applications, color: AMBER },
    { name: 'Rejected', value: overview.rejected_applications, color: ROSE },
  ] : [];

  if (loading) {
    return (
      <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16 }}>
        <RefreshCw size={32} style={{ color: EMERALD, animation: 'spin 1s linear infinite' }} />
        <p style={{ color: SLATE, fontWeight: 600 }}>Loading statewide analytics…</p>
      </div>
    );
  }

  if (error && !overview) {
    return (
      <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: ROSE }}>
          <AlertTriangle size={40} />
          <p style={{ fontWeight: 700, marginTop: 12 }}>Failed to load analytics</p>
          <p style={{ fontSize: 13, color: SLATE }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ paddingTop: 28, paddingBottom: 48, fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* ── Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
            <div style={{ background: NAVY, borderRadius: 10, padding: 10 }}>
              <Activity size={22} color={AMBER} />
            </div>
            <div>
              <h1 style={{ fontSize: 26, fontWeight: 900, color: NAVY, margin: 0 }}>
                Statewide Welfare Analytics
              </h1>
              <p style={{ fontSize: 13, color: SLATE, margin: 0 }}>Gujarat — Aapnu Parivar Portal</p>
            </div>
          </div>
          {overview && (
            <p style={{ fontSize: 12, color: '#94a3b8', margin: 0 }}>
              Snapshot: <strong>{overview.snapshot_date}</strong> · Last refreshed: {overview.refreshed_at?.slice(0, 19) ?? '—'}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          {token && (
            <>
              <button
                onClick={() => setShowSimModal(true)}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', background: EMERALD, color: 'white', border: 'none', borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: 'pointer' }}
              >
                <Play size={15} /> DBT Simulation
              </button>
              <button
                onClick={handleForceRefresh}
                disabled={refreshing}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', background: 'white', color: NAVY, border: '1.5px solid #e2e8f0', borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: refreshing ? 'not-allowed' : 'pointer' }}
              >
                <RefreshCw size={15} style={refreshing ? { animation: 'spin 1s linear infinite' } : {}} />
                Refresh
              </button>
            </>
          )}
        </div>
      </div>

      {/* ── KPI Cards Row 1 ── */}
      {overview && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16, marginBottom: 20 }}>
            <KPICard icon={<Users size={22} />} label="Total Households" value={overview.total_families.toLocaleString('en-IN')} sub={`${overview.verified_families.toLocaleString('en-IN')} verified`} color={NAVY} trend="up" />
            <KPICard icon={<Users size={22} />} label="Total Members" value={overview.total_members.toLocaleString('en-IN')} sub={`${overview.bpl_families.toLocaleString('en-IN')} BPL families`} color={INDIGO} trend="up" />
            <KPICard icon={<IndianRupee size={22} />} label="Total Disbursed" value={fmt(overview.total_disbursed_amount_inr)} sub={`${overview.disbursed_applications} applications`} color={EMERALD} trend="up" />
            <KPICard icon={<Activity size={22} />} label="Applications" value={overview.total_scheme_applications.toLocaleString('en-IN')} sub={`${overview.pending_applications} pending`} color={AMBER} trend="neutral" />
            <KPICard icon={<Baby size={22} />} label="Births Recorded" value={overview.total_births_recorded} color={EMERALD} />
            <KPICard icon={<HeartCrack size={22} />} label="Deaths Recorded" value={overview.total_deaths_recorded} color={ROSE} />
            <KPICard icon={<Scissors size={22} />} label="Splits This Month" value={overview.total_splits_this_month} color={AMBER} />
          </div>

          {/* ── Charts Row 1 ── */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 20, marginBottom: 20 }}>
            {/* Monthly Trend */}
            <div style={cardStyle}>
              <h3 style={cardTitle}>Monthly Applications & Disbursement Trend</h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={overview.monthly_trend} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: SLATE }} />
                  <YAxis yAxisId="left" tick={{ fontSize: 11, fill: SLATE }} />
                  <YAxis yAxisId="right" orientation="right" tickFormatter={v => `₹${(v / 100000).toFixed(0)}L`} tick={{ fontSize: 11, fill: SLATE }} />
                  <Tooltip
                    contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
                    formatter={(val, name) =>
                      name === 'disbursed_inr'
                        ? [fmt(Number(val)), 'Disbursed']
                        : [Number(val).toLocaleString('en-IN'), 'Applications']
                    }
                  />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="applications" stroke={INDIGO} strokeWidth={2.5} dot={false} name="Applications" />
                  <Line yAxisId="right" type="monotone" dataKey="disbursed_inr" stroke={EMERALD} strokeWidth={2.5} dot={false} name="disbursed_inr" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Application Status Pie */}
            <div style={cardStyle}>
              <h3 style={cardTitle}>Application Status Breakdown</h3>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={appStatusData}
                    cx="50%" cy="50%"
                    innerRadius={60} outerRadius={100}
                    paddingAngle={4}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {appStatusData.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 12px', marginTop: 8, justifyContent: 'center' }}>
                {appStatusData.map(d => (
                  <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}>
                    <div style={{ width: 10, height: 10, borderRadius: 2, background: d.color }} />
                    <span style={{ color: SLATE }}>{d.name}: <strong>{d.value}</strong></span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Charts Row 2 ── */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
            {/* District Breakdown */}
            <div style={cardStyle}>
              <h3 style={cardTitle}>Households by District</h3>
              {districtData.length === 0 ? (
                <div style={emptyState}>No district data yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={districtData} margin={{ top: 8, right: 8, left: 0, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 10, fill: SLATE }} angle={-35} textAnchor="end" interval={0} />
                    <YAxis tick={{ fontSize: 11, fill: SLATE }} />
                    <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                    <Bar dataKey="families" name="Households" radius={[4, 4, 0, 0]}>
                      {districtData.map((_, i) => (
                        <Cell key={i} fill={DISTRICT_COLORS[i % DISTRICT_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Scheme Applications */}
            <div style={cardStyle}>
              <h3 style={cardTitle}>Top Schemes by Applications</h3>
              {schemeData.length === 0 ? (
                <div style={emptyState}>No scheme applications yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={schemeData} layout="vertical" margin={{ top: 8, right: 24, left: 8, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11, fill: SLATE }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: SLATE }} width={130} />
                    <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                    <Bar dataKey="count" name="Applications" fill={NAVY} radius={[0, 4, 4, 0]}>
                      {schemeData.map((_, i) => (
                        <Cell key={i} fill={DISTRICT_COLORS[i % DISTRICT_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </>
      )}

      {/* ── DBT Simulation Results ── */}
      {(latestSim || simRuns.length > 0) && (
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ ...cardTitle, margin: 0 }}>DBT Simulation Results</h3>
            {token && (
              <button onClick={() => setShowSimModal(true)} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', background: EMERALD, color: 'white', border: 'none', borderRadius: 6, fontWeight: 600, fontSize: 13, cursor: 'pointer' }}>
                <Play size={13} /> New Simulation
              </button>
            )}
          </div>

          {latestSim && (
            <div style={{ background: '#f8fafc', borderRadius: 10, padding: '20px 24px', marginBottom: 20, border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <span style={{ fontSize: 11, fontWeight: 700, color: EMERALD, textTransform: 'uppercase', letterSpacing: 1 }}>Latest Run — {latestSim.run_id}</span>
                  <h4 style={{ margin: '4px 0 0', fontWeight: 800, color: NAVY, fontSize: 18 }}>{latestSim.simulation_label}</h4>
                </div>
                <span style={{
                  background: latestSim.status === 'COMPLETED' ? '#d1fae5' : '#fee2e2',
                  color: latestSim.status === 'COMPLETED' ? EMERALD : ROSE,
                  fontWeight: 700, fontSize: 12, padding: '4px 10px', borderRadius: 99,
                }}>
                  {latestSim.status}
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 16 }}>
                {[
                  { label: 'Eligible Families', value: latestSim.eligible_family_count.toLocaleString('en-IN') },
                  { label: 'Per-household Benefit', value: fmt(latestSim.benefit_amount_inr) },
                  { label: 'Total Projected Disbursement', value: fmt(latestSim.total_projected_disbursement_inr) },
                  { label: 'Scheme Filter', value: latestSim.scheme_filter ?? '—' },
                  { label: 'Income Band', value: latestSim.income_band_filter ?? '—' },
                  { label: 'Ration Card', value: latestSim.ration_card_filter ?? '—' },
                ].map(({ label, value }) => (
                  <div key={label} style={{ background: 'white', borderRadius: 8, padding: '12px 16px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: 11, color: SLATE, marginBottom: 4 }}>{label}</div>
                    <div style={{ fontWeight: 800, fontSize: 16, color: NAVY }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* History Table */}
          {simRuns.length > 0 && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                    {['Run ID', 'Label', 'Date', 'Eligible Families', 'Projected Total', 'Status'].map(h => (
                      <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 700, color: NAVY, whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {simRuns.map((r, i) => (
                    <tr key={r.run_id} style={{ borderBottom: '1px solid #f1f5f9', background: i % 2 === 0 ? 'white' : '#fafafa' }}>
                      <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontSize: 12, color: INDIGO }}>{r.run_id}</td>
                      <td style={{ padding: '10px 14px', color: NAVY, fontWeight: 600, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.simulation_label}</td>
                      <td style={{ padding: '10px 14px', color: SLATE }}>{r.simulation_date}</td>
                      <td style={{ padding: '10px 14px', color: NAVY, fontWeight: 700 }}>{r.eligible_family_count.toLocaleString('en-IN')}</td>
                      <td style={{ padding: '10px 14px', color: EMERALD, fontWeight: 700 }}>{fmt(r.total_projected_disbursement_inr)}</td>
                      <td style={{ padding: '10px 14px' }}>
                        <span style={{
                          background: r.status === 'COMPLETED' ? '#d1fae5' : '#fee2e2',
                          color: r.status === 'COMPLETED' ? EMERALD : ROSE,
                          fontWeight: 700, fontSize: 11, padding: '3px 8px', borderRadius: 99,
                        }}>
                          {r.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {!token && (
        <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 10, padding: '14px 20px', color: '#92400e', fontSize: 13, fontWeight: 600, marginTop: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={16} />
            Sign in as a Departmental Officer to run real-time DBT simulations and refresh live analytics data.
          </div>
          <a href="/officer-login" style={{ background: '#0f172a', color: '#ffffff', padding: '6px 14px', borderRadius: 6, textDecoration: 'none', fontSize: 12, fontWeight: 700, whiteSpace: 'nowrap' }}>
            Officer Login
          </a>
        </div>
      )}

      {showSimModal && token && (
        <SimModal
          token={token}
          onClose={() => setShowSimModal(false)}
          onResult={handleSimResult}
        />
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default AnalyticsDashboardPage;

// ─── Shared styles ──────────────────────────────────────────────────────────
const cardStyle: React.CSSProperties = {
  background: 'white',
  border: '1px solid #e2e8f0',
  borderRadius: 14,
  padding: '24px 24px 20px',
  boxShadow: '0 1px 6px rgba(15,23,42,0.06)',
};

const cardTitle: React.CSSProperties = {
  fontSize: 15,
  fontWeight: 800,
  color: NAVY,
  marginBottom: 16,
  marginTop: 0,
};

const emptyState: React.CSSProperties = {
  height: 200,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: '#94a3b8',
  fontSize: 14,
  fontWeight: 600,
};
