import React from 'react';
import { Info } from 'lucide-react';

export default function SimilarityExplanation({ reasoning }) {
  return (
    <div className="similarity-explanation">
      <Info size={14} className="xai-icon" />
      <span className="xai-text">{reasoning}</span>
    </div>
  );
}
