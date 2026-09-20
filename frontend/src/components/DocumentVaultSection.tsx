import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Upload, CheckCircle2, Clock, XCircle, AlertCircle, Plus, FileCheck } from 'lucide-react';

interface DocumentVaultProps {
  familyId: string;
  members: Array<{ person_id: string; full_name: string }>;
}

export const DocumentVaultSection: React.FC<DocumentVaultProps> = ({ familyId, members }) => {
  const queryClient = useQueryClient();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [docType, setDocType] = useState('INCOME_CERTIFICATE');
  const [personId, setPersonId] = useState<string>('');
  const [docNumber, setDocNumber] = useState('');
  const [issuingAuth, setIssuingAuth] = useState('Revenue Department, Govt of Gujarat');
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split('T')[0]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: documents = [], isLoading, isError } = useQuery({
    queryKey: ['family-documents', familyId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${familyId}/documents`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load document vault');
      return res.json();
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${familyId}/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          person_id: personId || undefined,
          document_type: docType,
          document_number: docNumber,
          issuing_authority: issuingAuth,
          issue_date: issueDate,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to register document');
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['family-documents', familyId] });
      queryClient.invalidateQueries({ queryKey: ['family-eligibility', familyId] });
      setShowUploadModal(false);
      setDocNumber('');
      setErrorMessage(null);
    },
    onError: (err: any) => {
      setErrorMessage(err.message || 'Error registering document');
    },
  });

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!docNumber.trim()) {
      setErrorMessage('Please enter document certificate/reference number');
      return;
    }
    uploadMutation.mutate();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> VERIFIED
          </span>
        );
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
            <Clock className="w-3.5 h-3.5 text-amber-600" /> PENDING REVIEW
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded bg-red-50 text-red-700 border border-red-200">
            <XCircle className="w-3.5 h-3.5 text-red-600" /> REJECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Vault Header & Add Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded border border-slate-200 shadow-sm">
        <div>
          <h3 className="text-base font-bold text-gov-navy flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-gov-navy" />
            Digital Document Vault
          </h3>
          <p className="text-xs text-slate-500">
            Central repository of income, caste, land, and identity certificates for household eligibility validation.
          </p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="px-3.5 py-2 rounded bg-gov-navy hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Upload / Register Certificate</span>
        </button>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full overflow-hidden">
            <div className="bg-gov-navy px-5 py-3 text-white flex items-center justify-between">
              <h4 className="font-bold text-sm flex items-center gap-2">
                <Upload className="w-4 h-4 text-saffron" />
                Register Household Certificate
              </h4>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-300 hover:text-white font-bold text-lg leading-none"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="p-5 space-y-4 text-xs">
              {errorMessage && (
                <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Document Type *</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white font-medium text-slate-900 focus:ring-1 focus:ring-gov-navy"
                >
                  <option value="INCOME_CERTIFICATE" className="bg-white text-slate-900">Income Certificate (આવક દાખલો)</option>
                  <option value="CASTE_CERTIFICATE" className="bg-white text-slate-900">Caste / Social Category Certificate (જાતિ દાખલો)</option>
                  <option value="LAND_RECORD" className="bg-white text-slate-900">Land Ownership Record / 7/12 (જમીન રેકોર્ડ)</option>
                  <option value="DOMICILE_CERTIFICATE" className="bg-white text-slate-900">Gujarat Domicile Certificate (રહેવાસી પ્રમાણપત્ર)</option>
                  <option value="DISABILITY_CERTIFICATE" className="bg-white text-slate-900">Disability Certificate (દિવ્યાંગ પ્રમાણપત્ર)</option>
                  <option value="OTHER" className="bg-white text-slate-900">Other Official Document</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Target Member (Optional)</label>
                <select
                  value={personId}
                  onChange={(e) => setPersonId(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white font-medium text-slate-900 focus:ring-1 focus:ring-gov-navy"
                >
                  <option value="" className="bg-white text-slate-900">-- Entire Household / Head --</option>
                  {members.map((m) => (
                    <option key={m.person_id} value={m.person_id} className="bg-white text-slate-900">
                      {m.full_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Certificate / Document Reference Number *
                </label>
                <input
                  type="text"
                  placeholder="e.g. GJ-INC-2025-88491 or GJ-VERIFIED-991"
                  value={docNumber}
                  onChange={(e) => setDocNumber(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-gov-navy font-mono"
                  required
                />
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  Tip: Enter prefix <strong>GJ-VERIFIED-</strong> for auto-approval in demo mode.
                </span>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Issuing Authority</label>
                <input
                  type="text"
                  value={issuingAuth}
                  onChange={(e) => setIssuingAuth(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-gov-navy"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Issue Date</label>
                <input
                  type="date"
                  value={issueDate}
                  onChange={(e) => setIssueDate(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-gov-navy"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-3.5 py-1.5 rounded border border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploadMutation.isPending}
                  className="px-4 py-1.5 rounded bg-gov-navy hover:bg-slate-800 text-white font-semibold flex items-center gap-1.5"
                >
                  {uploadMutation.isPending ? 'Registering...' : 'Register Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Documents List */}
      {isLoading ? (
        <div className="py-8 text-center text-xs text-slate-500">Loading document vault...</div>
      ) : isError ? (
        <div className="p-4 rounded bg-red-50 text-red-700 text-xs">Failed to load document vault.</div>
      ) : documents.length === 0 ? (
        <div className="gov-card p-8 text-center space-y-2">
          <FileText className="w-8 h-8 text-slate-300 mx-auto" />
          <h4 className="text-sm font-bold text-gov-navy">No Documents Uploaded Yet</h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Upload income, caste, land, or domicile certificates to unlock automated scheme eligibility and officer confirmation queues.
          </p>
        </div>
      ) : (
        <div className="gov-card divide-y divide-slate-100">
          {documents.map((doc: any) => {
            const memberObj = members.find((m) => m.person_id === doc.person_id);

            return (
              <div key={doc.document_id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-gov-navy">{doc.document_type.replace(/_/g, ' ')}</span>
                    {getStatusBadge(doc.status)}
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span>Ref No: <strong className="font-mono text-slate-700">{doc.document_number}</strong></span>
                    <span>•</span>
                    <span>Issuing Auth: {doc.issuing_authority}</span>
                    <span>•</span>
                    <span>Issued: {doc.issue_date}</span>
                    {memberObj && (
                      <>
                        <span>•</span>
                        <span className="text-gov-navy font-medium">Holder: {memberObj.full_name}</span>
                      </>
                    )}
                  </div>

                  {doc.rejection_reason && (
                    <div className="mt-1 text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200">
                      <strong>Rejection Reason:</strong> {doc.rejection_reason}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                  <span className="px-2.5 py-1 bg-slate-100 rounded text-[11px] text-slate-600">
                    {doc.file_path}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
