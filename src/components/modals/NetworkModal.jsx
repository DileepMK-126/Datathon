import React from 'react';
import { Network } from 'lucide-react';
import Modal from '../common/Modal';
import NetworkGraph from '../network/NetworkGraph';

export default function NetworkModal({ 
  isOpen, 
  onClose, 
  liveData, 
  networkLayout, 
  onReviewUnifiedCase,
  userRole
}) {
  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      className="network-modal"
      ariaLabelledBy="network-title"
    >
      <div className="panel-kicker purple">
        <Network size={15}/> ENTITY RESOLUTION
      </div>
      <h2 id="network-title">Connected case network</h2>
      <p className="modal-subtitle">
        The graph groups records through shared identifiers. Connections are leads, not proof of involvement.
      </p>
      
      <NetworkGraph 
        userRole={userRole}
      />
    </Modal>
  );
}
