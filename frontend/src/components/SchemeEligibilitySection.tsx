import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Award, CheckCircle2, AlertCircle, ChevronDown, ChevronUp, RefreshCw, FileQuestion, ShieldAlert, Building } from 'lucide-react';

interface SchemeEligibilityProps {
  familyId: string;
}

export const SchemeEligibilitySection: React.FC<SchemeEligibilityProps> = ({ familyId }) => {
  const [expandedScheme, setExpandedScheme] = useState<string | null>(null);


  const { data: eligibilityList = [], isLoading, isError, isRefetching, refetch } = useQuery({
    queryKey: ['family-eligibility', familyId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${familyId}/eligibility`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch scheme eligibility');
      return res.json();
    },
  });

  const toggleExpand = (schemeId: string) => {
    setExpandedScheme(expandedScheme === schemeId ? null : schemeId);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'AUTOMATICALLY_ELIGIBLE':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> AUTOMATICALLY ELIGIBLE
          </span>
        );
      case 'NEEDS_DOCUMENT_VERIFICATION':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded bg-amber-50 text-amber-800 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" /> DOCS NEEDED
          </span>
        );
      case 'OFFICER_APPROVED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" /> OFFICER APPROVED
          </span>
        );
      case 'OFFICER_REJECTED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded bg-red-50 text-red-700 border border-red-200">
            <ShieldAlert className="w-3.5 h-3.5 text-red-600" /> OFFICER REJECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded bg-slate-100 text-slate-600 border border-slate-200">
            INELIGIBLE
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Entitlements Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded border border-slate-200 shadow-sm">
        <div>
          <h3 className="text-base font-bold text-gov-navy flex items-center gap-2">
            <Award className="w-5 h-5 text-saffron" />
            Rule-Based Welfare Scheme Entitlements
          </h3>
          <p className="text-xs text-slate-500">
            Real-time automated evaluation of state and central scheme eligibility based on household demographic & document attributes.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="px-3.5 py-2 rounded bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 text-xs font-semibold flex items-center gap-1.5 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin text-gov-navy' : 'text-slate-600'}`} />
          <span>{isRefetching ? 'Evaluating Rules...' : 'Re-evaluate Entitlements'}</span>
        </button>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-xs text-slate-500">Evaluating rule engine for all state schemes...</div>
      ) : isError ? (
        <div className="p-4 rounded bg-red-50 text-red-700 text-xs">Failed to load scheme eligibility data.</div>
      ) : eligibilityList.length === 0 ? (
        <div className="gov-card p-8 text-center text-xs text-slate-500">
          No schemes available in catalog.
        </div>
      ) : (
        <div className="space-y-3">
          {eligibilityList.map((item: any) => {
            const isExpanded = expandedScheme === item.scheme_id;
            const isEligible = item.status === 'AUTOMATICALLY_ELIGIBLE' || item.status === 'OFFICER_APPROVED';

            return (
              <div
                key={item.scheme_id}
                className={`gov-card overflow-hidden transition-all border ${
                  isEligible ? 'border-emerald-200 bg-white' : 'border-slate-200 bg-white'
                }`}
              >
                <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-gov-navy">{item.scheme_name}</span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                        {item.level}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Building className="w-3.5 h-3.5 text-slate-400" />
                        {item.department}
                      </span>
                      <span>•</span>
                      <span className="font-semibold text-emerald-700">
                        Benefit: {item.financial_benefit}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-3">
                    {getStatusBadge(item.status)}
                    <button
                      onClick={() => toggleExpand(item.scheme_id)}
                      className="px-3 py-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-gov-navy flex items-center gap-1"
                    >
                      <span>{isExpanded ? 'Hide Details' : 'Why Am I Eligible?'}</span>
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Expandable Breakdown Drawer */}
                {isExpanded && (
                  <div className="bg-slate-50 p-4 border-t border-slate-200 text-xs space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Evaluation Breakdown / Passed Criteria */}
                      <div className="space-y-2">
                        <h5 className="font-bold text-slate-700 flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          Passed Evaluation Criteria
                        </h5>
                        <ul className="space-y-1">
                          {item.passed_criteria && item.passed_criteria.length > 0 ? (
                            item.passed_criteria.map((rule: string, idx: number) => (
                              <li key={idx} className="flex items-start gap-1.5 text-slate-600 bg-white p-2 rounded border border-slate-200">
                                <span className="text-emerald-600 font-bold">✓</span>
                                <span>{rule}</span>
                              </li>
                            ))
                          ) : (
                            <li className="text-slate-400 italic">No passed criteria recorded</li>
                          )}
                        </ul>
                      </div>

                      {/* Failed or Missing Requirements */}
                      <div className="space-y-2">
                        <h5 className="font-bold text-slate-700 flex items-center gap-1.5">
                          <FileQuestion className="w-4 h-4 text-amber-600" />
                          Failed Criteria & Required Documents
                        </h5>
                        <ul className="space-y-1">
                          {item.failed_criteria && item.failed_criteria.length > 0 ? (
                            item.failed_criteria.map((rule: string, idx: number) => (
                              <li key={idx} className="flex items-start gap-1.5 text-red-700 bg-red-50 p-2 rounded border border-red-200">
                                <span className="text-red-600 font-bold">✕</span>
                                <span>{rule}</span>
                              </li>
                            ))
                          ) : (
                            <li className="text-emerald-700 font-medium bg-emerald-50 p-2 rounded border border-emerald-200">
                              No failed criteria found!
                            </li>
                          )}

                          {item.missing_documents && item.missing_documents.length > 0 && (
                            <div className="mt-2 p-2.5 rounded bg-amber-50 border border-amber-200 space-y-1">
                              <span className="font-bold text-amber-800 block">Missing Documents Required in Vault:</span>
                              {item.missing_documents.map((doc: string, idx: number) => (
                                <div key={idx} className="text-amber-900 font-semibold flex items-center gap-1">
                                  <span>• {doc.replace(/_/g, ' ')}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </ul>
                      </div>
                    </div>

                    {item.officer_notes && (
                      <div className="p-3 bg-blue-50 rounded border border-blue-200 text-blue-900">
                        <span className="font-bold block text-[11px] uppercase tracking-wider text-blue-700">Department Officer Review Notes:</span>
                        <span>{item.officer_notes}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
