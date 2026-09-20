import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Layers, CheckCircle2, AlertTriangle, ArrowRight, ArrowLeft } from 'lucide-react';


interface FamilySplitWizardProps {
  sourceFamilyId: string;
  members: Array<{ person_id: string; full_name: string; role_in_family: string }>;
  onClose: () => void;
}

export const FamilySplitWizardModal: React.FC<FamilySplitWizardProps> = ({ sourceFamilyId, members, onClose }) => {
  const queryClient = useQueryClient();
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);

  // Form State
  const [selectedMovedIds, setSelectedMovedIds] = useState<string[]>([]);
  const [newHeadId, setNewHeadId] = useState<string>('');
  const [replacementHeadId, setReplacementHeadId] = useState<string>('');
  const [splitReason, setSplitReason] = useState('Employment relocation and independent nuclear family establishment');
  const [line1, setLine1] = useState('Plot 42, Sector 12');
  const [village, setVillage] = useState('Gandhinagar');
  const [districtCode, setDistrictCode] = useState(7);
  const [pincode, setPincode] = useState('382010');

  const [splitResult, setSplitResult] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const currentHeadObj = members.find((m) => m.role_in_family === 'HEAD');
  const isCurrentHeadMoving = currentHeadObj && selectedMovedIds.includes(currentHeadObj.person_id);

  const toggleMemberSelection = (personId: string) => {
    if (selectedMovedIds.includes(personId)) {
      setSelectedMovedIds(selectedMovedIds.filter((id) => id !== personId));
      if (newHeadId === personId) setNewHeadId('');
    } else {
      const updated = [...selectedMovedIds, personId];
      setSelectedMovedIds(updated);
      if (updated.length === 1) setNewHeadId(personId);
    }
  };

  const splitMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${sourceFamilyId}/split`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          moved_person_ids: selectedMovedIds,
          new_head_person_id: newHeadId,
          replacement_source_head_person_id: isCurrentHeadMoving ? replacementHeadId : undefined,
          split_reason: splitReason,
          new_address: {
            line1,
            village_or_town: village,
            district_code: Number(districtCode),
            pincode,
          },
        }),
      });
      const text = await res.text();
      let data: any = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { detail: text || `Server error (${res.status} ${res.statusText})` };
      }

      if (!res.ok) {
        const msg = typeof data.detail === 'string' 
          ? data.detail 
          : (data.detail ? JSON.stringify(data.detail) : 'Failed to process household split');
        throw new Error(msg);
      }
      return data;
    },
    onSuccess: (data) => {
      setSplitResult(data);
      setStep(4);
      queryClient.invalidateQueries({ queryKey: ['my-family'] });
    },
    onError: (err: any) => {
      setErrorMsg(err.message || 'An error occurred during household split execution.');
    },
  });

  const handleStep1Next = () => {
    if (selectedMovedIds.length === 0) {
      setErrorMsg('Please select at least 1 member to move to the new household.');
      return;
    }
    if (selectedMovedIds.length === members.length) {
      setErrorMsg('Cannot move all members. At least 1 member must remain in source household.');
      return;
    }
    setErrorMsg(null);
    setStep(2);
  };

  const handleStep2Next = () => {
    if (!newHeadId) {
      setErrorMsg('Please designate a Head of Family for the new household.');
      return;
    }
    if (isCurrentHeadMoving && !replacementHeadId) {
      setErrorMsg('Since the current Household Head is moving out, you must select a Replacement Head for the source family.');
      return;
    }
    setErrorMsg(null);
    setStep(3);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!splitReason.trim()) {
      setErrorMsg('Please provide a justification reason for splitting the household.');
      return;
    }
    setErrorMsg(null);
    splitMutation.mutate();
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gov-navy px-5 py-3 text-white flex items-center justify-between">
          <h4 className="font-bold text-sm flex items-center gap-2">
            <Layers className="w-4 h-4 text-saffron" />
            Household Division & Lineage Split Wizard
          </h4>
          <button onClick={onClose} className="text-slate-300 hover:text-white font-bold text-lg leading-none">&times;</button>
        </div>

        {/* Stepper Header */}
        <div className="bg-slate-50 border-b border-slate-200 px-5 py-2.5 flex items-center justify-between text-xs font-bold text-slate-600">
          <span className={step === 1 ? 'text-gov-navy font-extrabold' : ''}>1. Select Members</span>
          <span>&rarr;</span>
          <span className={step === 2 ? 'text-gov-navy font-extrabold' : ''}>2. Designate Heads</span>
          <span>&rarr;</span>
          <span className={step === 3 ? 'text-gov-navy font-extrabold' : ''}>3. Address & Reason</span>
          <span>&rarr;</span>
          <span className={step === 4 ? 'text-gov-navy font-extrabold' : ''}>4. Result</span>
        </div>

        <div className="p-5 text-xs space-y-4">
          {errorMsg && (
            <div className="p-2.5 rounded bg-red-50 text-red-700 border border-red-200 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* STEP 1: Select Members */}
          {step === 1 && (
            <div className="space-y-3">
              <div>
                <h5 className="font-bold text-slate-800 text-sm">Step 1: Select Members Moving to New Household</h5>
                <p className="text-slate-500">Choose members who are leaving Family <strong>#{sourceFamilyId}</strong> to form a new registered family identity.</p>
              </div>

              <div className="divide-y divide-slate-100 border border-slate-200 rounded max-h-56 overflow-y-auto">
                {members.map((m) => {
                  const isSelected = selectedMovedIds.includes(m.person_id);
                  return (
                    <label key={m.person_id} className={`p-3 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors ${isSelected ? 'bg-blue-50/50' : ''}`}>
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleMemberSelection(m.person_id)}
                          className="rounded text-gov-navy focus:ring-gov-navy"
                        />
                        <div>
                          <span className="font-bold text-gov-navy">{m.full_name}</span>
                          <span className="text-[10px] ml-2 px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border">
                            {m.role_in_family}
                          </span>
                        </div>
                      </div>
                    </label>
                  );
                })}
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <span className="text-slate-500 font-semibold">{selectedMovedIds.length} member(s) selected</span>
                <button
                  type="button"
                  onClick={handleStep1Next}
                  className="px-4 py-2 rounded bg-gov-navy text-white font-bold flex items-center gap-1"
                >
                  <span>Next: Designate Heads</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Designate Heads */}
          {step === 2 && (
            <div className="space-y-4">
              <div>
                <h5 className="font-bold text-slate-800 text-sm">Step 2: Assign Household Heads</h5>
                <p className="text-slate-500">Assign a Head of Household for the new family and ensure the original family maintains a valid head.</p>
              </div>

              <div className="p-3 bg-slate-50 rounded border border-slate-200 space-y-2">
                <label className="block font-bold text-gov-navy mb-1">Head of NEW Household *</label>
                {members.filter((m) => selectedMovedIds.includes(m.person_id)).map((m) => (
                  <label key={m.person_id} className="flex items-center gap-2 cursor-pointer font-semibold text-slate-700">
                    <input
                      type="radio"
                      name="newHead"
                      value={m.person_id}
                      checked={newHeadId === m.person_id}
                      onChange={() => setNewHeadId(m.person_id)}
                    />
                    <span>{m.full_name}</span>
                  </label>
                ))}
              </div>

              {isCurrentHeadMoving && (
                <div className="p-3 bg-amber-50 rounded border border-amber-200 space-y-2">
                  <span className="font-bold text-amber-900 block flex items-center gap-1">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    Original Household Head is moving out!
                  </span>
                  <p className="text-amber-800 text-[11px]">
                    Select a Replacement Head of Household for remaining members in source family #{sourceFamilyId}:
                  </p>
                  {members.filter((m) => !selectedMovedIds.includes(m.person_id)).map((m) => (
                    <label key={m.person_id} className="flex items-center gap-2 cursor-pointer font-semibold text-slate-800">
                      <input
                        type="radio"
                        name="repHead"
                        value={m.person_id}
                        checked={replacementHeadId === m.person_id}
                        onChange={() => setReplacementHeadId(m.person_id)}
                      />
                      <span>{m.full_name}</span>
                    </label>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="px-3.5 py-1.5 rounded border border-slate-300 text-slate-700 font-semibold flex items-center gap-1"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>
                <button
                  type="button"
                  onClick={handleStep2Next}
                  className="px-4 py-2 rounded bg-gov-navy text-white font-bold flex items-center gap-1"
                >
                  <span>Next: Address & Reason</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Address & Reason */}
          {step === 3 && (
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <h5 className="font-bold text-slate-800 text-sm">Step 3: New Household Address & Justification</h5>
                <p className="text-slate-500">Provide residential details for the new family and justification for the split.</p>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Reason for Household Division *</label>
                <textarea
                  rows={2}
                  value={splitReason}
                  onChange={(e) => setSplitReason(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-gov-navy"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Street / House Address</label>
                  <input
                    type="text"
                    value={line1}
                    onChange={(e) => setLine1(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Village / City</label>
                  <input
                    type="text"
                    value={village}
                    onChange={(e) => setVillage(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">District Code (1-33)</label>
                  <input
                    type="number"
                    value={districtCode}
                    onChange={(e) => setDistrictCode(Number(e.target.value))}
                    className="w-full p-2 border border-slate-300 rounded font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Pincode</label>
                  <input
                    type="text"
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded font-mono"
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="px-3.5 py-1.5 rounded border border-slate-300 text-slate-700 font-semibold flex items-center gap-1"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>
                <button
                  type="submit"
                  disabled={splitMutation.isPending}
                  className="px-4 py-2 rounded bg-gov-navy hover:bg-slate-800 text-white font-bold flex items-center gap-1.5"
                >
                  {splitMutation.isPending ? 'Processing Split...' : 'Submit Household Split'}
                </button>
              </div>
            </form>
          )}

          {/* STEP 4: Result */}
          {step === 4 && splitResult && (
            <div className="space-y-4">
              <div className="p-4 rounded bg-emerald-50 border border-emerald-200 text-emerald-900 space-y-2">
                <div className="flex items-center gap-2 font-bold text-sm">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <span>Household Split Submission Completed!</span>
                </div>

                <div className="text-xs space-y-1">
                  <div>Split Reference ID: <strong className="font-mono">#{splitResult.split_id}</strong></div>
                  <div>Status: <strong className="uppercase">{splitResult.status}</strong></div>
                  {splitResult.new_family_id && (
                    <div className="font-bold text-gov-navy">
                      New Family Identity Issued: <span className="font-mono">{splitResult.new_family_id}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Anomaly Risk Score Badge */}
              <div className="p-3 bg-slate-50 rounded border border-slate-200 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-700">Risk Anomaly Score Evaluation:</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold font-mono ${
                    splitResult.anomaly_score > 50 ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'
                  }`}>
                    {splitResult.anomaly_score} / 100
                  </span>
                </div>

                {splitResult.anomaly_reasons && splitResult.anomaly_reasons.length > 0 ? (
                  <div className="space-y-1 text-red-700 text-[11px] pt-1">
                    <span className="font-semibold block">Risk Flags Identified:</span>
                    {splitResult.anomaly_reasons.map((r: string, idx: number) => (
                      <div key={idx}>• {r}</div>
                    ))}
                  </div>
                ) : (
                  <span className="text-emerald-700 text-[11px] font-medium block">No risk flags detected. Split verified low-risk.</span>
                )}
              </div>

              {splitResult.status === 'PENDING_OFFICER_REVIEW' && (
                <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded text-xs">
                  <strong>Notice:</strong> Due to an anomaly risk score &gt; 50, this household split requires manual verification by a Department Officer before taking final effect.
                </div>
              )}

              <div className="flex justify-end pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 bg-gov-navy text-white font-bold rounded"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
