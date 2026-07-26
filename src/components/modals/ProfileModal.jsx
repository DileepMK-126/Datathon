import React from 'react';
import { Layers3 } from 'lucide-react';
import Modal from '../common/Modal';
import CaseProfile from '../cases/CaseProfile';

export default function ProfileModal({ 
  isOpen, 
  onClose, 
  caseProfile 
}) {
  if (!caseProfile) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      className="profile-modal"
      ariaLabelledBy="profile-title"
    >
      <div className="panel-kicker purple">
        <Layers3 size={15}/> UNIFIED CASE PROFILE
      </div>
      <h2 id="profile-title">
        {caseProfile.case.id} · {caseProfile.case.crime_type}
      </h2>
      <p className="modal-subtitle">{caseProfile.case.summary}</p>
      
      <CaseProfile caseProfile={caseProfile} />
    </Modal>
  );
}
