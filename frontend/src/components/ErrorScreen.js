import React from 'react';

const ErrorScreen = ({ extractionState, onRetry }) => {
  return (
    <div className="error-screen">
      <div className="error-content">
        <div className="error-icon">❌</div>
        <h2>Extraction Failed</h2>
        <p className="error-message">{extractionState.message}</p>
        
        {extractionState.progress.length > 0 && (
          <div className="progress-log">
            <h3>📋 Progress Before Error:</h3>
            <div className="progress-messages">
              {extractionState.progress.map((message, index) => (
                <div key={index} className="progress-message">
                  <span className="progress-icon">✓</span>
                  {message}
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="error-suggestions">
          <h3>💡 Troubleshooting Tips:</h3>
          <ul>
            <li>Verify your username and password are correct</li>
            <li>Check if you need a security token for your network</li>
            <li>Ensure you selected the correct environment (Production/Sandbox)</li>
            <li>Try again - sometimes it's a temporary network issue</li>
            <li>Check if your Salesforce session hasn't expired</li>
            <li>Verify you have API access permissions</li>
          </ul>
        </div>

        <button onClick={onRetry} className="retry-button">
          Try Again
        </button>
      </div>
    </div>
  );
};

export default ErrorScreen;