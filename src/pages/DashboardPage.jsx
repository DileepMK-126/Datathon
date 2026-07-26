import React, { useState } from 'react';
import Sidebar from '../components/dashboard/Sidebar';
import Header from '../components/dashboard/Header';
import Dashboard from '../components/dashboard/Dashboard';
import AlertModal from '../components/modals/AlertModal';
import NetworkModal from '../components/modals/NetworkModal';
import ProfileModal from '../components/modals/ProfileModal';
import MorningBrief from '../components/intelligence/MorningBrief';

import DemoOverlay from '../components/demo/DemoOverlay';
import CommandPalette from '../components/dashboard/CommandPalette';
import ToastContainer from '../components/dashboard/ToastContainer';
import { useEffect } from 'react';

export default function DashboardPage({ dashboardProps }) {
  const [showBrief, setShowBrief] = useState(true);
  const [demoActive, setDemoActive] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [toasts, setToasts] = useState([]);

  const addToast = (type, title, desc) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, type, title, desc }]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Listen for Ctrl+K command palette trigger
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setPaletteOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const {
    activeZone,
    setActiveZone,
    period,
    setPeriod,
    isAlertsOpen,
    setIsAlertsOpen,
    networkOpen,
    setNetworkOpen,
    liveData,
    trendData,
    recommendationData,
    caseProfile,
    profileOpen,
    setProfileOpen,
    apiError,
    liveZones,
    displayAlerts,
    metrics,
    activeAlert,
    riskLabel,
    scaleText,
    networkLayout,
    openAlert,
    openCaseProfile,
    logoutUser,
    defaultTrend,
    intelligenceData,
    intelligenceLoading,
    timelineData,
    timelineLoading,
    activeCaseId,
    auth,
  } = dashboardProps;

  const handleCommandPaletteAction = (actionId) => {
    switch (actionId) {
      case 'start-walkthrough':
        setDemoActive(true);
        addToast('success', 'Presentation Mode Enabled', 'Walkthrough scenarios loaded successfully.');
        break;
      case 'clear-cache':
        addToast('warning', 'Memory Cache Cleared', 'All prediction buffers and similarity indexes cleared.');
        break;
      case 'inspect-sector-7':
        const zone7 = liveZones?.find(z => z.id === 'sector-7') || { id: 'sector-7', name: 'Sector 7' };
        setActiveZone(zone7);
        addToast('info', 'Focused Sector 7', 'Dashboard cards redirected to Sector 7 datasets.');
        break;
      case 'inspect-old-town':
        const zoneOld = liveZones?.find(z => z.id === 'old-town') || { id: 'old-town', name: 'Old Town' };
        setActiveZone(zoneOld);
        addToast('info', 'Focused Old Town', 'Dashboard cards redirected to Old Town datasets.');
        break;
      default:
        break;
    }
  };

  if (showBrief) {
    return (
      <div className="app-shell">
        <Sidebar 
          onNetworkClick={() => setNetworkOpen(true)} 
          onLogout={logoutUser}
          onDemoClick={() => setDemoActive(true)}
        />
        
        <main className="main-content">
          <Header onAlertsClick={() => setIsAlertsOpen(true)} />
          <MorningBrief 
            userRole={auth.user?.role}
            onEnterDashboard={() => setShowBrief(false)}
          />
          <footer>
            Sentinel is a decision-support prototype. Data shown is synthetic and open-data derived; all operational action requires human review.
          </footer>
        </main>
        
        {demoActive && (
          <DemoOverlay 
            onExitDemo={() => setDemoActive(false)}
            userRole={auth.user?.role}
          />
        )}
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar 
        onNetworkClick={() => setNetworkOpen(true)} 
        onLogout={logoutUser}
        onDemoClick={() => setDemoActive(true)}
      />
      
      <main className="main-content">
        <Header onAlertsClick={() => setIsAlertsOpen(true)} />
        
        <Dashboard 
          metrics={metrics}
          apiError={apiError}
          liveData={liveData}
          liveZones={liveZones}
          activeZone={activeZone}
          setActiveZone={setActiveZone}
          scaleText={scaleText}
          riskLabel={riskLabel}
          recommendationData={recommendationData}
          period={period}
          setPeriod={setPeriod}
          trendData={trendData}
          defaultTrend={defaultTrend}
          displayAlerts={displayAlerts}
          openAlert={openAlert}
          setIsAlertsOpen={setIsAlertsOpen}
          setNetworkOpen={setNetworkOpen}
          intelligenceData={intelligenceData}
          intelligenceLoading={intelligenceLoading}
          timelineData={timelineData}
          timelineLoading={timelineLoading}
          activeCaseId={activeCaseId}
          caseProfile={caseProfile}
          userRole={auth.user?.role}
          openCaseProfile={openCaseProfile}
        />
        
        <footer>
          Sentinel is a decision-support prototype. Data shown is synthetic and open-data derived; all operational action requires human review.
        </footer>
      </main>

      <AlertModal 
        isOpen={isAlertsOpen} 
        onClose={() => setIsAlertsOpen(false)} 
        activeAlert={activeAlert} 
        onOpenNetwork={() => {
          setIsAlertsOpen(false);
          setNetworkOpen(true);
        }}
      />

      <NetworkModal 
        isOpen={networkOpen} 
        onClose={() => setNetworkOpen(false)} 
        liveData={liveData}
        networkLayout={networkLayout}
        onReviewUnifiedCase={openCaseProfile}
        userRole={auth.user?.role}
      />

      <ProfileModal 
        isOpen={profileOpen} 
        onClose={() => setProfileOpen(false)} 
        caseProfile={caseProfile}
      />

      {demoActive && (
        <DemoOverlay 
          onExitDemo={() => setDemoActive(false)}
          userRole={auth.user?.role}
        />
      )}

      <CommandPalette 
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onActionTrigger={handleCommandPaletteAction}
      />

      <ToastContainer 
        toasts={toasts}
        onCloseToast={removeToast}
      />
    </div>
  );
}
