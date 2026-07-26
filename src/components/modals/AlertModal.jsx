import React from 'react';
import { AlertTriangle, Sparkles, ArrowRight } from 'lucide-react';
import Modal from '../common/Modal';

export default function AlertModal({ 
  isOpen, 
  onClose, 
  activeAlert, 
  onOpenNetwork 
}) {
  if (!activeAlert) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      className="intel-modal"
      ariaLabelledBy="intel-title"
    >
      <div className="modal-icon">
        <AlertTriangle size={23}/>
      </div>
      <span className="modal-label">
        {activeAlert.type.toUpperCase()} ALERT · NEEDS REVIEW
      </span>
      <h2 id="intel-title">{activeAlert.title}</h2>
      <p>{activeAlert.text}</p>
      
      <div className="modal-details">
        <div>
          <span>Confidence</span>
          <b>{activeAlert.confidence ?? 94}%</b>
        </div>
        <div>
          <span>Linked records</span>
          <b>{activeAlert.linked_records ?? 17}</b>
        </div>
        <div>
          <span>Detected</span>
          <b>{activeAlert.detected ?? activeAlert.time}</b>
        </div>
      </div>
      
      <div className="recommendation">
        <Sparkles size={18}/>
        <div>
          <span>Recommended next step</span>
          <strong>Review linked cases and validate with the duty officer before actioning.</strong>
        </div>
      </div>
      
      <div className="modal-buttons">
        <button className="secondary-button" onClick={onClose}>
          Dismiss
        </button>
        <button className="primary-button" onClick={onOpenNetwork}>
          Open case network <ArrowRight size={17}/>
        </button>
      </div>
    </Modal>
  );
}
