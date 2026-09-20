import React from 'react';
import { Navigate, Link } from 'react-router-dom';
import { useAuth, isOfficerRole } from '../context/AuthContext';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const isOfficerRoute = allowedRoles.some((r) => isOfficerRole(r));
    const hasRole = isOfficerRoute ? isOfficerRole(user.role) : allowedRoles.includes(user.role);
    if (!hasRole) {
      return (
        <div className="max-w-2xl mx-auto py-12 text-center space-y-4">
          <div className="gov-card p-8 border-red-200 bg-red-50 text-red-900 space-y-4">
            <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 mx-auto flex items-center justify-center border border-red-200">
              <ShieldAlert className="w-7 h-7" />
            </div>

            <div className="space-y-1">
              <h2 className="text-xl font-bold text-red-900">Access Restricted: Officer Authorization Required</h2>
              <p className="text-xs text-red-700 max-w-md mx-auto leading-relaxed">
                The Departmental Administration Console and officer queues are restricted to verified Government Officers and District Administrators.
              </p>
            </div>

            <div className="pt-2 flex items-center justify-center gap-3">
              <Link
                to="/my-family"
                className="px-4 py-2 rounded bg-gov-navy hover:bg-slate-800 text-white text-xs font-bold inline-flex items-center gap-1.5 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Go to My Household Profile</span>
              </Link>
            </div>
          </div>
        </div>
      );
    }
  }

  return <>{children}</>;
};
