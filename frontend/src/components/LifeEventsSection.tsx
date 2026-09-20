import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { History, Calendar, User, Plus, AlertCircle, Sparkles, Layers } from 'lucide-react';


interface LifeEventsSectionProps {
  familyId: string;
  members: Array<{ person_id: string; full_name: string }>;
}

export const LifeEventsSection: React.FC<LifeEventsSectionProps> = ({ familyId, members }) => {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [eventType, setEventType] = useState('BIRTH');
  const [personId, setPersonId] = useState('');
  const [eventDate, setEventDate] = useState(new Date().toISOString().split('T')[0]);
  const [description, setDescription] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: events = [], isLoading, isError } = useQuery({
    queryKey: ['family-life-events', familyId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${familyId}/life-events`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load life events timeline');
      return res.json();
    },
  });

  const registerMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/v1/families/${familyId}/life-events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          person_id: personId || undefined,
          event_type: eventType,
          event_date: eventDate,
          description: description || undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to register life event');
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['family-life-events', familyId] });
      queryClient.invalidateQueries({ queryKey: ['my-family'] });
      setShowModal(false);
      setDescription('');
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || 'Error recording event');
    },
  });

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'BIRTH':
        return <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold">BIRTH (જન્મ)</span>;
      case 'DEATH':
        return <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-300 text-[10px] font-bold">DEATH (અવસાન)</span>;
      case 'MARRIAGE_OUT':
      case 'MARRIAGE_IN':
        return <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-bold">MARRIAGE (લગ્ન)</span>;
      case 'HOUSEHOLD_SPLIT':
        return <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold">HOUSEHOLD SPLIT (વિભાજન)</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold">{type}</span>;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded border border-slate-200 shadow-sm">
        <div>
          <h3 className="text-base font-bold text-gov-navy flex items-center gap-2">
            <History className="w-5 h-5 text-gov-navy" />
            Immutable Life Events & Household Lineage Timeline
          </h3>
          <p className="text-xs text-slate-500">
            Audit-tracked chronicle of births, marriages, deaths, and household splits linked to Gujarat State Registry.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-3.5 py-2 rounded bg-gov-navy hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register Life Event</span>
        </button>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full overflow-hidden">
            <div className="bg-gov-navy px-5 py-3 text-white flex items-center justify-between">
              <h4 className="font-bold text-sm flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-saffron" />
                Record Household Life Event
              </h4>
              <button onClick={() => setShowModal(false)} className="text-slate-300 hover:text-white font-bold text-lg leading-none">&times;</button>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); registerMutation.mutate(); }} className="p-5 space-y-4 text-xs">
              {errorMsg && (
                <div className="p-2.5 rounded bg-red-50 text-red-700 border border-red-200 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Event Type *</label>
                <select
                  value={eventType}
                  onChange={(e) => setEventType(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white font-medium text-slate-900 focus:ring-1 focus:ring-gov-navy"
                >
                  <option value="BIRTH" className="bg-white text-slate-900">Child Birth (જન્મ)</option>
                  <option value="DEATH" className="bg-white text-slate-900">Decease / Demise (અવસાન)</option>
                  <option value="MARRIAGE_OUT" className="bg-white text-slate-900">Marriage (Daughter/Son Moving Out)</option>
                  <option value="MARRIAGE_IN" className="bg-white text-slate-900">Marriage (New Member Joining Household)</option>
                  <option value="ADDRESS_CHANGE" className="bg-white text-slate-900">Residential Relocation / Address Update</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Affected Household Member (Optional)</label>
                <select
                  value={personId}
                  onChange={(e) => setPersonId(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white font-medium text-slate-900 focus:ring-1 focus:ring-gov-navy"
                >
                  <option value="" className="bg-white text-slate-900">-- Household Level Event --</option>
                  {members.map((m) => (
                    <option key={m.person_id} value={m.person_id} className="bg-white text-slate-900">
                      {m.full_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Event Date *</label>
                <input
                  type="date"
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-gov-navy"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Certificate / Description Reference</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. Birth Certificate No. GJ-BIRTH-2026-9912 or Tahsildar Notice Ref"
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-gov-navy"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
                <button type="button" onClick={() => setShowModal(false)} className="px-3.5 py-1.5 rounded border border-slate-300 text-slate-700 font-semibold">Cancel</button>
                <button type="submit" disabled={registerMutation.isPending} className="px-4 py-1.5 rounded bg-gov-navy text-white font-semibold">
                  {registerMutation.isPending ? 'Recording...' : 'Record Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Timeline List */}
      {isLoading ? (
        <div className="py-8 text-center text-xs text-slate-500">Loading life events chronicle...</div>
      ) : isError ? (
        <div className="p-4 rounded bg-red-50 text-red-700 text-xs">Failed to load timeline.</div>
      ) : events.length === 0 ? (
        <div className="gov-card p-8 text-center text-xs text-slate-500 space-y-1">
          <Layers className="w-8 h-8 text-slate-300 mx-auto" />
          <p className="font-bold text-slate-700">No Life Events Recorded Yet</p>
          <p className="text-slate-500">All birth, death, marriage, and household split events will appear here in chronological order.</p>
        </div>
      ) : (
        <div className="gov-card p-5 space-y-4">
          <div className="relative border-l-2 border-slate-200 ml-3 pl-6 space-y-6">
            {events.map((evt: any) => (
              <div key={evt.event_id} className="relative group">
                {/* Timeline node icon */}
                <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-white border-2 border-gov-navy flex items-center justify-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-saffron"></div>
                </div>

                <div className="bg-slate-50 p-3.5 rounded border border-slate-200 hover:border-slate-300 transition-colors space-y-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {getEventBadge(evt.event_type)}
                      {evt.person_name && (
                        <span className="font-bold text-xs text-gov-navy flex items-center gap-1">
                          <User className="w-3.5 h-3.5 text-slate-400" /> {evt.person_name}
                        </span>
                      )}
                    </div>

                    <span className="text-[11px] font-mono text-slate-500 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" /> {evt.event_date}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 font-medium">
                    {evt.description || 'Registered household milestone'}
                  </p>

                  <div className="text-[10px] text-slate-400 font-mono pt-1 border-t border-slate-100 flex items-center gap-2">
                    <span>Audit Ref #{evt.event_id}</span>
                    <span>•</span>
                    <span>Logged {new Date(evt.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
