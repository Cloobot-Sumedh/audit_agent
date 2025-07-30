import React, { useEffect, useState } from 'react';

const NotificationToast = ({ 
  isVisible, 
  message, 
  onClose, 
  type = 'success',
  duration = 3000 
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration]);

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      onClose();
    }, 300); // Match the CSS transition duration
  };

  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case 'success': return '✓';
      case 'error': return '✗';
      case 'warning': return '⚠';
      case 'info': return 'ℹ';
      default: return '✓';
    }
  };

  const getColors = () => {
    switch (type) {
      case 'success': return { bg: '#10b981', border: '#059669' };
      case 'error': return { bg: '#ef4444', border: '#dc2626' };
      case 'warning': return { bg: '#f59e0b', border: '#d97706' };
      case 'info': return { bg: '#3b82f6', border: '#2563eb' };
      default: return { bg: '#10b981', border: '#059669' };
    }
  };

  const colors = getColors();

  return (
    <div 
      className="notification-toast"
      style={{
        position: 'fixed',
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: colors.bg,
        color: 'white',
        padding: '12px 16px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        zIndex: 10000,
        minWidth: '300px',
        maxWidth: '400px',
        border: `1px solid ${colors.border}`,
        transform: isAnimating ? 'translateX(-50%)' : 'translateX(-50%) scale(0.9)',
        opacity: isAnimating ? 1 : 0,
        transition: 'all 0.3s ease-in-out',
        fontSize: '0.9rem',
        fontWeight: '500'
      }}
    >
      <div 
        style={{
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '50%',
          width: '24px',
          height: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '14px',
          fontWeight: 'bold'
        }}
      >
        {getIcon()}
      </div>
      
      <div style={{ flex: 1 }}>
        {message}
      </div>
      
      <button 
        onClick={handleClose}
        style={{
          background: 'none',
          border: 'none',
          color: 'white',
          cursor: 'pointer',
          fontSize: '16px',
          padding: '0',
          width: '20px',
          height: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '50%',
          opacity: 0.7,
          transition: 'opacity 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.opacity = '1'}
        onMouseLeave={(e) => e.target.style.opacity = '0.7'}
      >
        ×
      </button>
    </div>
  );
};

export default NotificationToast;