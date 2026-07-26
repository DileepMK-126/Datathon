import React from 'react';

export default function Card({ title, kicker, kickerTone = '', className = '', headerActions = null, children }) {
  return (
    <article className={`panel ${className}`}>
      <div className="panel-head">
        <div>
          {kicker && <div className={`panel-kicker ${kickerTone}`}>{kicker}</div>}
          <h2>{title}</h2>
        </div>
        {headerActions}
      </div>
      {children}
    </article>
  );
}
