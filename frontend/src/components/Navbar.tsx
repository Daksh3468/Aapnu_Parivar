import React from 'react';
import { Home, Building2, LogIn, LogOut, Layers, BarChart2, UserCheck } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth, isOfficerRole } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  
  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const isOfficer = isAuthenticated && user && isOfficerRole(user.role);
  const isCitizen = isAuthenticated && user && !isOfficer;

  const getNavLinkClass = (path: string) => {
    const active = isActive(path);
    return `flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
      active
        ? 'tab-active font-extrabold ring-1 ring-slate-900'
        : 'tab-inactive font-semibold'
    }`;
  };

  return (
    <nav className="bg-white border-b border-slate-200 shadow-xs sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Official Emblem & Branding with Official Logo Image */}
          <Link to="/" className="flex items-center gap-3.5 group">
            <img
              src="/logo.jpg"
              alt="Aapnu Parivar Logo"
              className="w-12 h-12 rounded-lg object-contain bg-white p-0.5 shadow-xs border border-slate-200 group-hover:scale-105 transition-transform"
            />

            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-gov-navy">
                  આપણું પરિવાર
                </span>
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                  Aapnu Parivar
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Unified Gujarat Household Identity & Welfare Beneficiary Portal
              </p>
            </div>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-2">
            
            {/* Common Home Link */}
            <Link to="/" className={getNavLinkClass('/')}>
              {isActive('/') && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse"></span>}
              <Home className={`w-4 h-4 ${isActive('/') ? 'text-saffron' : 'text-slate-500'}`} />
              <span>Portal Home</span>
            </Link>

            {/* Public Welfare Schemes */}
            <Link to="/schemes" className={getNavLinkClass('/schemes')}>
              {isActive('/schemes') && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse"></span>}
              <Layers className={`w-4 h-4 ${isActive('/schemes') ? 'text-saffron' : 'text-slate-500'}`} />
              <span>Welfare Schemes</span>
            </Link>

            {/* Citizen Specific Navigation */}
            {isCitizen && (
              <Link to="/my-family" className={getNavLinkClass('/my-family')}>
                {isActive('/my-family') && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse"></span>}
                <UserCheck className={`w-4 h-4 ${isActive('/my-family') ? 'text-saffron' : 'text-slate-500'}`} />
                <span>My Household & Applications</span>
              </Link>
            )}

            {/* Officer Specific Navigation */}
            {isOfficer && (
              <>
                <Link to="/officer" className={getNavLinkClass('/officer')}>
                  {isActive('/officer') && <span className="w-2 h-2 rounded-full bg-saffron animate-pulse"></span>}
                  <Building2 className={`w-4 h-4 ${isActive('/officer') ? 'text-saffron' : 'text-slate-500'}`} />
                  <span>Departmental Console</span>
                </Link>

                <Link to="/analytics" className={getNavLinkClass('/analytics')}>
                  {isActive('/analytics') && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>}
                  <BarChart2 className={`w-4 h-4 ${isActive('/analytics') ? 'text-emerald-400' : 'text-slate-500'}`} />
                  <span>Statewide Analytics</span>
                </Link>
              </>
            )}

            {/* Authentication Bar */}
            {isAuthenticated && user ? (
              <div className="flex items-center gap-2 ml-2 pl-2 border-l border-slate-200">
                <div className="text-right hidden sm:block">
                  <span className="text-xs font-extrabold text-gov-navy block">
                    {user.family_id ? `Family ID: ${user.family_id}` : user.login_id}
                  </span>
                  <span className={`text-[10px] uppercase font-extrabold px-2 py-0.5 rounded border ${
                    isOfficer
                      ? 'bg-amber-100 text-amber-900 border-amber-300'
                      : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                  }`}>
                    {isOfficer ? user.role : `Household Active Member`}
                  </span>
                </div>

                <button
                  onClick={() => { logout(); navigate('/login'); }}
                  className="p-2 rounded-lg bg-slate-100 hover:bg-red-50 text-slate-700 hover:text-red-700 border border-slate-200 transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 ml-2">
                <Link
                  to="/register"
                  className={getNavLinkClass('/register')}
                >
                  <span>Register Household</span>
                </Link>

                <Link
                  to="/login"
                  className={getNavLinkClass('/login')}
                >
                  <LogIn className={`w-4 h-4 ${isActive('/login') ? 'text-saffron' : 'text-slate-500'}`} />
                  <span>Portal Sign In</span>
                </Link>
              </div>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
};
