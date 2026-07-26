import React, { useState, useEffect } from 'react';
import { SlidersHorizontal, FileJson, Printer, ShieldAlert } from 'lucide-react';
import Card from '../common/Card';
import Loader from '../common/Loader';
import RecommendationCard from './RecommendationCard';

export default function RecommendationPanel({ zoneId, userRole }) {
  const [recommendationsData, setRecommendationsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filter States
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `/api/recommendations/${zoneId}`;
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error('Failed to load patrol recommendations.');
      }
      const data = await res.json();
      setRecommendationsData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (zoneId) {
      fetchRecommendations();
    }
  }, [zoneId]);

  const handleExportJson = () => {
    if (!recommendationsData) return;
    const blob = new Blob([JSON.stringify(recommendationsData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `patrol-recommendations-${zoneId}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    alert("Patrol Briefing Report prepared. Press Ctrl+P/Cmd+P to print report.");
    window.print();
  };

  // Client-side filtering
  const filteredRecs = recommendationsData?.recommendations.filter(rec => {
    const matchesPriority = priorityFilter ? rec.priority.toLowerCase() === priorityFilter.toLowerCase() : true;
    const matchesCategory = categoryFilter ? rec.category.toLowerCase().includes(categoryFilter.toLowerCase()) : true;
    return matchesPriority && matchesCategory;
  }) ?? [];

  return (
    <Card 
      title={`Evidence-Based Patrol Recommendations — ${recommendationsData?.zone_name ?? 'Loading'}`}
      kicker="DECISION SUPPORT DISPATCH"
      kickerTone="red"
      className="patrol-recommendations-card"
    >
      <div className="recommendations-header-actions mb-3">
        {/* Filters */}
        <div className="recs-filters-bar">
          <SlidersHorizontal size={14} className="text-muted" />
          <div className="select-wrapper">
            <select value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)}>
              <option value="">All Priorities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          <div className="select-wrapper">
            <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
              <option value="">All Categories</option>
              <option value="patrol">Patrol Increase</option>
              <option value="cctv">CCTV/Surveillance</option>
              <option value="investigation">Investigation Reviews</option>
            </select>
          </div>
        </div>

        {/* Exports */}
        <div className="recs-exports-bar">
          <button className="btn btn-secondary btn-sm" onClick={handleExportJson} title="Export JSON Report">
            <FileJson size={13} />
            <span>Export JSON</span>
          </button>
          <button className="btn btn-primary btn-sm" onClick={handlePrint} title="Print Briefing Report">
            <Printer size={13} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {loading && <Loader message="Compiling tactical dispatch alternatives..." />}
      {error && <div className="error-panel">{error}</div>}

      {!loading && !error && recommendationsData && (
        <>
          <div className="human-verification-alert mb-3">
            <ShieldAlert size={14} className="text-orange" />
            <span>
              <strong>Operational Disclaimer:</strong> Sentinel recommendations are strictly decision-support advisories. Physical dispatch requires independent review and confirmation.
            </span>
          </div>

          {filteredRecs.length === 0 ? (
            <div className="empty-state-panel text-center py-4">
              <p className="text-muted italic">No recommendations match the selected filters.</p>
            </div>
          ) : (
            <div className="recommendations-cards-grid">
              {filteredRecs.map(rec => (
                <RecommendationCard 
                  key={rec.id}
                  rec={rec}
                  userRole={userRole}
                />
              ))}
            </div>
          )}
        </>
      )}
    </Card>
  );
}
