import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function NetworkGraph({ 
  liveData, 
  networkLayout, 
  onReviewUnifiedCase 
}) {
  return (
    <div className="network-body">
      <div className="network-graph">
        <svg viewBox="0 0 560 300">
          <g className="network-lines">
            {(liveData?.network?.edges ?? []).slice(0, 12).map(edge => {
              const source = networkLayout.find(node => node.id === edge.source);
              const target = networkLayout.find(node => node.id === edge.target);
              return source && target ? (
                <line 
                  key={`${edge.source}-${edge.target}`} 
                  x1={source.x} 
                  y1={source.y} 
                  x2={target.x} 
                  y2={target.y}
                />
              ) : null;
            })}
          </g>
          
          {networkLayout.length ? (
            networkLayout.map(node => (
              <g 
                key={node.id} 
                className={`node ${
                  node.kind === 'case' 
                    ? 'node-case' 
                    : node.kind === 'phone' 
                      ? 'node-key' 
                      : 'node-person'
                }`}
              >
                <circle cx={node.x} cy={node.y} r={node.kind === 'phone' ? 40 : 31}/>
                <text x={node.x} y={node.y - 3}>{node.label.slice(0, 11)}</text>
                <text x={node.x} y={node.y + 11}>{node.kind}</text>
              </g>
            ))
          ) : (
            <>
              <g className="network-lines">
                <line x1="110" y1="148" x2="270" y2="92"/>
                <line x1="110" y1="148" x2="265" y2="220"/>
                <line x1="270" y1="92" x2="412" y2="145"/>
                <line x1="265" y1="220" x2="412" y2="145"/>
              </g>
              <g className="node node-case">
                <circle cx="110" cy="148" r="37"/>
                <text x="110" y="145">FIR</text>
                <text x="110" y="160">#7821</text>
              </g>
              <g className="node node-person">
                <circle cx="270" cy="92" r="35"/>
                <text x="270" y="90">R. Shah</text>
                <text x="270" y="105">person</text>
              </g>
              <g className="node node-key">
                <circle cx="412" cy="145" r="43"/>
                <text x="412" y="141">+91•••</text>
                <text x="412" y="156">identifier</text>
              </g>
            </>
          )}
        </svg>
      </div>
      
      <div className="network-side">
        <span>CLUSTER SUMMARY</span>
        <strong>{liveData?.network?.summary ?? '3 case files linked'}</strong>
        <p>
          {liveData?.network?.method ?? 
            'One masked device identifier and two co-occurrence records link the entities across 14 days.'
          }
        </p>
        <div className="link-chip"><i></i> Shared masked identifier</div>
        <div className="link-chip"><i></i> Human validation required</div>
        <button className="primary-button" onClick={onReviewUnifiedCase}>
          Review unified case <ArrowRight size={17}/>
        </button>
      </div>
    </div>
  );
}
