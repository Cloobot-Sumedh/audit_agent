import React from 'react';

const LoadingScreen = ({ extractionState, onCancel }) => {
  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="loading-spinner"></div>
        <h2>Extracting Metadata...</h2>
        <p className="loading-message">{extractionState.message}</p>
        
        <div className="progress-log">
          <h3>Progress Log:</h3>
          <div className="progress-messages">
            {extractionState.progress.map((message, index) => (
              <div key={index} className="progress-message">
                <span className="progress-icon">✓</span>
                {message}
              </div>
            ))}
            {extractionState.status === 'loading' && (
              <div className="progress-message current">
                <span className="progress-icon loading">⟳</span>
                Processing...
              </div>
            )}
          </div>
        </div>

        <button onClick={onCancel} className="cancel-button">
          Cancel & Start Over
        </button>
      </div>
    </div>
  );
};

export default LoadingScreen;