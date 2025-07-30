import React from 'react';

const ObjectsList = ({ 
  metadataType, 
  files, 
  loading, 
  onObjectClick, 
  onAddToList, 
  selectedList 
}) => {
  const getObjectIcon = (filename) => {
    if (filename.endsWith('.cls')) return '⚡';
    if (filename.endsWith('.trigger')) return '🔄';
    if (filename.endsWith('.object')) return '📦';
    if (filename.endsWith('.flow')) return '🔀';
    if (filename.endsWith('.layout')) return '📋';
    return '📄';
  };

  const getObjectType = (filename) => {
    if (filename.endsWith('.cls')) return 'Apex Classes';
    if (filename.endsWith('.trigger')) return 'Apex Classes';
    if (filename.endsWith('.object')) return 'Custom Object';
    if (filename.endsWith('.flow')) return 'Flow';
    if (filename.endsWith('.layout')) return 'Layout';
    return 'Unknown';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="objects-list">
      <div className="objects-header">
        <div className="header-content">
          <div className="metadata-type-info">
            <span className="type-icon">{metadataType?.icon}</span>
            <div className="type-details">
              <h2>{metadataType?.type}</h2>
              <p>Search for {metadataType?.type}</p>
            </div>
          </div>
          <div className="search-container">
            <input 
              type="text" 
              placeholder={`Search for ${metadataType?.type}`}
              className="search-input"
            />
            <span className="search-icon">🔍</span>
          </div>
        </div>
      </div>

      <div className="objects-content">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner small"></div>
            <p>Loading {metadataType?.type}...</p>
          </div>
        ) : (
          <>
            <div className="objects-count">
              <span className="count-text">All Types</span>
              <span className="count-number">{files.length}</span>
            </div>

            <div className="objects-grid">
              {files.length > 0 ? (
                files.map((file, index) => (
                  <div 
                    key={index} 
                    className="object-card"
                    onClick={() => onObjectClick(file)}
                  >
                    <div className="object-header">
                      <div className="object-icon">
                        {getObjectIcon(file.name)}
                      </div>
                      <div className="object-actions">
                        <button 
                          className="add-to-list-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            onAddToList(file.name);
                          }}
                          title={`Add to ${selectedList}`}
                        >
                          <span className="plus-icon">⊕</span>
                        </button>
                      </div>
                    </div>
                    
                    <div className="object-content">
                      <h3 className="object-name">{file.name}</h3>
                      <p className="object-description">
                        {getObjectType(file.name)}
                      </p>
                      <div className="object-meta">
                        {file.lastModified && (
                          <span className="meta-date">{formatDate(file.lastModified)}</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="object-badge">
                      <span className="badge-text">{getObjectType(file.name)}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-objects">
                  <p>No {metadataType?.type} found</p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ObjectsList;