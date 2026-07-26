import React, { useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, Info } from 'lucide-react';

export default function ToastContainer({ toasts, onCloseToast }) {
  return (
    <div className="toast-notifications-container">
      {toasts.map(toast => (
        <ToastItem 
          key={toast.id} 
          toast={toast} 
          onClose={() => onCloseToast(toast.id)} 
        />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 4000); // Auto close after 4 seconds
    return () => clearTimeout(timer);
  }, []);

  const getIcon = () => {
    switch (toast.type) {
      case 'success': return <CheckCircle size={16} className="text-green" />;
      case 'warning': return <AlertTriangle size={16} className="text-orange" />;
      default: return <Info size={16} className="text-blue" />;
    }
  };

  return (
    <div className={`toast-notification-item toast-${toast.type}`}>
      {getIcon()}
      <div className="toast-notification-content">
        <span className="toast-notification-title">{toast.title}</span>
        <p className="toast-notification-desc">{toast.desc}</p>
      </div>
      <button className="toast-notification-close-btn" onClick={onClose}>
        <X size={14} />
      </button>
    </div>
  );
}
