import React from 'react';
import { Navigate } from 'react-router-dom';

export const OfficerLoginPage: React.FC = () => {
  return <Navigate to="/login?role=officer" replace />;
};
