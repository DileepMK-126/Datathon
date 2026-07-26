import React from 'react';

export default function PriorityBadge({ priority }) {
  const getBadgeClass = () => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'priority-badge-critical';
      case 'high': return 'priority-badge-high';
      case 'medium': return 'priority-badge-medium';
      default: return 'priority-badge-low';
    }
  };

  return (
    <span className={`priority-badge ${getBadgeClass()}`}>
      {priority}
    </span>
  );
}
