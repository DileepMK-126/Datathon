import React from 'react';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, className = '', ariaLabelledBy, children }) {
  if (!isOpen) return null;
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section 
        className={className} 
        role="dialog" 
        aria-modal="true" 
        aria-labelledby={ariaLabelledBy}
        onMouseDown={e => e.stopPropagation()}
      >
        <button className="close-modal" onClick={onClose} aria-label="Close">
          <X size={20}/>
        </button>
        {children}
      </section>
    </div>
  );
}
