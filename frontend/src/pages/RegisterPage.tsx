import React from 'react';
import { RegisterStepper } from '../components/RegisterStepper';
import { UserPlus } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-8 space-y-6">
      <div className="gov-card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-saffron" />
            <h1 className="text-xl font-bold text-gov-navy">Register New Household (નવું કુટુંબ નોંધણી)</h1>
          </div>
          <p className="text-xs text-slate-500">
            Submit your family details to receive a unique 12-digit Gujarat Family ID and unlock entitlement checking.
          </p>
        </div>
      </div>

      <RegisterStepper />
    </div>
  );
};
