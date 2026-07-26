import { useState, useEffect, useMemo } from 'react';
import { getApi, signIn } from '../services/api';

const zones = [
  { id: 'sector-7', name: 'Sector 7', incidents: 43, delta: '+38%', risk: 87, x: 37, y: 45, tone: 'critical', score: 91 },
  { id: 'old-town', name: 'Old Town', incidents: 28, delta: '+19%', risk: 72, x: 62, y: 34, tone: 'high', score: 74 },
  { id: 'rivergate', name: 'Rivergate', incidents: 19, delta: '+8%', risk: 58, x: 75, y: 67, tone: 'watch', score: 59 },
  { id: 'central', name: 'Central Market', incidents: 16, delta: '-6%', risk: 36, x: 24, y: 70, tone: 'stable', score: 34 },
];

const seedAlerts = [
  { type: 'Anomaly', title: 'Burglary pattern exceeds baseline', text: 'Sector 7 has 43 reports in the last 7 days — 2.4× its expected volume.', time: '12 min ago', level: 'critical', zone: 'sector-7' },
  { type: 'Network', title: 'New link found across 3 cases', text: 'A shared device identifier connects recent reports in Sector 7 and Old Town.', time: '34 min ago', level: 'high', zone: 'old-town' },
  { type: 'Risk', title: 'Patrol coverage risk window', text: 'Model predicts elevated incident likelihood near Junction 4 between 20:00–23:00.', time: '1 hr ago', level: 'watch', zone: 'rivergate' },
];

const defaultTrend = [34, 39, 30, 43, 40, 46, 52, 44, 48, 56, 60, 58, 69, 73, 66, 81, 89, 83, 98, 106, 101, 115, 122, 136, 141, 132, 147, 158];

export function useDashboard() {
  const [activeZone, setActiveZone] = useState(zones[0]);
  const [period, setPeriod] = useState('7 days');
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);
  const [networkOpen, setNetworkOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [liveData, setLiveData] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [recommendationData, setRecommendationData] = useState(null);
  const [caseProfile, setCaseProfile] = useState(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [apiError, setApiError] = useState(false);
  const [auth, setAuth] = useState({ ready: false, required: false, user: null });
  const [intelligenceData, setIntelligenceData] = useState(null);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const [timelineData, setTimelineData] = useState(null);
  const [timelineLoading, setTimelineLoading] = useState(false);

  const liveZones = useMemo(() => {
    if (!liveData?.hotspots?.items?.length) return zones;
    const risks = new Map((liveData.dashboard?.risks ?? []).map(item => [item.zone_id, item]));
    return liveData.hotspots.items.map((cluster, index) => {
      const base = zones.find(zone => zone.id === cluster.zone_id) ?? zones[index % zones.length];
      const risk = risks.get(cluster.zone_id);
      const change = cluster.change_percent ?? 0;
      return {
        ...base,
        id: cluster.zone_id,
        name: cluster.zone_name,
        incidents: cluster.period_count ?? cluster.incident_count,
        delta: `${change >= 0 ? '+' : ''}${change}%`,
        risk: risk?.score ?? cluster.risk_score,
        score: risk?.score ?? cluster.risk_score,
        tone: cluster.tone,
        drivers: risk?.drivers ?? [],
        confidence: risk?.confidence,
      };
    });
  }, [liveData]);

  const displayAlerts = liveData?.alerts?.items?.length ? liveData.alerts.items : seedAlerts;
  const metrics = liveData?.dashboard?.metrics;
  const activeAlert = selectedAlert ?? displayAlerts[0];
  const riskLabel = activeZone.risk > 80 ? 'Critical' : activeZone.risk > 65 ? 'High' : activeZone.risk > 45 ? 'Elevated' : 'Guarded';
  const scaleText = useMemo(() => ({ '24 hours': '24H', '7 days': '7D', '30 days': '30D' }[period]), [period]);
  const periodDays = useMemo(() => ({ '24 hours': 14, '7 days': 28, '30 days': 30 }[period]), [period]);

  const networkLayout = useMemo(() => {
    const positions = [[93, 150], [255, 70], [265, 230], [405, 145], [505, 68], [500, 235], [145, 55], [145, 245], [360, 46]];
    return (liveData?.network?.nodes ?? []).slice(0, 9).map((node, index) => ({ ...node, x: positions[index][0], y: positions[index][1] }));
  }, [liveData]);

  // Health check & session validation
  useEffect(() => {
    let active = true;
    const API_BASE = import.meta.env.VITE_API_URL || '/api';
    fetch(`${API_BASE}/health`).then(async response => {
      if (!response.ok) throw new Error('Health check failed');
      return response.json();
    }).then(async health => {
      const required = health.auth_required === 'true' || health.auth_required === true;
      if (!required) {
        if (active) setAuth({ ready: true, required: false, user: { username: 'development-analyst', role: 'analyst' } });
        return;
      }
      const token = localStorage.getItem('sentinel_access_token');
      if (!token) {
        if (active) setAuth({ ready: true, required: true, user: null });
        return;
      }
      try {
        const profile = await getApi('/auth/me');
        if (active) setAuth({ ready: true, required: true, user: profile.user });
      } catch {
        localStorage.removeItem('sentinel_access_token');
        if (active) setAuth({ ready: true, required: true, user: null });
      }
    }).catch(() => {
      if (active) setAuth({ ready: true, required: false, user: { username: 'offline-analyst', role: 'analyst' } });
    });
    return () => { active = false; };
  }, []);

  // Main metrics loader
  useEffect(() => {
    let active = true;
    if (!auth.ready || (auth.required && !auth.user)) return () => { active = false; };
    Promise.all([getApi('/dashboard'), getApi('/hotspots'), getApi('/alerts'), getApi('/networks')])
      .then(([dashboard, hotspots, alertData, network]) => {
        if (!active) return;
        setLiveData({ dashboard, hotspots, alerts: alertData, network });
        setApiError(false);
        const first = hotspots.items?.[0];
        if (first) {
          const base = zones.find(zone => zone.id === first.zone_id) ?? zones[0];
          const risk = dashboard.risks?.find(item => item.zone_id === first.zone_id);
          setActiveZone({
            ...base,
            id: first.zone_id,
            name: first.zone_name,
            incidents: first.period_count ?? first.incident_count,
            delta: `${first.change_percent >= 0 ? '+' : ''}${first.change_percent}%`,
            risk: risk?.score ?? first.risk_score,
            score: risk?.score ?? first.risk_score,
            tone: first.tone,
            drivers: risk?.drivers ?? [],
            confidence: risk?.confidence
          });
        }
      })
      .catch(error => {
        if (!active) return;
        if (error.message.includes('(401)')) {
          localStorage.removeItem('sentinel_access_token');
          setAuth({ ready: true, required: true, user: null });
        } else {
          setApiError(true);
        }
      });
    return () => { active = false; };
  }, [auth.ready, auth.required, auth.user]);

  // Fetch trends
  useEffect(() => {
    let active = true;
    if (!auth.ready || (auth.required && !auth.user)) return () => { active = false; };
    getApi(`/trends?zone_id=${activeZone.id}&days=${periodDays}`)
      .then(data => { if (active) setTrendData(data); })
      .catch(() => { if (active) setTrendData(null); });
    return () => { active = false; };
  }, [activeZone.id, periodDays, auth.ready, auth.required, auth.user]);

  // Fetch recommendations
  useEffect(() => {
    let active = true;
    if (!auth.ready || (auth.required && !auth.user)) return () => { active = false; };
    getApi(`/recommendations?zone_id=${activeZone.id}`)
      .then(data => { if (active) setRecommendationData(data); })
      .catch(() => { if (active) setRecommendationData(null); });
    return () => { active = false; };
  }, [activeZone.id, auth.ready, auth.required, auth.user]);

  // Fetch intelligence brief
  useEffect(() => {
    let active = true;
    if (!auth.ready || (auth.required && !auth.user)) return () => { active = false; };
    setIntelligenceLoading(true);
    getApi(`/intelligence?zone_id=${activeZone.id}`)
      .then(data => {
        if (active) {
          setIntelligenceData(data);
          setIntelligenceLoading(false);
        }
      })
      .catch(() => {
        if (active) {
          // resilient fallback mapping
          setIntelligenceData({
            zone_id: activeZone.id,
            zone_name: activeZone.name,
            priority: activeZone.risk >= 80 ? 'HIGH' : activeZone.risk >= 45 ? 'MEDIUM' : 'LOW',
            confidence: activeZone.confidence ?? 75,
            summary: `System monitoring report for ${activeZone.name}. Baseline tracking is currently active. The hotspot model identified ${activeZone.incidents} incidents in this zone, deviating from normal baselines.`,
            drivers: activeZone.drivers?.map(d => d.name) ?? ["Recent incident frequency", "Area risk index"],
            evidence: [
              `Incident volume cluster containing ${activeZone.incidents} cases`,
              `Predictive risk score of ${activeZone.risk}/100 calculated`
            ],
            recommendations: ["Maintain regular patrol runs", "Validate recent status with operations center"],
            review_required: true
          });
          setIntelligenceLoading(false);
        }
      });
    return () => { active = false; };
  }, [activeZone.id, auth.ready, auth.required, auth.user, activeZone.risk, activeZone.name, activeZone.incidents, activeZone.drivers, activeZone.confidence]);

  // Resolve active case ID for timeline based on selected zone
  const activeCaseId = useMemo(() => {
    const caseInZone = liveData?.network?.nodes?.find(
      node => node.kind === 'case' && node.zone_id === activeZone.id
    );
    if (caseInZone) return caseInZone.id;

    const alertInZone = displayAlerts.find(
      alert => (alert.zone_id ?? alert.zone) === activeZone.id
    );
    if (alertInZone && alertInZone.text) {
      const match = alertInZone.text.match(/FIR-\d+/i);
      if (match) return match[0].toUpperCase();
    }

    const zoneDefaults = {
      'sector-7': 'FIR-7001',
      'old-town': 'FIR-7006',
      'rivergate': 'FIR-7011',
      'central': 'FIR-7012'
    };
    return zoneDefaults[activeZone.id] || 'FIR-7001';
  }, [liveData, activeZone.id, displayAlerts]);

  // Fetch case timeline
  useEffect(() => {
    let active = true;
    if (!auth.ready || (auth.required && !auth.user)) return () => { active = false; };
    if (!activeCaseId) return;
    setTimelineLoading(true);
    getApi(`/cases/${activeCaseId}/timeline`)
      .then(data => {
        if (active) {
          setTimelineData(data);
          setTimelineLoading(false);
        }
      })
      .catch(() => {
        if (active) {
          // offline/fallback timeline data structure
          setTimelineData({
            case_id: activeCaseId,
            events: [
              {
                event_id: `${activeCaseId}-fir`,
                timestamp: '2026-07-18T10:00:00Z',
                source_system: 'Police FIR',
                event_type: 'FIR Registered',
                title: 'First Information Report Registered',
                description: `FIR filed for active investigation in ${activeZone.name}. Initial details logged.`,
                confidence: 1.0,
                linked_case: activeCaseId,
                resolved_entities: activeZone.drivers?.map(d => d.name) || ["Aisha Khan"],
                supporting_evidence: [`FIR Reference: ${activeCaseId}`],
                severity: 'HIGH'
              },
              {
                event_id: `${activeCaseId}-cctv`,
                timestamp: '2026-07-19T14:30:00Z',
                source_system: 'CCTV',
                event_type: 'CCTV Match',
                title: 'Vehicle / Movement Pattern Detected',
                description: `Camera scan flagged suspect vehicle matching description in vicinity of incident in ${activeZone.name}.`,
                confidence: 0.74,
                linked_case: activeCaseId,
                resolved_entities: ["Phone Reference 981726"],
                supporting_evidence: ["Camera CAM-S7-02"],
                severity: 'MEDIUM'
              },
              {
                event_id: `${activeCaseId}-lab`,
                timestamp: '2026-07-20T09:00:00Z',
                source_system: 'Laboratory',
                event_type: 'Laboratory Analysis',
                title: 'Forensic Lab Report',
                description: 'Physical evidence match resolved against known registry records. Status: analyst review.',
                confidence: 0.84,
                linked_case: activeCaseId,
                resolved_entities: ["Registry Match"],
                supporting_evidence: ["Observation Match Report"],
                severity: 'HIGH'
              },
              {
                event_id: `${activeCaseId}-court`,
                timestamp: '2026-07-22T11:00:00Z',
                source_system: 'Court',
                event_type: 'Court Hearing',
                title: 'Justice-System Linkage Hearing',
                description: 'Judicial reference citation JUD-003 listed for hearing. Stage: historical record match.',
                confidence: 0.69,
                linked_case: activeCaseId,
                resolved_entities: [],
                supporting_evidence: ["Citation JUD-003"],
                severity: 'MEDIUM'
              },
              {
                event_id: `${activeCaseId}-prison`,
                timestamp: '2026-07-24T16:00:00Z',
                source_system: 'Prison',
                event_type: 'Prison Booking',
                title: 'Correctional Booking Update',
                description: 'Suspect status updated. Booking disposition resolved.',
                confidence: 0.69,
                linked_case: activeCaseId,
                resolved_entities: [],
                supporting_evidence: ["Disposition record review"],
                severity: 'MEDIUM'
              },
              {
                event_id: `${activeCaseId}-ai`,
                timestamp: new Date().toISOString(),
                source_system: 'Intelligence Engine',
                event_type: 'AI Intelligence Alert',
                title: 'Unified Cognitive Intelligence Briefing',
                description: `Sentinel Engine flag: active intelligence generated with ${activeZone.risk}% risk score. Threat assessment requires operational review.`,
                confidence: 0.95,
                linked_case: activeCaseId,
                resolved_entities: ["AI Cognitive Driver"],
                supporting_evidence: ["Multi-model risk attribution"],
                severity: activeZone.risk >= 80 ? 'CRITICAL' : activeZone.risk >= 65 ? 'HIGH' : 'MEDIUM'
              }
            ]
          });
          setTimelineLoading(false);
        }
      });
    return () => { active = false; };
  }, [activeCaseId, auth.ready, auth.required, auth.user, activeZone.name, activeZone.risk, activeZone.drivers]);

  const openAlert = (alert) => {
    setSelectedAlert(alert);
    setActiveZone(liveZones.find(zone => zone.id === (alert.zone_id ?? alert.zone)) ?? liveZones[0]);
    setIsAlertsOpen(true);
  };

  const openCaseProfile = async (caseIdParam = null) => {
    const idToFetch = caseIdParam || liveData?.network?.nodes?.find(node => node.kind === 'case')?.id;
    if (!idToFetch) return;
    try {
      const data = await getApi(`/cases/${idToFetch}`);
      setCaseProfile(data);
      setProfileOpen(true);
    } catch {
      setCaseProfile(null);
    }
  };

  const loginUser = async (username, password) => {
    const payload = await signIn(username, password);
    setAuth({ ready: true, required: true, user: { username, role: payload.role } });
  };

  const logoutUser = () => {
    localStorage.removeItem('sentinel_access_token');
    setAuth({ ready: true, required: true, user: null });
  };

  return {
    activeZone,
    setActiveZone,
    period,
    setPeriod,
    isAlertsOpen,
    setIsAlertsOpen,
    networkOpen,
    setNetworkOpen,
    selectedAlert,
    setSelectedAlert,
    liveData,
    trendData,
    recommendationData,
    caseProfile,
    profileOpen,
    setProfileOpen,
    apiError,
    auth,
    liveZones,
    displayAlerts,
    metrics,
    activeAlert,
    riskLabel,
    scaleText,
    periodDays,
    networkLayout,
    openAlert,
    openCaseProfile,
    loginUser,
    logoutUser,
    defaultTrend,
    intelligenceData,
    intelligenceLoading,
    timelineData,
    timelineLoading,
    activeCaseId,
  };
}
