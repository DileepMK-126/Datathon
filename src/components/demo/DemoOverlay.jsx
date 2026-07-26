import React, { useEffect, useState } from 'react';
import { Play, Pause, ChevronLeft, ChevronRight, X, Maximize2 } from 'lucide-react';
import ScenarioSelector from './ScenarioSelector';
import ProgressBar from './ProgressBar';
import DemoStepCard from './DemoStepCard';
import DemoControls from './DemoControls';
import { getApi } from '../../services/api';

export default function DemoOverlay({ onExitDemo, userRole }) {
  const [demoState, setDemoState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await getApi('/demo/status');
      setDemoState(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  // Keyboard navigation shortcuts listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.code === 'Space' || e.code === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        handlePrevious();
      } else if (e.code === 'Escape') {
        e.preventDefault();
        onExitDemo();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [demoState]);

  // Highlights and dimming overlays effect
  useEffect(() => {
    if (!demoState?.highlight_class) return;
    
    // Remove existing highlights
    document.querySelectorAll('.demo-highlight-target').forEach(el => {
      el.classList.remove('demo-highlight-target');
    });

    const target = document.querySelector(demoState.highlight_class);
    if (target) {
      target.classList.add('demo-highlight-target');
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [demoState?.highlight_class]);

  // Autoplay intervals effect
  useEffect(() => {
    if (!demoState?.is_playing || demoState?.timer_mode === 'manual') return;
    
    const intervalSecs = demoState.timer_mode === '3min' ? 15 : 25; // timing per step
    const timer = setInterval(() => {
      handleNext();
    }, intervalSecs * 1000);

    return () => clearInterval(timer);
  }, [demoState?.is_playing, demoState?.step_index, demoState?.timer_mode]);

  const handleStart = async (scenario = 'burglary', timer = 'manual') => {
    setLoading(true);
    try {
      const data = await getApi(`/demo/start?scenario=${scenario}&timer=${timer}`);
      setDemoState(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    try {
      const data = await getApi('/demo/next');
      setDemoState(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePrevious = async () => {
    try {
      const data = await getApi('/demo/previous');
      setDemoState(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReset = async () => {
    try {
      const data = await getApi('/demo/reset');
      setDemoState(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleTimerChange = (mode) => {
    handleStart(demoState?.scenario_id ?? 'burglary', mode);
  };

  const handleScenarioChange = (scenarioId) => {
    handleStart(scenarioId, demoState?.timer_mode ?? 'manual');
  };

  const handlePlayToggle = () => {
    if (!demoState) return;
    setDemoState(prev => ({
      ...prev,
      is_playing: !prev.is_playing
    }));
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => setIsFullscreen(true));
    } else {
      document.exitFullscreen().then(() => setIsFullscreen(false));
    }
  };

  if (!demoState) return null;

  return (
    <>
      {/* Dim overlay background */}
      <div className="demo-dim-backdrop" />

      {/* Floating Presenter Command Board */}
      <div className="demo-floating-dashboard-overlay">
        <div className="demo-overlay-header">
          <div className="brief-eyebrow">Sentinel Presentation Walkthrough</div>
          <div className="overlay-header-actions">
            <button className="btn btn-secondary btn-sm px-2" onClick={toggleFullscreen} title="Fullscreen presenter notes">
              <Maximize2 size={13} />
            </button>
            <button className="btn btn-danger btn-sm px-2" onClick={onExitDemo} title="Exit Walkthrough">
              <X size={14} />
            </button>
          </div>
        </div>

        <ScenarioSelector 
          selectedScenarioId={demoState.scenario_id}
          onChangeScenario={handleScenarioChange}
        />

        <ProgressBar 
          currentStep={demoState.step_index}
          totalSteps={demoState.total_steps}
        />

        <DemoStepCard 
          stepTitle={demoState.step_title}
          narration={demoState.narration}
          directive={demoState.directive}
          stepNumber={demoState.step_index + 1}
          totalSteps={demoState.total_steps}
        />

        <DemoControls 
          isPlaying={demoState.is_playing}
          timerMode={demoState.timer_mode}
          onPlayToggle={handlePlayToggle}
          onTimerChange={handleTimerChange}
          onNext={handleNext}
          onPrevious={handlePrevious}
          onReset={handleReset}
        />
      </div>
    </>
  );
}
