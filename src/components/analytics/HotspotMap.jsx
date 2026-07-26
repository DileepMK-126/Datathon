import React from 'react';
import { MapPin, ZoomIn, ZoomOut, ChevronDown, ChevronRight } from 'lucide-react';
import Card from '../common/Card';

export default function HotspotMap({ 
  liveZones, 
  activeZone, 
  setActiveZone, 
  scaleText, 
  metrics, 
  liveData, 
  onViewIntelligence 
}) {
  const mapControls = (
    <div className="map-controls">
      <button className="period-button">{scaleText} <ChevronDown size={15}/></button>
      <button className="icon-button small"><ZoomIn size={17}/></button>
      <button className="icon-button small"><ZoomOut size={17}/></button>
    </div>
  );

  return (
    <Card 
      title="Incident hotspots" 
      kicker="GEOSPATIAL DETECTION" 
      className="map-panel" 
      headerActions={mapControls}
    >
      <div className="map-legend">
        <span><i className="legend-dot critical"></i> Critical</span>
        <span><i className="legend-dot high"></i> High</span>
        <span><i className="legend-dot watch"></i> Watch</span>
        <span className="cluster-label">DBSCAN CLUSTERS</span>
      </div>
      
      <div className="city-map">
        <div className="river"><span>HARBOR RIVER</span></div>
        <div className="road road-one"></div>
        <div className="road road-two"></div>
        <div className="road road-three"></div>
        <div className="road road-four"></div>
        <div className="district district-a">NORTH<br/>WARD</div>
        <div className="district district-b">OLD TOWN</div>
        <div className="district district-c">RIVERGATE</div>
        <div className="district district-d">CENTRAL</div>
        
        {liveZones.map(zone => (
          <button 
            key={zone.id} 
            className={`hotspot ${zone.tone} ${activeZone.id === zone.id ? 'selected' : ''}`} 
            style={{ left: `${zone.x}%`, top: `${zone.y}%` }} 
            onClick={() => setActiveZone(zone)} 
            aria-label={`Show ${zone.name} hotspot`}
          >
            <span className="hotspot-core"></span>
            <span className="hotspot-count">{zone.incidents}</span>
          </button>
        ))}
        
        <div className="map-overlay-card">
          <span>SELECTED CLUSTER</span>
          <strong>{activeZone.name}</strong>
          <p><b>{activeZone.incidents}</b> incidents · <em>{activeZone.delta}</em> vs baseline</p>
          <button onClick={onViewIntelligence}>
            View intelligence <ChevronRight size={14}/>
          </button>
        </div>
      </div>
      
      <div className="map-footer">
        <span><i className="pulse-dot"></i> {metrics?.active_incidents ?? 247} records analyzed</span>
        <span>{liveData ? 'Model run complete' : 'Updated just now'}</span>
      </div>
    </Card>
  );
}
