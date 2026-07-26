import React, { useState } from 'react';
import { ShieldCheck, HelpCircle, Check, Clock } from 'lucide-react';
import PriorityBadge from './PriorityBadge';
import ImpactCard from './ImpactCard';
import EvidenceAccordion from './EvidenceAccordion';

export default function RecommendationCard({ rec, userRole }) {
  const [approved, setApproved] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleApprove = async () => {
    if (userRole !== 'supervisor' && userRole !== 'admin') {
      alert("Permission denied. Only Supervisors and Administrators can approve and dispatch recommendation actions.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`/api/recommendations/${rec.id}/approve`, { method: 'POST' });
      if (res.ok) {
        setApproved(true);
      }
    } catch (err) {
      alert('Failed to approve recommendation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`recommendation-card-item ${approved ? 'approved' : ''}`}>
      <div className="recommendation-card-header">
        <div className="card-badge-row">
          <PriorityBadge priority={rec.priority} />
          <span className="rec-confidence-percentage">{rec.confidence}% Confidence</span>
        </div>
        <div className="rec-shift-pill">
          <Clock size={12} />
          <span>{rec.recommended_shift} ({rec.duration_hours}h)</span>
        </div>
      </div>

      <h4 className="recommendation-card-title">{rec.category}</h4>
      <p className="recommendation-card-explanation">"{rec.explanation}"</p>

      <ImpactCard 
        deterrence={rec.deterrence_level}
        responseTime={rec.expected_response_reduction}
        trustIndex={rec.community_trust_index}
      />

      <EvidenceAccordion 
        evidence={rec.supporting_evidence}
        relatedCases={rec.related_cases}
      />

      <div className="recommendation-card-footer">
        <div className="human-review-disclaimer">
          <ShieldCheck size={12} className="text-orange" />
          <span>Verification Required</span>
        </div>

        <button 
          type="button"
          className={`btn btn-sm ${approved ? 'btn-success' : 'btn-primary'}`}
          onClick={handleApprove}
          disabled={approved || loading}
        >
          {loading ? 'Approving...' : approved ? (
            <>
              <Check size={14} />
              <span>Approved</span>
            </>
          ) : (
            <span>Approve Action</span>
          )}
        </button>
      </div>
    </div>
  );
}
