import React, { useState } from 'react';
import { User, Users, MapPin, Building, ShieldCheck, Plus, Trash2, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle, KeyRound } from 'lucide-react';
import { RegistrationSuccessModal } from './RegistrationSuccessModal';

const GUJARAT_DISTRICTS = [
  { code: 1, name: 'Ahmedabad' },
  { code: 2, name: 'Amreli' },
  { code: 3, name: 'Anand' },
  { code: 4, name: 'Aravalli' },
  { code: 5, name: 'Banaskantha' },
  { code: 6, name: 'Bharuch' },
  { code: 7, name: 'Bhavnagar' },
  { code: 8, name: 'Botad' },
  { code: 9, name: 'Chhota Udaipur' },
  { code: 10, name: 'Dahod' },
  { code: 11, name: 'Dang' },
  { code: 12, name: 'Devbhumi Dwarka' },
  { code: 13, name: 'Gandhinagar' },
  { code: 14, name: 'Gir Somnath' },
  { code: 15, name: 'Jamnagar' },
  { code: 16, name: 'Junagadh' },
  { code: 17, name: 'Kheda' },
  { code: 18, name: 'Kutch' },
  { code: 19, name: 'Mahisagar' },
  { code: 20, name: 'Mehsana' },
  { code: 21, name: 'Morbi' },
  { code: 22, name: 'Narmada' },
  { code: 23, name: 'Navsari' },
  { code: 24, name: 'Panchmahal' },
  { code: 25, name: 'Patan' },
  { code: 26, name: 'Porbandar' },
  { code: 27, name: 'Rajkot' },
  { code: 28, name: 'Sabarkantha' },
  { code: 29, name: 'Surat' },
  { code: 30, name: 'Surendranagar' },
  { code: 31, name: 'Tapi' },
  { code: 32, name: 'Vadodara' },
  { code: 33, name: 'Valsad' },
];

export const RegisterStepper: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);

  // Form State
  const [head, setHead] = useState({
    full_name: 'Rameshbhai Patel',
    dob: '1980-05-15',
    gender: 'MALE',
    marital_status: 'MARRIED',
    mobile: '9876500001',
    relation_to_head: 'SELF',
    social_category: 'GENERAL',
    education_level: 'GRADUATE',
    occupation_type: 'FARMER',
    has_bank_account: true,
  });

  const [members, setMembers] = useState<any[]>([
    {
      full_name: 'Savitaben Patel',
      dob: '1984-08-20',
      gender: 'FEMALE',
      marital_status: 'MARRIED',
      mobile: '9876500002',
      relation_to_head: 'SPOUSE',
      social_category: 'GENERAL',
      education_level: 'SECONDARY',
      occupation_type: 'HOMEMAKER',
      has_bank_account: true,
    },
  ]);

  const [address, setAddress] = useState({
    line1: '101, Shanti Tower, Sector-11',
    village_or_town: 'Bhavnagar',
    taluka: 'Bhavnagar City',
    district_code: 7,
    pincode: '364001',
  });

  const [attributes, setAttributes] = useState({
    ration_card_type: 'PHH',
    ration_card_number: 'GJ0712345678',
    income_band: '1L_2_5L',
    land_holding_acres: 2.5,
    house_type: 'PUCCA',
    house_owned: true,
    has_lpg_connection: true,
    primary_occupation: 'FARMER',
    consent_given: true,
  });

  const [password, setPassword] = useState('Gujarat@123');
  const [confirmPassword, setConfirmPassword] = useState('Gujarat@123');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successResult, setSuccessResult] = useState<any | null>(null);

  const handleAddMember = () => {
    setMembers([
      ...members,
      {
        full_name: '',
        dob: '2010-01-01',
        gender: 'MALE',
        marital_status: 'UNMARRIED',
        relation_to_head: 'SON',
        social_category: 'GENERAL',
        education_level: 'PRIMARY',
        occupation_type: 'OTHER',
        has_bank_account: false,
      },
    ]);
  };

  const handleRemoveMember = (index: number) => {
    setMembers(members.filter((_, i) => i !== index));
  };

  const handleMemberChange = (index: number, field: string, value: any) => {
    const updated = [...members];
    updated[index][field] = value;
    setMembers(updated);
  };

  const handleSubmitRegistration = async () => {
    setError(null);

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Password and Confirm Password do not match.');
      return;
    }

    setLoading(true);

    try {
      const payload = {
        address,
        head: { ...head, is_head: true },
        members,
        password,
        ...attributes,
      };

      const res = await fetch('/api/v1/families', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'Registration failed');

      setSuccessResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { title: 'Family Head', icon: User },
    { title: 'Members', icon: Users },
    { title: 'Address', icon: MapPin },
    { title: 'Household Attributes', icon: Building },
    { title: 'Review & Submit', icon: ShieldCheck },
  ];

  return (
    <div className="space-y-6">
      {/* Success Modal */}
      {successResult && (
        <RegistrationSuccessModal
          familyId={successResult.family_id}
          headName={successResult.head_name}
          memberCount={successResult.member_count}
          onClose={() => setSuccessResult(null)}
        />
      )}

      {/* Stepper Progress Indicator */}
      <div className="gov-card p-4">
        <div className="flex items-center justify-between">
          {steps.map((s, idx) => {
            const stepNum = idx + 1;
            const Icon = s.icon;
            const isActive = currentStep === stepNum;
            const isDone = currentStep > stepNum;

            return (
              <React.Fragment key={idx}>
                <div className="flex items-center gap-2">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                      isDone
                        ? 'bg-emerald-600 text-white'
                        : isActive
                        ? 'bg-gov-navy text-white shadow-sm'
                        : 'bg-slate-100 text-slate-500 border border-slate-300'
                    }`}
                  >
                    {isDone ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                  </div>
                  <span className={`text-xs font-semibold hidden md:inline ${isActive ? 'text-gov-navy font-bold' : 'text-slate-500'}`}>
                    {s.title}
                  </span>
                </div>
                {idx < steps.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-2 ${currentStep > stepNum ? 'bg-emerald-500' : 'bg-slate-200'}`}></div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Form Content Step by Step */}
      <div className="gov-card p-6">
        {/* Step 1: Head Details */}
        {currentStep === 1 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold text-gov-navy border-b border-slate-100 pb-2">
              Step 1: Family Head Personal & Identity Details (પરિવારના વડાની વિગત)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Full Name (પૂરું નામ)</label>
                <input
                  type="text"
                  value={head.full_name}
                  onChange={(e) => setHead({ ...head, full_name: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900 focus:ring-2 focus:ring-gov-blue"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Date of Birth (જન્મ તારીખ)</label>
                <input
                  type="date"
                  value={head.dob}
                  onChange={(e) => setHead({ ...head, dob: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900 focus:ring-2 focus:ring-gov-blue"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Gender (જાતિ)</label>
                <select
                  value={head.gender}
                  onChange={(e) => setHead({ ...head, gender: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900"
                >
                  <option value="MALE" className="bg-white text-slate-900">Male (પુરુષ)</option>
                  <option value="FEMALE" className="bg-white text-slate-900">Female (સ્ત્રી)</option>
                  <option value="OTHER" className="bg-white text-slate-900">Other (અન્ય)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Mobile Number (મોબાઈલ)</label>
                <input
                  type="text"
                  value={head.mobile}
                  onChange={(e) => setHead({ ...head, mobile: e.target.value })}
                  maxLength={10}
                  className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Social Category (સામાજિક કેટેગરી)</label>
                <select
                  value={head.social_category}
                  onChange={(e) => setHead({ ...head, social_category: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900"
                >
                  <option value="GENERAL" className="bg-white text-slate-900">General</option>
                  <option value="SC" className="bg-white text-slate-900">SC (Scheduled Caste)</option>
                  <option value="ST" className="bg-white text-slate-900">ST (Scheduled Tribe)</option>
                  <option value="SEBC" className="bg-white text-slate-900">SEBC / OBC</option>
                  <option value="EWS" className="bg-white text-slate-900">EWS</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Education Level (શિક્ષણ)</label>
                <select
                  value={head.education_level}
                  onChange={(e) => setHead({ ...head, education_level: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900"
                >
                  <option value="NONE" className="bg-white text-slate-900">Illiterate / Primary</option>
                  <option value="SECONDARY" className="bg-white text-slate-900">Secondary (10th)</option>
                  <option value="HIGHER_SECONDARY" className="bg-white text-slate-900">Higher Secondary (12th)</option>
                  <option value="GRADUATE" className="bg-white text-slate-900">Graduate / College</option>
                  <option value="DIPLOMA_ITI" className="bg-white text-slate-900">Diploma / ITI</option>
                </select>
              </div>

              {/* Account First-time Password Section */}
              <div className="md:col-span-2 p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-3">
                <div className="flex items-center gap-2 text-gov-navy font-bold text-xs border-b border-slate-200 pb-2">
                  <KeyRound className="w-4 h-4 text-saffron" />
                  <span>Set Login Password for Portal Access (પોર્ટલ માટે પાસવર્ડ સેટ કરો)</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Portal Login Password (પાસવર્ડ)</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Create login password (min 6 chars)"
                      minLength={6}
                      required
                      className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900 focus:ring-2 focus:ring-gov-blue text-xs font-mono"
                    />
                  </div>
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Confirm Password (પાસવર્ડ કન્ફર્મ કરો)</label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Re-enter login password"
                      minLength={6}
                      required
                      className="w-full p-2 bg-white border border-slate-300 rounded text-slate-900 focus:ring-2 focus:ring-gov-blue text-xs font-mono"
                    />
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 font-medium italic">
                  * Note: After registration, you will log into your Family Portal using your Head Mobile ({head.mobile || '10-digit mobile'}) and this password.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Household Members */}
        {currentStep === 2 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h2 className="text-base font-bold text-gov-navy">
                Step 2: Household Family Members (પરિવારના સભ્યો)
              </h2>
              <button
                type="button"
                onClick={handleAddMember}
                className="px-3 py-1.5 rounded bg-gov-blue text-white text-xs font-semibold flex items-center gap-1 hover:bg-gov-hover"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Member</span>
              </button>
            </div>

            {members.length === 0 ? (
              <p className="text-xs text-slate-500 italic py-4 text-center bg-slate-50 rounded">
                No additional members added. Only the head will be registered.
              </p>
            ) : (
              <div className="space-y-4">
                {members.map((m, idx) => (
                  <div key={idx} className="p-4 rounded border border-slate-200 bg-slate-50 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-gov-navy">Member #{idx + 1}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveMember(idx)}
                        className="text-red-600 hover:text-red-800 text-xs font-semibold flex items-center gap-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span>Remove</span>
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
                        <input
                          type="text"
                          value={m.full_name}
                          onChange={(e) => handleMemberChange(idx, 'full_name', e.target.value)}
                          placeholder="Member full name"
                          className="w-full p-2 bg-white border border-slate-300 rounded"
                          required
                        />
                      </div>

                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Relation to Head</label>
                        <select
                          value={m.relation_to_head}
                          onChange={(e) => handleMemberChange(idx, 'relation_to_head', e.target.value)}
                          className="w-full p-2 bg-white border border-slate-300 rounded"
                        >
                          <option value="SPOUSE" className="bg-white text-slate-900">Spouse (પતિ/પત્ની)</option>
                          <option value="SON" className="bg-white text-slate-900">Son (પુત્ર)</option>
                          <option value="DAUGHTER" className="bg-white text-slate-900">Daughter (પુત્રી)</option>
                          <option value="FATHER" className="bg-white text-slate-900">Father (પિતા)</option>
                          <option value="MOTHER" className="bg-white text-slate-900">Mother (માતા)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Date of Birth</label>
                        <input
                          type="date"
                          value={m.dob}
                          onChange={(e) => handleMemberChange(idx, 'dob', e.target.value)}
                          className="w-full p-2 bg-white border border-slate-300 rounded"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Address */}
        {currentStep === 3 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold text-gov-navy border-b border-slate-100 pb-2">
              Step 3: Residential Address & District (સરનામું અને જિલ્લો)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="md:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">Address Line 1 (મકાન નં. / શેરી)</label>
                <input
                  type="text"
                  value={address.line1}
                  onChange={(e) => setAddress({ ...address, line1: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Village / Town / City</label>
                <input
                  type="text"
                  value={address.village_or_town}
                  onChange={(e) => setAddress({ ...address, village_or_town: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Taluka (તાલુકો)</label>
                <input
                  type="text"
                  value={address.taluka}
                  onChange={(e) => setAddress({ ...address, taluka: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Gujarat District (જિલ્લો)</label>
                <select
                  value={address.district_code}
                  onChange={(e) => setAddress({ ...address, district_code: parseInt(e.target.value, 10) })}
                  className="w-full p-2 bg-white border border-slate-300 rounded font-semibold text-gov-navy"
                >
                  {GUJARAT_DISTRICTS.map((d) => (
                    <option key={d.code} value={d.code} className="bg-white text-slate-900">
                      {d.code < 10 ? `0${d.code}` : d.code} - {d.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Pincode (પિનકોડ)</label>
                <input
                  type="text"
                  value={address.pincode}
                  onChange={(e) => setAddress({ ...address, pincode: e.target.value })}
                  maxLength={6}
                  className="w-full p-2 bg-white border border-slate-300 rounded font-mono"
                  required
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Household Attributes */}
        {currentStep === 4 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold text-gov-navy border-b border-slate-100 pb-2">
              Step 4: Annual Income & Economic Attributes (આર્થિક વિગત)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Ration Card Category</label>
                <select
                  value={attributes.ration_card_type}
                  onChange={(e) => setAttributes({ ...attributes, ration_card_type: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded"
                >
                  <option value="AAY" className="bg-white text-slate-900">AAY (Antyodaya Anna Yojana)</option>
                  <option value="PHH" className="bg-white text-slate-900">PHH (Priority Household)</option>
                  <option value="NON_NFSA" className="bg-white text-slate-900">Non-NFSA Card</option>
                  <option value="NONE" className="bg-white text-slate-900">None</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Annual Household Income Band</label>
                <select
                  value={attributes.income_band}
                  onChange={(e) => setAttributes({ ...attributes, income_band: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded font-semibold text-gov-navy"
                >
                  <option value="LT_1L" className="bg-white text-slate-900">Less than ₹1 Lakh / year</option>
                  <option value="1L_2_5L" className="bg-white text-slate-900">₹1.0 Lakh - ₹2.5 Lakh / year</option>
                  <option value="2_5L_5L" className="bg-white text-slate-900">₹2.5 Lakh - ₹5.0 Lakh / year</option>
                  <option value="5L_8L" className="bg-white text-slate-900">₹5.0 Lakh - ₹8.0 Lakh / year</option>
                  <option value="GT_8L" className="bg-white text-slate-900">Greater than ₹8.0 Lakh / year</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Agricultural Land Holding (Acres)</label>
                <input
                  type="number"
                  step="0.1"
                  value={attributes.land_holding_acres}
                  onChange={(e) => setAttributes({ ...attributes, land_holding_acres: parseFloat(e.target.value) || 0 })}
                  className="w-full p-2 bg-white border border-slate-300 rounded"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">House Ownership Type</label>
                <select
                  value={attributes.house_type}
                  onChange={(e) => setAttributes({ ...attributes, house_type: e.target.value })}
                  className="w-full p-2 bg-white border border-slate-300 rounded"
                >
                  <option value="PUCCA" className="bg-white text-slate-900">Pucca (પાકું મકાન)</option>
                  <option value="SEMI_PUCCA" className="bg-white text-slate-900">Semi-Pucca</option>
                  <option value="KUCCHA" className="bg-white text-slate-900">Kuccha (કાચું મકાન)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Review & Submit */}
        {currentStep === 5 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold text-gov-navy border-b border-slate-100 pb-2">
              Step 5: Review Household Registration & Consent Declaration
            </h2>

            <div className="bg-slate-50 p-4 rounded border border-slate-200 text-xs space-y-3">
              <div className="flex items-center justify-between border-b pb-2">
                <span className="font-bold text-gov-navy">Family Head: {head.full_name}</span>
                <span className="text-slate-500">DOB: {head.dob}</span>
              </div>

              <div className="flex items-center justify-between border-b pb-2">
                <span className="font-bold text-gov-navy">District: Code #{address.district_code} ({address.village_or_town})</span>
                <span className="text-slate-500">Pincode: {address.pincode}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="font-bold text-gov-navy">Total Household Members: {1 + members.length}</span>
                <span className="text-slate-500">Income Band: {attributes.income_band}</span>
              </div>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-200 rounded text-xs space-y-2">
              <label className="flex items-start gap-2 cursor-pointer font-semibold text-amber-900">
                <input
                  type="checkbox"
                  checked={attributes.consent_given}
                  onChange={(e) => setAttributes({ ...attributes, consent_given: e.target.checked })}
                  className="mt-0.5"
                />
                <span>
                  I hereby declare that all household details provided above are true to the best of my knowledge. I consent to the issuance of a Gujarat Family ID under state welfare laws.
                </span>
              </label>
            </div>
          </div>
        )}

        {/* Stepper Navigation Buttons */}
        <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1 || loading}
            className="px-4 py-2 rounded bg-slate-100 text-slate-700 hover:bg-slate-200 disabled:opacity-50 text-xs font-semibold flex items-center gap-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Previous</span>
          </button>

          {currentStep < 5 ? (
            <button
              type="button"
              onClick={() => setCurrentStep(currentStep + 1)}
              className="px-5 py-2 rounded bg-gov-blue hover:bg-gov-hover text-white text-xs font-semibold flex items-center gap-1 shadow-sm"
            >
              <span>Next Step</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmitRegistration}
              disabled={loading || !attributes.consent_given}
              className="px-6 py-2.5 rounded bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 shadow-sm"
            >
              <span>{loading ? 'Submitting...' : 'Submit Registration'}</span>
              <CheckCircle2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
