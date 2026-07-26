import React from 'react';

export default function ScenarioSelector({ selectedScenarioId, onChangeScenario }) {
  const scenarios = [
    { id: 'burglary', name: 'Burglary Scenario' },
    { id: 'vehicle_theft', name: 'Vehicle Theft Scenario' },
    { id: 'drug_trafficking', name: 'Drug Trafficking Scenario' },
    { id: 'repeat_offender', name: 'Repeat Offender Scenario' },
    { id: 'gang_network', name: 'Gang Network Topology' },
  ];

  return (
    <div className="scenario-selector-container">
      <label htmlFor="scenario-select" className="scenario-select-label">Walkthrough Scenario:</label>
      <div className="select-wrapper">
        <select 
          id="scenario-select"
          value={selectedScenarioId} 
          onChange={e => onChangeScenario(e.target.value)}
        >
          {scenarios.map(sc => (
            <option key={sc.id} value={sc.id}>{sc.name}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
