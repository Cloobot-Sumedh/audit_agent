import React, { useEffect, useState } from 'react';

const QuickAddNotification = ({ 
  isVisible, 
  objectName,
  listName,
  onClose, 
  onChangeList,
  onUndo,
  duration = 4000 
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [timeLeft, setTimeLeft] = useState(duration / 1000);
  const [showChangeButton, setShowChangeButton] = useState(false);

  useEffect(() => {
    if (isVisible) {
      console.log('🔄 QuickAddNotification isVisible:', isVisible);
      setIsAnimating(true);
      setTimeLeft(12); // Updated to 12 seconds to match the new duration
      setShowChangeButton(true); // Show change button immediately
      console.log('🔄 Setting showChangeButton to true');
      
      // Hide change button after 6 seconds (increased from 3 seconds)
      const changeButtonTimer = setTimeout(() => {
        console.log('🔄 Hiding change button after 6 seconds');
        setShowChangeButton(false);
      }, 6000);
      
      // Countdown timer
      const countdownInterval = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(countdownInterval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      // Auto close timer - extended duration when change button is shown
      const timer = setTimeout(() => {
        handleClose();
      }, 12000); // 12 seconds total (increased from 9 seconds)

      return () => {
        clearTimeout(timer);
        clearTimeout(changeButtonTimer);
        clearInterval(countdownInterval);
      };
    }
  }, [isVisible, duration]);

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      onClose();
    }, 300); // Match the CSS transition duration
  };

  const handleUndo = () => {
    setIsAnimating(false);
    setTimeout(() => {
      onUndo();
    }, 300);
  };

  const handleChangeList = () => {
    console.log('🔄 Change button clicked!');
    setIsAnimating(false);
    setTimeout(() => {
      console.log('🔄 Calling onChangeList function');
      onChangeList();
    }, 300);
  };

  if (!isVisible) return null;

  return (
    <div 
      className="quick-add-notification"
      style={{
        position: 'fixed',
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        color: 'white',
        padding: '12px 16px',
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(16, 185, 129, 0.4)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        zIndex: 10000,
        minWidth: '350px',
        maxWidth: '450px',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        transform: isAnimating ? 'translateX(-50%)' : 'translateX(-50%) scale(0.9)',
        opacity: isAnimating ? 1 : 0,
        transition: 'all 0.3s ease-in-out',
        fontSize: '0.9rem',
        fontWeight: '500'
      }}
    >
      {/* Success Icon */}
      <div 
        style={{
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '50%',
          width: '32px',
          height: '32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px',
          fontWeight: 'bold',
          flexShrink: 0
        }}
      >
        ✓
      </div>
      
      {/* Message Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: '600', marginBottom: '2px' }}>
          {objectName} added to {listName}
        </div>
        <div style={{ 
          opacity: 0.9, 
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <span>Auto-closing in {timeLeft}s</span>
          <div 
            style={{
              width: '60px',
              height: '2px',
              background: 'rgba(255, 255, 255, 0.3)',
              borderRadius: '1px',
              overflow: 'hidden'
            }}
          >
            <div 
              style={{
                width: `${(timeLeft / 12) * 100}%`,
                height: '100%',
                background: 'white',
                transition: 'width 1s linear',
                borderRadius: '1px'
              }}
            />
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        {console.log('🔄 Rendering - showChangeButton:', showChangeButton)}
        {showChangeButton && (
          <button 
            onClick={handleChangeList}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '6px',
              padding: '6px 12px',
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontWeight: '500',
              whiteSpace: 'nowrap',
              animation: 'fadeIn 0.3s ease-in-out, pulse 2s infinite'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.3)';
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)';
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            }}
          >
            Change
          </button>
        )}
        
        <button 
          onClick={handleUndo}
          style={{
            background: 'rgba(239, 68, 68, 0.2)',
            color: 'white',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '6px',
            padding: '6px 12px',
            fontSize: '0.8rem',
            cursor: 'pointer',
            transition: 'all 0.2s',
            fontWeight: '500',
            whiteSpace: 'nowrap'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(239, 68, 68, 0.3)';
            e.target.style.borderColor = 'rgba(239, 68, 68, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'rgba(239, 68, 68, 0.2)';
            e.target.style.borderColor = 'rgba(239, 68, 68, 0.4)';
          }}
        >
          Undo
        </button>
        
        <button 
          onClick={handleClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            fontSize: '18px',
            padding: '4px',
            width: '24px',
            height: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%',
            opacity: 0.8,
            transition: 'all 0.2s',
            flexShrink: 0
          }}
          onMouseEnter={(e) => {
            e.target.style.opacity = '1';
            e.target.style.background = 'rgba(255, 255, 255, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.target.style.opacity = '0.8';
            e.target.style.background = 'none';
          }}
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default QuickAddNotification;