import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { TopGovHeader } from './components/TopGovHeader';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { ProtectedRoute } from './components/ProtectedRoute';
import { CitizenHome } from './pages/CitizenHome';
import { OfficerHome } from './pages/OfficerHome';
import { LoginPage } from './pages/LoginPage';
import { OfficerLoginPage } from './pages/OfficerLoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { FamilyProfilePage } from './pages/FamilyProfilePage';
import { AllSchemesPage } from './pages/AllSchemesPage';
import { AnalyticsDashboardPage } from './pages/AnalyticsDashboardPage';

import { AIChatbotWidget } from './components/AIChatbotWidget';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans">
            <TopGovHeader />
            <Navbar />
            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<CitizenHome />} />
                <Route path="/schemes" element={<AllSchemesPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/my-family" element={<FamilyProfilePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/officer-login" element={<OfficerLoginPage />} />
                <Route
                  path="/officer"
                  element={
                    <ProtectedRoute allowedRoles={['STATE_ADMIN', 'OFFICER', 'DISTRICT_OFFICER', 'FIELD_OFFICER', 'ADMIN']}>
                      <OfficerHome />
                    </ProtectedRoute>
                  }
                />
                <Route path="/analytics" element={<AnalyticsDashboardPage />} />
              </Routes>
            </main>
            <AIChatbotWidget />
            <Footer />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
