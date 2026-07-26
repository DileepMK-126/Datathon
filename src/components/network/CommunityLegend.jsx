import React from 'react';

export default function CommunityLegend({ communities }) {
  if (!communities || communities.length === 0) return null;

  // Let's use a nice selection of modern colors
  const colors = ["#a855f7", "#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#6366f1", "#ec4899", "#14b8a6"];

  return (
    <div className="community-legend-card">
      <div className="community-legend-title">Detected Sub-networks / Communities</div>
      <div className="community-legend-grid">
        {communities.map((c, index) => (
          <div key={c.community_id} className="community-legend-item">
            <span 
              className="community-color-swatch"
              style={{ backgroundColor: colors[index % colors.length] }}
            />
            <span className="community-label">Cluster {c.community_id} ({c.members.length} nodes)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
