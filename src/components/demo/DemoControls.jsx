import React from 'react';
import { Play, Pause, ChevronLeft, ChevronRight, RotateCcw, Clock } from 'lucide-react';

export default function DemoControls({
  isPlaying,
  timerMode,
  onPlayToggle,
  onTimerChange,
  onNext,
  onPrevious,
  onReset
}) {
  return (
    <div className="demo-controls-container">
      {/* Step navigation buttons */}
      <div className="demo-step-nav-buttons">
        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onPrevious}
          title="Previous Step (Left Arrow)"
        >
          <ChevronLeft size={16} />
          <span>Prev</span>
        </button>

        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onReset}
          title="Restart Workflow"
        >
          <RotateCcw size={14} />
          <span>Reset</span>
        </button>

        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onNext}
          title="Next Step (Right Arrow / Space)"
        >
          <span>Next</span>
          <ChevronRight size={16} />
        </button>
      </div>

      {/* Auto play interval settings */}
      <div className="demo-play-controls-row">
        <button 
          className={`btn btn-sm ${isPlaying ? 'btn-danger' : 'btn-success'}`}
          onClick={onPlayToggle}
        >
          {isPlaying ? (
            <>
              <Pause size={14} />
              <span>Pause Auto</span>
            </>
          ) : (
            <>
              <Play size={14} />
              <span>Play Auto</span>
            </>
          )}
        </button>

        <div className="select-wrapper">
          <Clock size={12} className="clock-icon" />
          <select 
            value={timerMode} 
            onChange={e => onTimerChange(e.target.value)}
          >
            <option value="manual">Manual Progress</option>
            <option value="3min">3 Min Presentation</option>
            <option value="5min">5 Min Presentation</option>
          </select>
        </div>
      </div>
    </div>
  );
}
