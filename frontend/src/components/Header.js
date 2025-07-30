import React from 'react';

const Header = ({ breadcrumbs, onBreadcrumbClick }) => {
  return (
    <div className="header-container">
      <div className="breadcrumb-nav">
        {breadcrumbs.map((crumb, index) => (
          <React.Fragment key={index}>
            <span 
              className={`breadcrumb-item ${index === breadcrumbs.length - 1 ? 'current' : ''}`}
              onClick={() => index < breadcrumbs.length - 1 && onBreadcrumbClick(crumb.screen)}
            >
              {crumb.label}
            </span>
            {index < breadcrumbs.length - 1 && (
              <span className="breadcrumb-separator">▸</span>
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="header-actions">
        <div className="search-container">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Search for Workspace"
            className="search-input"
          />
        </div>
        
        <div className="header-buttons">
          <button className="header-btn">📊</button>
          <button className="header-btn">🔔</button>
          <button className="header-btn">❓</button>
          <div className="user-menu">
            <div className="user-avatar-small">
              <span>U</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;