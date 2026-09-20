import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock3, ExternalLink, FileText, RefreshCw, Send } from 'lucide-react';

interface ApplicationsSectionProps { familyId: string; }

const tokenHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`, 'Content-Type': 'application/json' });

export const ApplicationsSection: React.FC<ApplicationsSectionProps> = ({ familyId }) => {
  const [message, setMessage] = useState<string | null>(null);
  const applications = useQuery({
    queryKey: ['applications', familyId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/families/${familyId}/applications`, { headers: tokenHeaders() });
      if (!response.ok) throw new Error('Unable to load applications');
      return response.json();
    },
  });
  const eligibility = useQuery({
    queryKey: ['family-eligibility', familyId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/families/${familyId}/eligibility`, { headers: tokenHeaders() });
      if (!response.ok) throw new Error('Unable to load eligibility');
      return response.json();
    },
  });

  const apply = async (schemeId: string) => {
    setMessage(null);
    const response = await fetch(`/api/v1/families/${familyId}/applications`, { method: 'POST', headers: tokenHeaders(), body: JSON.stringify({ scheme_id: schemeId }) });
    const body = await response.json();
    setMessage(response.ok ? `Application submitted. Reference: ${body.external_reference}` : body.detail || 'Application could not be submitted.');
    if (response.ok) await applications.refetch();
  };

  const refresh = async (applicationId: string) => {
    const response = await fetch(`/api/v1/families/${familyId}/applications/${applicationId}/refresh`, { method: 'POST', headers: tokenHeaders() });
    const body = await response.json();
    setMessage(response.ok ? `Status updated: ${body.status.replaceAll('_', ' ')}` : body.detail || 'Status refresh failed.');
    if (response.ok) await applications.refetch();
  };

  const activeSchemeIds = new Set((applications.data || []).filter((item: any) => !['REJECTED', 'DISBURSED'].includes(item.status)).map((item: any) => item.scheme_id));
  const available = (eligibility.data || []).filter((item: any) => ['AUTO_ELIGIBLE', 'OFFICER_APPROVED'].includes(item.status) && !activeSchemeIds.has(item.scheme_id));

  return <div className="space-y-5">
    <div className="gov-card p-5 flex flex-col sm:flex-row gap-4 justify-between">
      <div><h3 className="font-bold text-gov-navy flex items-center gap-2"><FileText className="w-5 h-5 text-saffron" />Scheme applications</h3><p className="text-xs text-slate-500 mt-1">Submit eligible applications with pre-filled household information, then track simulated official-portal updates.</p></div>
      <button onClick={() => { applications.refetch(); eligibility.refetch(); }} className="self-start px-3 py-2 rounded border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold flex gap-1.5 items-center transition-colors"><RefreshCw className="w-3.5 h-3.5" />Refresh</button>
    </div>
    {message && <div className="p-3 rounded text-xs font-medium bg-blue-50 border border-blue-200 text-blue-800">{message}</div>}
    {available.length > 0 && <div className="gov-card p-4 space-y-3"><h4 className="font-bold text-sm text-gov-navy">Ready to apply</h4>{available.map((item: any) => <div key={item.scheme_id} className="flex items-center justify-between gap-3 p-3 rounded bg-slate-50 border border-slate-200"><div><p className="text-sm font-semibold text-slate-900">{item.scheme_name}</p><p className="text-xs text-slate-500">{item.benefit_summary}</p></div><button onClick={() => apply(item.scheme_id)} className="shrink-0 px-3 py-2 rounded bg-gov-navy hover:bg-slate-800 text-white text-xs font-bold flex gap-1 items-center transition-colors"><Send className="w-3.5 h-3.5" />Apply</button></div>)}</div>}
    {applications.isLoading ? <div className="text-xs text-slate-500 p-5">Loading applications…</div> : applications.data?.length === 0 ? <div className="gov-card p-6 text-center text-xs text-slate-500">No applications submitted yet.</div> : <div className="space-y-3">{applications.data.map((item: any) => <div key={item.application_id} className="gov-card p-4"><div className="flex flex-col sm:flex-row justify-between gap-3"><div><p className="font-bold text-gov-navy">{item.scheme_name}</p><p className="text-xs text-slate-500 mt-1">{item.external_reference} · {item.source_system}</p></div><div className="flex items-center gap-2"><span className="text-[11px] font-bold px-2 py-1 rounded bg-emerald-50 border border-emerald-200 text-emerald-700">{item.status.replaceAll('_', ' ')}</span><button onClick={() => refresh(item.application_id)} className="p-2 rounded border border-slate-300 bg-white hover:bg-slate-50 text-slate-600 transition-colors" title="Refresh status"><RefreshCw className="w-3.5 h-3.5" /></button><a href={item.official_url} target="_blank" rel="noreferrer" className="p-2 rounded border border-slate-300 bg-white hover:bg-slate-50 text-slate-600 transition-colors" title="Official portal"><ExternalLink className="w-3.5 h-3.5" /></a></div></div><div className="mt-3 flex flex-wrap gap-2">{item.history.map((history: any) => <span key={`${history.status}-${history.occurred_at}`} className="text-[10px] px-2 py-1 rounded bg-slate-100 text-slate-600 flex items-center gap-1"><Clock3 className="w-3 h-3" />{history.status.replaceAll('_', ' ')}</span>)}</div></div>)}</div>}
  </div>;
};
