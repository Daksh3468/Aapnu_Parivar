import React, { useState } from 'react';
import { formatFamilyId, validateFamilyId } from '../utils/familyId';
import { CheckCircle2, AlertCircle, Shield } from 'lucide-react';

interface FamilyIdInputProps {
  value: string;
  onChange: (value: string, isValid: boolean) => void;
  placeholder?: string;
  className?: string;
}

export const FamilyIdInput: React.FC<FamilyIdInputProps> = ({
  value,
  onChange,
  placeholder = 'GJ-07-26-4831927-1',
  className = '',
}) => {
  const [touched, setTouched] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatFamilyId(e.target.value);
    const validation = validateFamilyId(formatted);
    onChange(formatted, validation.isValid);
  };

  const validation = validateFamilyId(value);
  const showError = touched && value.length > 0 && !validation.isValid;
  const showSuccess = value.length > 0 && validation.isValid;

  return (
    <div className={`space-y-1.5 ${className}`}>
      <label className="block text-xs font-bold text-gov-navy uppercase tracking-wider">
        Gujarat Family ID (૧૨ અંકનો ફેમિલી આઈડી)
      </label>
      
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={handleChange}
          onBlur={() => setTouched(true)}
          placeholder={placeholder}
          maxLength={18}
          className={`w-full pl-10 pr-10 py-2.5 bg-white border rounded-md font-mono text-sm font-semibold tracking-wider uppercase transition-colors focus:outline-none focus:ring-2 ${
            showError
              ? 'border-red-500 text-red-900 focus:ring-red-500/20'
              : showSuccess
              ? 'border-emerald-500 text-slate-900 focus:ring-emerald-500/20'
              : 'border-slate-300 text-slate-900 focus:border-gov-blue focus:ring-gov-blue/20'
          }`}
        />
        
        <Shield className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />

        {showSuccess && (
          <CheckCircle2 className="w-5 h-5 text-emerald-600 absolute right-3 top-3" />
        )}
        
        {showError && (
          <AlertCircle className="w-5 h-5 text-red-500 absolute right-3 top-3" />
        )}
      </div>

      {showError && (
        <p className="text-xs text-red-600 font-medium flex items-center gap-1">
          <span>{validation.error}</span>
        </p>
      )}

      {showSuccess && (
        <p className="text-xs text-emerald-700 font-medium flex items-center gap-1">
          <span>Verhoeff Check Digit Verified ✓</span>
        </p>
      )}
    </div>
  );
};
