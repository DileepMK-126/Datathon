import React from 'react';

export default function SimilarityBadge({ score, confidence }) {
  let badgeClass = 'similarity-badge ';
  
  if (score >= 90) {
    badgeClass += 'badge-critical';
  } else if (score >= 80) {
    badgeClass += 'badge-strong';
  } else if (score >= 70) {
    badgeClass += 'badge-moderate';
  } else {
    badgeClass += 'badge-weak';
  }

  return (
    <span className={badgeClass}>
      {score}% - {confidence}
    </span>
  );
}
