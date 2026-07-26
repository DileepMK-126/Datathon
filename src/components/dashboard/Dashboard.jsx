import React from 'react';
import { Activity, Crosshair, Network, ShieldCheck, Clock3, ArrowRight, Sparkles, FileText } from 'lucide-react';
import HotspotMap from '../analytics/HotspotMap';
import RiskGauge from '../analytics/RiskGauge';
import TrendChart from '../analytics/TrendChart';
import AlertsPanel from '../analytics/AlertsPanel';
import IntelligencePanel from '../analytics/IntelligencePanel';
import TimelinePanel from '../analytics/TimelinePanel';
import CaseSimilarityPanel from '../cases/CaseSimilarityPanel';
import ExplainabilityPanel from '../intelligence/ExplainabilityPanel';
import RecommendationPanel from '../recommendations/RecommendationPanel';

export default function Dashboard({
  metrics,
  apiError,
  liveData,
  liveZones,
  activeZone,
  setActiveZone,
  scaleText,
  riskLabel,
  recommendationData,
  period,
  setPeriod,
  trendData,
  defaultTrend,
  displayAlerts,
  openAlert,
  setIsAlertsOpen,
  setNetworkOpen,
  intelligenceData,
  intelligenceLoading,
  timelineData,
  timelineLoading,
  activeCaseId,
  caseProfile,
  userRole,
  openCaseProfile
}) {
  return (
    <>
      <section className="page-head">
        <div>
          <div className="eyebrow"><Sparkles size={14}/> LIVE INTELLIGENCE</div>
          <h1>City crime intelligence</h1>
          <p>Understand emerging patterns, connected cases, and where to focus next.</p>
        </div>
        <div className="head-actions">
          <div className="live-indicator">
            <i></i> {apiError ? 'Using demo fallback' : liveData ? 'API analytics live' : 'Loading analytics'}
          </div>
          <button className="export-button">
            <FileText size={17}/> Briefing report
          </button>
        </div>
      </section>

      <section className="metric-row" aria-label="City summary">
        <article className="metric-card">
          <div className="metric-top">
            <span>Active incidents</span>
            <span className="metric-icon orange"><Activity size={18}/></span>
          </div>
          <div className="metric-value">{metrics?.active_incidents ?? 247}</div>
          <div className="metric-detail negative">
            <ArrowRight size={14}/> {metrics?.incident_change_percent ?? 12.6}% <span>vs. last period</span>
          </div>
        </article>
        
        <article className="metric-card">
          <div className="metric-top">
            <span>Emerging hotspots</span>
            <span className="metric-icon red"><Crosshair size={18}/></span>
          </div>
          <div className="metric-value">{metrics?.emerging_hotspots ?? 4}</div>
          <div className="metric-detail neutral">
            <span className="new-pill">LIVE</span><span>require review</span>
          </div>
        </article>
        
        <article className="metric-card">
          <div className="metric-top">
            <span>Linked case clusters</span>
            <span className="metric-icon violet"><Network size={18}/></span>
          </div>
          <div className="metric-value">{metrics?.linked_case_clusters ?? 18}</div>
          <div className="metric-detail positive">
            <ArrowRight size={14}/> live <span>entity matches</span>
          </div>
        </article>
        
        <article className="metric-card">
          <div className="metric-top">
            <span>High-risk zones</span>
            <span className="metric-icon blue"><ShieldCheck size={18}/></span>
          </div>
          <div className="metric-value">{metrics?.high_risk_zones ?? 2}</div>
          <div className="metric-detail neutral">
            <Clock3 size={14}/><span>Model refreshed on load</span>
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <div className="intel-full-width">
          <IntelligencePanel data={intelligenceData} loading={intelligenceLoading} />
        </div>
        <div className="intel-full-width">
          <TimelinePanel data={timelineData} loading={timelineLoading} />
        </div>
        <div className="intel-full-width">
          <ExplainabilityPanel zoneId={activeZone.id} userRole={userRole} />
        </div>
        <div className="intel-full-width">
          <CaseSimilarityPanel 
            caseId={activeCaseId}
            currentCaseDetails={caseProfile || { case: { id: activeCaseId } }}
            userRole={userRole}
            onOpenCaseProfile={openCaseProfile}
          />
        </div>
        <div className="intel-full-width">
          <RecommendationPanel zoneId={activeZone.id} userRole={userRole} />
        </div>

        <HotspotMap 
          liveZones={liveZones}
          activeZone={activeZone}
          setActiveZone={setActiveZone}
          scaleText={scaleText}
          metrics={metrics}
          liveData={liveData}
          onViewIntelligence={() => {
            const firstAlert = displayAlerts.find(alert => (alert.zone_id ?? alert.zone) === activeZone.id) ?? displayAlerts[0];
            openAlert(firstAlert);
          }}
        />

        <RiskGauge 
          activeZone={activeZone}
          riskLabel={riskLabel}
          recommendationData={recommendationData}
        />

        <TrendChart 
          period={period}
          setPeriod={setPeriod}
          trendData={trendData}
          defaultTrend={defaultTrend}
        />

        <AlertsPanel 
          displayAlerts={displayAlerts}
          onViewAllAlerts={() => setIsAlertsOpen(true)}
          onOpenAlert={openAlert}
        />
      </section>
    </>
  );
}
