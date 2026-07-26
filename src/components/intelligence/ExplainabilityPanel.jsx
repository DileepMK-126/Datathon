import React, { useState, useEffect } from 'react';
import { Sparkles, HelpCircle } from 'lucide-react';
import Card from '../common/Card';
import Loader from '../common/Loader';
import DriverBar from './DriverBar';
import ConfidenceRing from './ConfidenceRing';
import EvidenceChip from './EvidenceChip';
import SummaryCard from './SummaryCard';
import { getApi } from '../../services/api';

export default function ExplainabilityPanel({ zoneId, userRole }) {
  const [explanationData, setExplanationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchExplanation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getApi(`/risks/explain/${zoneId}`);
      setExplanationData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (zoneId) {
      fetchExplanation();
    }
  }, [zoneId]);

  const handleExportJson = () => {
    if (!explanationData) return;
    const blob = new Blob([JSON.stringify(explanationData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `risk-explanation-${zoneId}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPdf = () => {
    alert("Risk explanation brief prepared for printing. Press Ctrl+P/Cmd+P to print report.");
    window.print();
  };

  return (
    <Card 
      title={`Explainable AI Risk Attribution — ${explanationData?.zone_name ?? 'Loading'}`}
      kicker="XAI PREDICTION DRIVERS"
      kickerTone="red"
      className="explainability-panel-card"
    >
      {loading && <Loader message="Attributing local model decisions..." />}
      {error && <div className="error-panel">{error}</div>}

      {!loading && !error && explanationData && (
        <div className="xai-panel-layout">
          
          {/* Top row: Summary & Confidence */}
          <div className="xai-top-row">
            <ConfidenceRing 
              score={explanationData.confidence} 
              level={explanationData.confidence_level} 
            />
            <SummaryCard 
              summary={explanationData.summary}
              onExportJson={handleExportJson}
              onExportPdf={handleExportPdf}
              userRole={userRole}
            />
          </div>

          {/* Bottom row: Contributors split grid */}
          <div className="contributors-split-grid">
            
            {/* Column 1: Positive Drivers */}
            <div className="contributors-column">
              <h4 className="column-label text-red">Risk Factors (Positive Attributions)</h4>
              {explanationData.positive_contributors.length === 0 ? (
                <div className="no-contributors-text">No significant positive attributions.</div>
              ) : (
                explanationData.positive_contributors.map(driver => (
                  <div key={driver.feature} className="driver-wrapper-item">
                    <DriverBar 
                      feature={driver.feature}
                      impact={driver.impact}
                      direction={driver.direction}
                      value={driver.value}
                    />
                    <EvidenceChip evidence={driver.evidence} />
                  </div>
                ))
              )}
            </div>

            {/* Column 2: Negative Drivers */}
            <div className="contributors-column">
              <h4 className="column-label text-green">Mitigating Factors (Negative Attributions)</h4>
              {explanationData.negative_contributors.length === 0 ? (
                <div className="no-contributors-text text-muted">No mitigating factors active.</div>
              ) : (
                explanationData.negative_contributors.map(driver => (
                  <div key={driver.feature} className="driver-wrapper-item">
                    <DriverBar 
                      feature={driver.feature}
                      impact={driver.impact}
                      direction={driver.direction}
                      value={driver.value}
                    />
                    <EvidenceChip evidence={driver.evidence} />
                  </div>
                ))
              )}
            </div>

          </div>

        </div>
      )}
    </Card>
  );
}
