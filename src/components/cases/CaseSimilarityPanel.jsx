import React, { useState, useEffect } from 'react';
import { Sparkles, SlidersHorizontal, GitCompare, X, Check, ShieldAlert } from 'lucide-react';
import Card from '../common/Card';
import Loader from '../common/Loader';
import CaseSimilarityCard from './CaseSimilarityCard';
import { getApi } from '../../services/api';

export default function CaseSimilarityPanel({ 
  caseId,
  currentCaseDetails,
  userRole,
  onOpenCaseProfile
}) {
  const [similarityData, setSimilarityData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Filter settings
  const [threshold, setThreshold] = useState(75);
  const [limit, setLimit] = useState(5);
  const [category, setCategory] = useState('');
  const [district, setDistrict] = useState('');
  const [sort, setSort] = useState('score');
  
  // Side-by-side comparison modal state
  const [compareMatch, setCompareMatch] = useState(null);

  const fetchSimilarCases = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `/cases/${caseId}/similar?limit=${limit}&threshold=${threshold}&sort=${sort}`;
      if (category) url += `&category=${encodeURIComponent(category)}`;
      if (district) url += `&district=${encodeURIComponent(district)}`;
      
      const data = await getApi(url);
      setSimilarityData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) {
      fetchSimilarCases();
    }
  }, [caseId, threshold, limit, category, district, sort]);

  const handleCompare = (match) => {
    if (userRole === 'analyst') {
      alert('Supervisor or Administrator credentials are required to access the case comparison system.');
      return;
    }
    setCompareMatch(match);
  };

  const highlightMatch = (val1, val2) => {
    if (!val1 || !val2) return '';
    const clean1 = String(val1).toLowerCase().trim();
    const clean2 = String(val2).toLowerCase().trim();
    return clean1 === clean2 ? 'attribute-match-highlight' : '';
  };

  return (
    <div className="case-similarity-section">
      <Card
        title="Similar historical investigations"
        kicker="CASE INTELLIGENCE SEARCH"
        kickerTone="red"
        className="similarity-panel-card"
      >
        {/* Filters bar */}
        <div className="similarity-filters-bar">
          <div className="filter-group">
            <SlidersHorizontal size={14} className="filter-icon" />
            <span>Filters:</span>
          </div>
          
          <div className="filter-controls">
            <div className="select-wrapper">
              <select value={category} onChange={e => setCategory(e.target.value)}>
                <option value="">All Crime Types</option>
                <option value="Burglary">Burglary</option>
                <option value="Theft">Theft</option>
                <option value="Vehicle theft">Vehicle theft</option>
                <option value="Fraud">Fraud</option>
                <option value="Assault">Assault</option>
              </select>
            </div>

            <div className="select-wrapper">
              <select value={district} onChange={e => setDistrict(e.target.value)}>
                <option value="">All Zones</option>
                <option value="sector-7">Sector 7</option>
                <option value="old-town">Old Town</option>
                <option value="rivergate">Rivergate</option>
                <option value="central">Central Market</option>
              </select>
            </div>

            <div className="range-wrapper">
              <label>Min Similarity: {threshold}%</label>
              <input 
                type="range" 
                min="50" 
                max="90" 
                step="5" 
                value={threshold} 
                onChange={e => setThreshold(Number(e.target.value))} 
              />
            </div>
          </div>
        </div>

        {/* Content list */}
        {loading && <Loader message="Scoring historical investigations..." />}
        {error && <div className="error-panel">{error}</div>}
        
        {!loading && !error && similarityData && (
          <>
            {similarityData.matches.length === 0 ? (
              <div className="empty-state-panel">
                <Sparkles size={24} />
                <p>No historical cases found matching the current criteria above the {threshold}% threshold.</p>
              </div>
            ) : (
              <div className="similarity-grid">
                {similarityData.matches.map(match => (
                  <CaseSimilarityCard 
                    key={match.case_id}
                    match={match}
                    onCompare={handleCompare}
                    onOpenCase={onOpenCaseProfile}
                    userRole={userRole}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </Card>

      {/* Side-by-Side Comparison Modal */}
      {compareMatch && (
        <div className="modal-overlay" onClick={() => setCompareMatch(null)}>
          <div className="compare-modal glass-panel slide-up" onClick={e => e.stopPropagation()}>
            <div className="compare-modal-header">
              <div className="compare-title-row">
                <GitCompare size={20} className="header-icon" />
                <h3>Side-by-Side Case Comparison</h3>
              </div>
              <button className="close-btn-round" onClick={() => setCompareMatch(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="compare-modal-body">
              <div className="compare-columns-grid">
                
                {/* Column 1: Attribute Names */}
                <div className="compare-attributes-column">
                  <div className="compare-cell cell-header">Attributes</div>
                  <div className="compare-cell">Case ID</div>
                  <div className="compare-cell">Crime Type</div>
                  <div className="compare-cell">Incident Date & Time</div>
                  <div className="compare-cell">Zone/District</div>
                  <div className="compare-cell">Police Station</div>
                  <div className="compare-cell">Vehicles</div>
                  <div className="compare-cell">Phones</div>
                  <div className="compare-cell">Persons</div>
                  <div className="compare-cell">Risk Window / Category</div>
                </div>

                {/* Column 2: Current Case */}
                <div className="compare-case-column focal-case">
                  <div className="compare-cell cell-header">Current Case</div>
                  <div className="compare-cell highlight-cell">{currentCaseDetails.case?.id || caseId}</div>
                  <div className={`compare-cell ${highlightMatch(currentCaseDetails.case?.crime_type, compareMatch.crime_type)}`}>
                    {currentCaseDetails.case?.crime_type}
                  </div>
                  <div className="compare-cell">{currentCaseDetails.case?.opened_at}</div>
                  <div className={`compare-cell ${highlightMatch(currentCaseDetails.case?.zone_id, compareMatch.details.zone_id)}`}>
                    {currentCaseDetails.case?.zone_name || currentCaseDetails.case?.zone_id}
                  </div>
                  <div className="compare-cell">
                    {currentCaseDetails.case?.zone_name ? `${currentCaseDetails.case.zone_name} Station` : ''}
                  </div>
                  <div className="compare-cell">
                    {currentCaseDetails.entities?.filter(e => e.type === 'vehicle').map(e => e.label).join(', ') || 'None'}
                  </div>
                  <div className="compare-cell">
                    {currentCaseDetails.entities?.filter(e => e.type === 'phone').map(e => e.label).join(', ') || 'None'}
                  </div>
                  <div className="compare-cell">
                    {currentCaseDetails.entities?.filter(e => e.type === 'person').map(e => e.label).join(', ') || 'None'}
                  </div>
                  <div className="compare-cell">
                    {currentCaseDetails.case?.status}
                  </div>
                </div>

                {/* Column 3: Historical Case */}
                <div className="compare-case-column matched-case">
                  <div className="compare-cell cell-header">Matched Case (Similarity: {compareMatch.similarity_score}%)</div>
                  <div className="compare-cell highlight-cell">{compareMatch.case_id}</div>
                  <div className={`compare-cell ${highlightMatch(currentCaseDetails.case?.crime_type, compareMatch.crime_type)}`}>
                    {compareMatch.crime_type}
                  </div>
                  <div className="compare-cell">{compareMatch.details.incident_date} {compareMatch.details.incident_time}</div>
                  <div className={`compare-cell ${highlightMatch(currentCaseDetails.case?.zone_id, compareMatch.details.zone_id)}`}>
                    {compareMatch.details.police_station.replace(' Station', '')}
                  </div>
                  <div className="compare-cell">{compareMatch.details.police_station}</div>
                  <div className="compare-cell">
                    {compareMatch.details.vehicles.join(', ') || 'None'}
                  </div>
                  <div className="compare-cell">
                    {compareMatch.details.phones.join(', ') || 'None'}
                  </div>
                  <div className="compare-cell">
                    {compareMatch.details.persons.join(', ') || 'None'}
                  </div>
                  <div className="compare-cell">
                    {compareMatch.details.recommendation_category}
                  </div>
                </div>

              </div>
            </div>

            {/* Admin Diagnostics */}
            {userRole === 'admin' && (
              <div className="admin-diagnostics-bar">
                <div className="diagnostics-header">
                  <ShieldAlert size={14} className="admin-icon" />
                  <span>Internal Matching Diagnostics (Administrator Only)</span>
                </div>
                <div className="subscores-row">
                  {compareMatch.subscores && Object.entries(compareMatch.subscores).map(([k, v]) => (
                    <div key={k} className="subscore-item">
                      <span className="subscore-label">{k}:</span>
                      <span className="subscore-val">{Math.round(v * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="compare-modal-footer">
              <button className="btn btn-secondary" onClick={() => setCompareMatch(null)}>
                Close Comparison
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
