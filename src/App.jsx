import React from 'react';
import { useDashboard } from './hooks/useDashboard';
import Loader from './components/common/Loader';
import LoginScreen from './components/LoginScreen';
import DashboardPage from './pages/DashboardPage';
import './styles.css';

export default function App() {
  const dashboardProps = useDashboard();
  const { auth, loginUser } = dashboardProps;

  if (!auth.ready) {
    return <Loader message="Validating secure session…" />;
  }

  if (auth.required && !auth.user) {
    return <LoginScreen onLogin={loginUser} />;
  }

  return <DashboardPage dashboardProps={dashboardProps} />;
}
