import React from 'react';

export default function Loader({ message = 'Loading...' }) {
  return (
    <div className="loading-auth">
      <div className="loader-spinner"></div>
      <div>{message}</div>
    </div>
  );
}
