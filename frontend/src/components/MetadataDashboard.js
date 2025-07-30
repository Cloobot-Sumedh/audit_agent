import React from 'react';

const MetadataDashboard = ({ 
  extractionData, 
  jobId, 
  lists = [], 
  onMetadataTypeClick, 
  onNewExtraction, 
  onExploreMetadata,
  onViewLists 
}) => {
  if (!extractionData || !extractionData.types) {
    return (
      <div className="dashboard-loading">
        <p>No metadata data available. Please run an extraction first.</p>
        <button onClick={onNewExtraction} className="primary-button">
          Start New Extraction
        </button>
      </div>
    );
  }

  const MyListCard = ({ list }) => (
    <div className="my-list-card" onClick={onViewLists}>
      <div className="list-card-header">
        <div className="list-icon">📋</div>
        <div className="list-actions">
          <button className="list-action-btn" onClick={(e) => e.stopPropagation()}>⋯</button>
        </div>
      </div>
      <div className="list-card-content">
        <h3 className="list-title">{list.title}</h3>
        <p className="list-description">{list.description}</p>
      </div>
      <div className="list-card-footer">
        <span className="list-count">{list.items?.length || 0}</span>
      </div>
    </div>
  );

  const MetadataTypeCard = ({ type, count, description, onClick }) => (
    <div className="metadata-type-card" onClick={() => count > 0 && onClick && onClick()}>
      <div className="metadata-card-content">
        <h3 className="metadata-type-title">{type}</h3>
        <div className="metadata-type-count">{count.toString().padStart(2, '0')}</div>
      </div>
    </div>
  );

  // Calculate total items in all lists
  const totalListItems = lists.reduce((total, list) => total + (list.items?.length || 0), 0);

  return (
    <div className="metadata-dashboard-enhanced">
      <div className="dashboard-header">
        <h1>Metadata Dashboard</h1>
        <div className="dashboard-actions">
          <button onClick={onExploreMetadata} className="explore-metadata-btn">
            🔍 Explore Metadata
          </button>
          {lists.length > 0 && (
            <button onClick={onViewLists} className="secondary-button">
              📋 My Lists ({totalListItems})
            </button>
          )}
          <button onClick={onNewExtraction} className="secondary-button">
            New Extraction
          </button>
        </div>
      </div>

      {/* My Lists Section */}
      <div className="my-lists-section">
        <div className="section-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>My Lists</h2>
            <button 
              onClick={onViewLists} 
              className="view-all-btn"
              style={{
                background: 'none',
                border: '1px solid #667eea',
                color: '#667eea',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '0.8rem',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              View All →
            </button>
          </div>
        </div>
        <div className="my-lists-grid">
          {lists.slice(0, 4).map((list) => (
            <MyListCard key={list.id} list={list} />
          ))}
          {lists.length === 0 && (
            <div className="empty-lists-message" style={{
              gridColumn: '1 / -1',
              textAlign: 'center',
              padding: '40px',
              color: '#888',
              background: '#2a2a2a',
              borderRadius: '12px',
              border: '2px dashed #444'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📋</div>
              <h3 style={{ color: 'white', marginBottom: '8px' }}>No Lists Created Yet</h3>
              <p>Start exploring metadata and add objects to lists to organize your work</p>
              <button 
                onClick={onExploreMetadata}
                style={{
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 20px',
                  marginTop: '16px',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
              >
                Explore Metadata
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Metadata Types Section */}
      <div className="metadata-types-section">
        <div className="section-header">
          <h2>Metadata Types</h2>
        </div>
        <div className="metadata-types-grid">
          {extractionData.types.map((item, index) => (
            <MetadataTypeCard
              key={index}
              type={item.type}
              count={item.count}
              description={item.description}
              onClick={() => onMetadataTypeClick(item)}
            />
          ))}
        </div>
      </div>

      {extractionData.outputPath && (
        <div className="output-info">
          <h3>📁 Output Location</h3>
          <p className="output-path">{extractionData.outputPath}</p>
          <small>Files have been extracted and organized by metadata type</small>
        </div>
      )}
    </div>
  );
};

export default MetadataDashboard;