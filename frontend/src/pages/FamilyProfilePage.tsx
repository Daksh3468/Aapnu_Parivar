import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth, isOfficerRole } from '../context/AuthContext';
import { AlertCircle, RefreshCw, Users, Building, Shield, CheckCircle2, UserCheck, Phone, FileCheck, Award, Send, History, Layers, Building2, ArrowRight, KeyRound } from 'lucide-react';
import { VerifyMemberModal } from '../components/VerifyMemberModal';
import { DocumentVaultSection } from '../components/DocumentVaultSection';
import { SchemeEligibilitySection } from '../components/SchemeEligibilitySection';
import { ApplicationsSection } from '../components/ApplicationsSection';
import { LifeEventsSection } from '../components/LifeEventsSection';
import { FamilySplitWizardModal } from '../components/FamilySplitWizardModal';
import { ChangePasswordModal } from '../components/ChangePasswordModal';

export const FamilyProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const isOfficer = user && isOfficerRole(user.role);
  const [selectedMember, setSelectedMember] = useState<{ id: string; name: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'PROFILE' | 'VAULT' | 'ELIGIBILITY' | 'APPLICATIONS' | 'LIFE_EVENTS'>('PROFILE');
  const [showSplitModal, setShowSplitModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  useEffect(() => {
    if (searchParams.get('action') === 'split' || searchParams.get('split') === 'true') {
      setShowSplitModal(true);
    }
  }, [searchParams]);

  const { data: family, isLoading, isError, refetch } = useQuery({
    queryKey: ['my-family'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('Not authenticated');
      const res = await fetch('/api/v1/families/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to fetch family profile');
      }
      return res.json();
    },
  });

  if (isLoading) {
    return (
      <div className="py-12 text-center space-y-3">
        <RefreshCw className="w-6 h-6 animate-spin text-gov-navy mx-auto" />
        <p className="text-xs text-slate-500 font-medium">Loading household profile from Gujarat registry...</p>
      </div>
    );
  }

  if (isError || !family) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <div className="gov-card p-6 border-red-200 bg-red-50 text-red-800 space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span>No Active Household Profile Found</span>
          </div>
          <p className="text-xs text-red-700">
            You do not currently have an active household profile. Please register a new family or claim an existing account.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 py-6 max-w-5xl mx-auto">

      {/* Officer Console Navigation Banner */}
      {isOfficer && (
        <div className="gov-card p-4 bg-slate-900 text-white flex flex-col sm:flex-row items-center justify-between gap-3 border-l-4 border-saffron">
          <div className="flex items-center gap-2 text-xs">
            <Building2 className="w-5 h-5 text-saffron shrink-0" />
            <span>You are logged in as a <strong>Department Officer ({user?.login_id})</strong>. Access verification queues and district stats in the Department Console.</span>
          </div>
          <Link
            to="/officer"
            className="px-4 py-2 rounded-lg bg-gov-blue hover:bg-gov-hover text-white text-xs font-bold shrink-0 flex items-center gap-1.5 shadow-md"
          >
            <span>Go to Department Console</span>
            <ArrowRight className="w-4 h-4 text-saffron" />
          </Link>
        </div>
      )}
      {/* Verify Member Modal */}
      {selectedMember && (
        <VerifyMemberModal
          personId={selectedMember.id}
          memberName={selectedMember.name}
          onClose={() => setSelectedMember(null)}
          onSuccess={() => refetch()}
        />
      )}

      {/* Household Split Wizard Modal */}
      {showSplitModal && (
        <FamilySplitWizardModal
          sourceFamilyId={family.family_id}
          members={family.members.map((m: any) => ({
            person_id: m.person_id,
            full_name: m.full_name,
            role_in_family: m.role_in_family,
          }))}
          onClose={() => {
            setShowSplitModal(false);
            refetch();
          }}
        />
      )}

      {/* Change Password Modal */}
      {showPasswordModal && (
        <ChangePasswordModal onClose={() => setShowPasswordModal(false)} />
      )}

      {/* Family Card Header */}
      <div className="gov-card overflow-hidden">
        <div className="gov-tricolor-stripe"></div>
        <div className="p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-saffron" />
                <span className="font-mono font-extrabold text-xl text-gov-navy tracking-wider">{family.family_id}</span>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {family.status}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Registered Household Identity • Gujarat State Registry</p>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 text-xs bg-slate-50 px-3 py-2 rounded border border-slate-200">
                <Building className="w-4 h-4 text-gov-blue" />
                <span>District Code: <strong>#{family.address.district_code} ({family.address.district_name})</strong></span>
              </div>
              <button
                onClick={() => setShowPasswordModal(true)}
                className="px-3 py-2 rounded bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 text-xs font-bold flex items-center gap-1.5 transition-colors"
                title="Change Account Password"
              >
                <KeyRound className="w-3.5 h-3.5 text-saffron" />
                <span>Change Password</span>
              </button>
              <button
                onClick={() => setShowSplitModal(true)}
                className="px-3 py-2 rounded bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 text-xs font-bold flex items-center gap-1.5 transition-colors"
                title="Split Household into a New Family Identity"
              >
                <Layers className="w-3.5 h-3.5 text-gov-navy" />
                <span>Split Household</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Family Head</span>
              <strong className="text-sm text-gov-navy">{family.head_name}</strong>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Ration Card & Income Band</span>
              <strong className="text-sm text-gov-navy">{family.ration_card_type} • {family.income_band}</strong>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Residential Address</span>
              <strong className="text-xs text-slate-800">{family.address.line1}, {family.address.village_or_town} ({family.address.pincode})</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-1.5 bg-slate-200/90 p-1.5 rounded-xl border border-slate-300">
        <button
          onClick={() => setActiveTab('PROFILE')}
          className={`px-4 py-2.5 text-xs font-extrabold flex items-center gap-2 rounded-lg transition-all ${
            activeTab === 'PROFILE'
              ? 'tab-active ring-1 ring-slate-900'
              : 'tab-inactive'
          }`}
        >
          {activeTab === 'PROFILE' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
          <Users className={`w-4 h-4 ${activeTab === 'PROFILE' ? 'text-saffron' : 'text-slate-500'}`} />
          <span>Household Members ({family.member_count})</span>
        </button>

        <button
          onClick={() => setActiveTab('VAULT')}
          className={`px-4 py-2.5 text-xs font-extrabold flex items-center gap-2 rounded-lg transition-all ${
            activeTab === 'VAULT'
              ? 'tab-active ring-1 ring-slate-900'
              : 'tab-inactive'
          }`}
        >
          {activeTab === 'VAULT' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
          <FileCheck className={`w-4 h-4 ${activeTab === 'VAULT' ? 'text-saffron' : 'text-slate-500'}`} />
          <span>Document Vault</span>
        </button>

        <button
          onClick={() => setActiveTab('ELIGIBILITY')}
          className={`px-4 py-2.5 text-xs font-extrabold flex items-center gap-2 rounded-lg transition-all ${
            activeTab === 'ELIGIBILITY'
              ? 'tab-active ring-1 ring-slate-900'
              : 'tab-inactive'
          }`}
        >
          {activeTab === 'ELIGIBILITY' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
          <Award className={`w-4 h-4 ${activeTab === 'ELIGIBILITY' ? 'text-saffron' : 'text-slate-500'}`} />
          <span>Scheme Entitlements</span>
        </button>

        <button
          onClick={() => setActiveTab('APPLICATIONS')}
          className={`px-4 py-2.5 text-xs font-extrabold flex items-center gap-2 rounded-lg transition-all ${
            activeTab === 'APPLICATIONS'
              ? 'tab-active ring-1 ring-slate-900'
              : 'tab-inactive'
          }`}
        >
          {activeTab === 'APPLICATIONS' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
          <Send className={`w-4 h-4 ${activeTab === 'APPLICATIONS' ? 'text-saffron' : 'text-slate-500'}`} />
          <span>Applications</span>
        </button>

        <button
          onClick={() => setActiveTab('LIFE_EVENTS')}
          className={`px-4 py-2.5 text-xs font-extrabold flex items-center gap-2 rounded-lg transition-all ${
            activeTab === 'LIFE_EVENTS'
              ? 'tab-active ring-1 ring-slate-900'
              : 'tab-inactive'
          }`}
        >
          {activeTab === 'LIFE_EVENTS' && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse" />}
          <History className={`w-4 h-4 ${activeTab === 'LIFE_EVENTS' ? 'text-saffron' : 'text-slate-500'}`} />
          <span>Life Events & Lineage</span>
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'PROFILE' && (
        <div className="gov-card divide-y divide-slate-100">
          {family.members.map((m: any) => {
            const isVerified = m.verification_status === 'VERIFIED';

            return (
              <div key={m.person_id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-gov-navy">{m.full_name}</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                      {m.relation_to_head}
                    </span>
                    {m.role_in_family === 'HEAD' && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                        HEAD OF FAMILY
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span>Gender: {m.gender}</span>
                    <span>•</span>
                    <span>DOB: {m.dob}</span>
                    {m.mobile_masked && (
                      <>
                        <span>•</span>
                        <span className="flex items-center gap-1"><Phone className="w-3 h-3 text-slate-400" /> {m.mobile_masked}</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {isVerified ? (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>e-KYC VERIFIED ({m.aadhaar_last4})</span>
                    </div>
                  ) : (
                    <button
                      onClick={() => setSelectedMember({ id: m.person_id, name: m.full_name })}
                      className="px-3 py-1.5 rounded bg-saffron hover:bg-saffron-dark text-white text-xs font-semibold flex items-center gap-1 shadow-sm transition-colors"
                    >
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>Verify via Aadhaar</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'VAULT' && (
        <DocumentVaultSection
          familyId={family.family_id}
          members={family.members.map((m: any) => ({ person_id: m.person_id, full_name: m.full_name }))}
        />
      )}

      {activeTab === 'ELIGIBILITY' && (
        <SchemeEligibilitySection familyId={family.family_id} />
      )}

      {activeTab === 'APPLICATIONS' && (
        <ApplicationsSection familyId={family.family_id} />
      )}

      {activeTab === 'LIFE_EVENTS' && (
        <LifeEventsSection
          familyId={family.family_id}
          members={family.members.map((m: any) => ({ person_id: m.person_id, full_name: m.full_name }))}
        />
      )}
    </div>
  );
};
