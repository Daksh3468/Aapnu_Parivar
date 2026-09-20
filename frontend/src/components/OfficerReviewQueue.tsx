import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, XCircle, FileCheck, Award, RefreshCw, MessageSquare, ShieldAlert, Layers } from 'lucide-react';

export const OfficerReviewQueue: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeQueue, setActiveQueue] = useState<'DOCUMENTS' | 'ELIGIBILITY' | 'SPLITS'>('DOCUMENTS');
  
  const [rejectModalDoc, setRejectModalDoc] = useState<any | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  
  const [reviewModalEligibility, setReviewModalEligibility] = useState<any | null>(null);
  const [reviewAction, setReviewAction] = useState<'OFFICER_APPROVED' | 'OFFICER_REJECTED'>('OFFICER_APPROVED');
  const [officerNotes, setOfficerNotes] = useState('');

  const [reviewModalSplit, setReviewModalSplit] = useState<any | null>(null);
  const [splitAction, setSplitAction] = useState<'OFFICER_APPROVED' | 'OFFICER_REJECTED'>('OFFICER_APPROVED');
  const [splitNotes, setSplitNotes] = useState('');

  // Fetch pending document queue
  const { data: docQueue = [], isLoading: isDocLoading, refetch: refetchDocs } = useQuery({
    queryKey: ['officer-doc-queue'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/v1/officer/documents-queue', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load document queue');
      return res.json();
    },
  });

  // Fetch pending eligibility review queue
  const { data: eligQueue = [], isLoading: isEligLoading, refetch: refetchElig } = useQuery({
    queryKey: ['officer-eligibility-queue'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/v1/officer/eligibility-queue', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load eligibility queue');
      return res.json();
    },
  });

  // Fetch pending split review queue
  const { data: splitQueue = [], isLoading: isSplitLoading, refetch: refetchSplits } = useQuery({
    queryKey: ['officer-splits-queue'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/v1/officer/splits-queue', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load split queue');
      return res.json();
    },
  });

  // Document verification mutation
  const docVerifyMutation = useMutation({
    mutationFn: async ({ docId, status, reason }: { docId: number; status: string; reason?: string }) => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/documents/${docId}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          status,
          rejection_reason: reason,
        }),
      });
      if (!res.ok) throw new Error('Failed to update document status');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['officer-doc-queue'] });
      setRejectModalDoc(null);
      setRejectionReason('');
    },
  });

  // Eligibility review mutation
  const eligReviewMutation = useMutation({
    mutationFn: async ({ familyId, schemeId, status, notes }: { familyId: string; schemeId: string; status: string; notes?: string }) => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${familyId}/eligibility/${schemeId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          status,
          officer_notes: notes,
        }),
      });
      if (!res.ok) throw new Error('Failed to submit officer eligibility review');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['officer-eligibility-queue'] });
      setReviewModalEligibility(null);
      setOfficerNotes('');
    },
  });

  // Split review mutation
  const splitReviewMutation = useMutation({
    mutationFn: async ({ splitId, status, notes }: { splitId: number; status: string; notes?: string }) => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/officer/splits/${splitId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          status,
          officer_notes: notes,
        }),
      });
      if (!res.ok) throw new Error('Failed to submit officer split review');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['officer-splits-queue'] });
      setReviewModalSplit(null);
      setSplitNotes('');
    },
  });

  const handleApproveDoc = (docId: number) => {
    docVerifyMutation.mutate({ docId, status: 'VERIFIED' });
  };

  const handleRejectDocSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!rejectModalDoc) return;
    docVerifyMutation.mutate({
      docId: rejectModalDoc.document_id,
      status: 'REJECTED',
      reason: rejectionReason || 'Document record mismatch / illegible certificate copy',
    });
  };

  const handleEligReviewSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewModalEligibility) return;
    eligReviewMutation.mutate({
      familyId: reviewModalEligibility.family_id,
      schemeId: reviewModalEligibility.scheme_id,
      status: reviewAction,
      notes: officerNotes || (reviewAction === 'OFFICER_APPROVED' ? 'Approved based on field survey verification.' : 'Rejected due to insufficient proof.'),
    });
  };

  const handleSplitReviewSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewModalSplit) return;
    splitReviewMutation.mutate({
      splitId: reviewModalSplit.split_id,
      status: splitAction,
      notes: splitNotes || (splitAction === 'OFFICER_APPROVED' ? 'Split approved after verifying residential separation.' : 'Split rejected due to anomaly risk.'),
    });
  };

  return (
    <div className="space-y-4">
      {/* Subnav Tabs */}
      <div className="flex flex-wrap items-center justify-between border border-slate-300 bg-slate-200/90 p-1.5 rounded-xl">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => setActiveQueue('DOCUMENTS')}
            className={`py-2.5 px-4 text-xs font-extrabold rounded-lg flex items-center gap-2 transition-all ${
              activeQueue === 'DOCUMENTS'
                ? 'tab-active ring-1 ring-slate-900'
                : 'tab-inactive'
            }`}
          >
            {activeQueue === 'DOCUMENTS' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
            <FileCheck className={`w-4 h-4 ${activeQueue === 'DOCUMENTS' ? 'text-saffron' : 'text-slate-500'}`} />
            <span>Document Verification Queue</span>
            <span className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
              activeQueue === 'DOCUMENTS' ? 'bg-amber-400 text-slate-950' : 'bg-slate-300 text-slate-800'
            }`}>
              {docQueue.length}
            </span>
          </button>

          <button
            onClick={() => setActiveQueue('ELIGIBILITY')}
            className={`py-2.5 px-4 text-xs font-extrabold rounded-lg flex items-center gap-2 transition-all ${
              activeQueue === 'ELIGIBILITY'
                ? 'tab-active ring-1 ring-slate-900'
                : 'tab-inactive'
            }`}
          >
            {activeQueue === 'ELIGIBILITY' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
            <Award className={`w-4 h-4 ${activeQueue === 'ELIGIBILITY' ? 'text-saffron' : 'text-slate-500'}`} />
            <span>Eligibility Override Queue</span>
            <span className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
              activeQueue === 'ELIGIBILITY' ? 'bg-amber-400 text-slate-950' : 'bg-slate-300 text-slate-800'
            }`}>
              {eligQueue.length}
            </span>
          </button>

          <button
            onClick={() => setActiveQueue('SPLITS')}
            className={`py-2.5 px-4 text-xs font-extrabold rounded-lg flex items-center gap-2 transition-all ${
              activeQueue === 'SPLITS'
                ? 'tab-active ring-1 ring-slate-900'
                : 'tab-inactive'
            }`}
          >
            {activeQueue === 'SPLITS' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
            <Layers className={`w-4 h-4 ${activeQueue === 'SPLITS' ? 'text-saffron' : 'text-slate-500'}`} />
            <span>Household Split Reviews</span>
            <span className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
              activeQueue === 'SPLITS' ? 'bg-amber-400 text-slate-950' : 'bg-slate-300 text-slate-800'
            }`}>
              {splitQueue.length}
            </span>
          </button>
        </div>

        <button
          onClick={() => {
            refetchDocs();
            refetchElig();
            refetchSplits();
          }}
          className="p-1.5 text-slate-500 hover:text-gov-navy rounded hover:bg-slate-100"
          title="Refresh Queues"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Reject Doc Modal */}
      {rejectModalDoc && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full overflow-hidden">
            <div className="bg-red-700 px-5 py-3 text-white flex items-center justify-between">
              <h4 className="font-bold text-sm">Reject Document Certificate</h4>
              <button onClick={() => setRejectModalDoc(null)} className="text-white text-lg font-bold">&times;</button>
            </div>
            <form onSubmit={handleRejectDocSubmit} className="p-5 space-y-4 text-xs">
              <p className="text-slate-600">
                Rejecting document <strong>{rejectModalDoc.document_type}</strong> (Ref: {rejectModalDoc.document_number}) for Family <strong>#{rejectModalDoc.family_id}</strong>.
              </p>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Reason for Rejection *</label>
                <textarea
                  rows={3}
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="e.g. Income certificate expired or authority stamp illegible"
                  className="w-full p-2 border border-slate-300 rounded bg-white text-slate-900 focus:ring-1 focus:ring-red-600 focus:outline-none"
                  required
                />
              </div>
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button type="button" onClick={() => setRejectModalDoc(null)} className="px-3 py-1.5 border border-slate-300 rounded bg-white text-slate-700 font-semibold hover:bg-slate-50 transition-colors">Cancel</button>
                <button type="submit" disabled={docVerifyMutation.isPending} className="px-4 py-1.5 rounded bg-red-700 hover:bg-red-800 text-white font-bold transition-colors">Confirm Rejection</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Eligibility Review Modal */}
      {reviewModalEligibility && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full overflow-hidden">
            <div className="bg-gov-navy px-5 py-3 text-white flex items-center justify-between">
              <h4 className="font-bold text-sm">Officer Eligibility Override Review</h4>
              <button onClick={() => setReviewModalEligibility(null)} className="text-white text-lg font-bold">&times;</button>
            </div>
            <form onSubmit={handleEligReviewSubmit} className="p-5 space-y-4 text-xs">
              <div>
                <p className="text-slate-600 font-medium">
                  Reviewing <strong>{reviewModalEligibility.scheme_name}</strong> application for Household Head <strong>{reviewModalEligibility.head_name}</strong> (Family ID: #{reviewModalEligibility.family_id}).
                </p>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Decision</label>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-1.5 font-bold text-emerald-700 cursor-pointer">
                    <input
                      type="radio"
                      name="decision"
                      value="OFFICER_APPROVED"
                      checked={reviewAction === 'OFFICER_APPROVED'}
                      onChange={() => setReviewAction('OFFICER_APPROVED')}
                    />
                    Approve Override
                  </label>
                  <label className="flex items-center gap-1.5 font-bold text-red-700 cursor-pointer">
                    <input
                      type="radio"
                      name="decision"
                      value="OFFICER_REJECTED"
                      checked={reviewAction === 'OFFICER_REJECTED'}
                      onChange={() => setReviewAction('OFFICER_REJECTED')}
                    />
                    Reject Scheme Application
                  </label>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Officer Notes / Justification</label>
                <textarea
                  rows={3}
                  value={officerNotes}
                  onChange={(e) => setOfficerNotes(e.target.value)}
                  placeholder="State reason for approval or rejection override..."
                  className="w-full p-2 border border-slate-300 rounded bg-white text-slate-900 focus:ring-1 focus:ring-gov-navy focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button type="button" onClick={() => setReviewModalEligibility(null)} className="px-3 py-1.5 border border-slate-300 rounded bg-white text-slate-700 font-semibold hover:bg-slate-50 transition-colors">Cancel</button>
                <button type="submit" disabled={eligReviewMutation.isPending} className="px-4 py-1.5 rounded bg-gov-navy hover:bg-slate-800 text-white font-bold transition-colors">Submit Review</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Split Review Modal */}
      {reviewModalSplit && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full overflow-hidden">
            <div className="bg-gov-navy px-5 py-3 text-white flex items-center justify-between">
              <h4 className="font-bold text-sm">Review Household Split Request</h4>
              <button onClick={() => setReviewModalSplit(null)} className="text-white text-lg font-bold">&times;</button>
            </div>
            <form onSubmit={handleSplitReviewSubmit} className="p-5 space-y-4 text-xs">
              <div>
                <p className="text-slate-600 font-medium">
                  Reviewing Split Request <strong>#{reviewModalSplit.split_id}</strong> for Source Family <strong>#{reviewModalSplit.source_family_id}</strong> ({reviewModalSplit.moved_person_ids.length} members moving).
                </p>
                <div className="mt-2 p-2 bg-red-50 text-red-800 border border-red-200 rounded text-[11px]">
                  <strong>Risk Anomaly Score:</strong> {reviewModalSplit.anomaly_score} / 100
                  {reviewModalSplit.anomaly_reasons && reviewModalSplit.anomaly_reasons.length > 0 && (
                    <div className="mt-1">
                      {reviewModalSplit.anomaly_reasons.map((r: string, idx: number) => (
                        <div key={idx}>• {r}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Decision</label>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-1.5 font-bold text-emerald-700 cursor-pointer">
                    <input
                      type="radio"
                      name="splitDecision"
                      value="OFFICER_APPROVED"
                      checked={splitAction === 'OFFICER_APPROVED'}
                      onChange={() => setSplitAction('OFFICER_APPROVED')}
                    />
                    Approve Household Split
                  </label>
                  <label className="flex items-center gap-1.5 font-bold text-red-700 cursor-pointer">
                    <input
                      type="radio"
                      name="splitDecision"
                      value="OFFICER_REJECTED"
                      checked={splitAction === 'OFFICER_REJECTED'}
                      onChange={() => setSplitAction('OFFICER_REJECTED')}
                    />
                    Reject Split Request
                  </label>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Officer Justification Notes</label>
                <textarea
                  rows={3}
                  value={splitNotes}
                  onChange={(e) => setSplitNotes(e.target.value)}
                  placeholder="Enter officer notes..."
                  className="w-full p-2 border border-slate-300 rounded bg-white text-slate-900 focus:ring-1 focus:ring-gov-navy focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button type="button" onClick={() => setReviewModalSplit(null)} className="px-3 py-1.5 border border-slate-300 rounded bg-white text-slate-700 font-semibold hover:bg-slate-50 transition-colors">Cancel</button>
                <button type="submit" disabled={splitReviewMutation.isPending} className="px-4 py-1.5 rounded bg-gov-navy hover:bg-slate-800 text-white font-bold transition-colors">Submit Split Review</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DOCUMENT QUEUE LIST */}
      {activeQueue === 'DOCUMENTS' && (
        <div className="space-y-3">
          {isDocLoading ? (
            <div className="py-8 text-center text-xs text-slate-500">Loading document verification queue...</div>
          ) : docQueue.length === 0 ? (
            <div className="gov-card p-8 text-center text-xs text-slate-500">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="font-bold text-slate-700">No Pending Document Verifications</p>
              <p className="text-slate-500">All submitted citizen certificates in your jurisdiction are up to date.</p>
            </div>
          ) : (
            <div className="gov-card divide-y divide-slate-100">
              {docQueue.map((doc: any) => (
                <div key={doc.document_id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-gov-navy">{doc.document_type.replace(/_/g, ' ')}</span>
                      <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        Family #{doc.family_id}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-slate-500">
                      <span>Ref No: <strong className="font-mono text-slate-800">{doc.document_number}</strong></span>
                      <span>•</span>
                      <span>Authority: {doc.issuing_authority}</span>
                      <span>•</span>
                      <span>Issued: {doc.issue_date}</span>
                    </div>

                    <div className="text-[11px] text-slate-400 font-mono">
                      Path: {doc.file_path}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleApproveDoc(doc.document_id)}
                      disabled={docVerifyMutation.isPending}
                      className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1 shadow-xs"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" /> Approve Certificate
                    </button>
                    <button
                      onClick={() => setRejectModalDoc(doc)}
                      disabled={docVerifyMutation.isPending}
                      className="px-3 py-1.5 rounded bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 font-bold text-xs flex items-center gap-1"
                    >
                      <XCircle className="w-3.5 h-3.5" /> Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ELIGIBILITY QUEUE LIST */}
      {activeQueue === 'ELIGIBILITY' && (
        <div className="space-y-3">
          {isEligLoading ? (
            <div className="py-8 text-center text-xs text-slate-500">Loading eligibility review queue...</div>
          ) : eligQueue.length === 0 ? (
            <div className="gov-card p-8 text-center text-xs text-slate-500">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="font-bold text-slate-700">No Scheme Eligibility Reviews Pending</p>
              <p className="text-slate-500">No applications or document flags require officer confirmation.</p>
            </div>
          ) : (
            <div className="gov-card divide-y divide-slate-100">
              {eligQueue.map((item: any) => (
                <div key={item.record_id || `${item.family_id}-${item.scheme_id}`} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-gov-navy">{item.scheme_name}</span>
                      <span className="font-mono text-xs px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                        {item.status}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-slate-500">
                      <span>Household Head: <strong>{item.head_name}</strong></span>
                      <span>•</span>
                      <span>Family ID: <strong className="font-mono text-slate-700">#{item.family_id}</strong></span>
                    </div>

                    {item.missing_documents && item.missing_documents.length > 0 && (
                      <div className="text-[11px] text-amber-700 font-semibold">
                        Missing Required Documents: {item.missing_documents.join(', ')}
                      </div>
                    )}
                  </div>

                  <div>
                    <button
                      onClick={() => setReviewModalEligibility(item)}
                      className="px-3.5 py-1.5 rounded bg-gov-navy hover:bg-slate-800 text-white font-bold text-xs flex items-center gap-1.5"
                    >
                      <MessageSquare className="w-3.5 h-3.5 text-saffron" /> Review & Action
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* HOUSEHOLD SPLIT QUEUE LIST */}
      {activeQueue === 'SPLITS' && (
        <div className="space-y-3">
          {isSplitLoading ? (
            <div className="py-8 text-center text-xs text-slate-500">Loading household split reviews...</div>
          ) : splitQueue.length === 0 ? (
            <div className="gov-card p-8 text-center text-xs text-slate-500">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="font-bold text-slate-700">No High-Risk Household Splits Pending</p>
              <p className="text-slate-500">All household split requests in your jurisdiction are processed.</p>
            </div>
          ) : (
            <div className="gov-card divide-y divide-slate-100">
              {splitQueue.map((s: any) => (
                <div key={s.split_id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-gov-navy">Household Split #{s.split_id}</span>
                      <span className="font-mono text-xs px-2 py-0.5 rounded bg-red-100 text-red-800 font-bold border border-red-200">
                        Risk Score: {s.anomaly_score} / 100
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-slate-500">
                      <span>Source Family: <strong className="font-mono text-slate-800">#{s.source_family_id}</strong></span>
                      <span>•</span>
                      <span>Moving Members: <strong>{s.moved_person_ids.length}</strong></span>
                      <span>•</span>
                      <span>Reason: {s.split_reason || 'N/A'}</span>
                    </div>

                    {s.anomaly_reasons && s.anomaly_reasons.length > 0 && (
                      <div className="text-[11px] text-red-700 font-semibold bg-red-50 p-1.5 rounded border border-red-200">
                        Risk Flags: {s.anomaly_reasons.join(' | ')}
                      </div>
                    )}
                  </div>

                  <div>
                    <button
                      onClick={() => setReviewModalSplit(s)}
                      className="px-3.5 py-1.5 rounded bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs flex items-center gap-1.5"
                    >
                      <ShieldAlert className="w-3.5 h-3.5 text-saffron" /> Review Split Risk
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
