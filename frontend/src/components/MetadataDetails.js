import React, { useState, useEffect } from 'react';
import MetadataObjectView from './MetadataObjectView';

const API_BASE_URL = 'http://localhost:5000/api';

const MetadataDetails = ({
  initialSelectedType,
  allTypes,
  totalFiles,
  jobId,
  onBackToDashboard,
  onOpenDiagram,
  onAddToList,
  onShowListModal,
  lastUsedListId,
  lists = [],
  onNavigateToDependency  // Add new prop for dependency navigation
}) => {
  const [activeType, setActiveType] = useState(initialSelectedType || { type: 'All Types', count: totalFiles });
  const [metadataFiles, setMetadataFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [selectedObject, setSelectedObject] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Use actual metadata types from backend, prepend "All Types"
  const metadataTypes = [
    { type: 'All Types', count: totalFiles },
    ...allTypes
  ];

  useEffect(() => {
    if (jobId && activeType) {
      loadMetadataFiles();
      setSelectedObject(null); // Clear selection when type changes
    }
  }, [activeType, jobId]);

  const loadMetadataFiles = async () => {
    setLoadingFiles(true);
    
    try {
      if (activeType.type === 'All Types') {
        // Fetch all metadata components for the job
        const response = await fetch(`${API_BASE_URL}/metadata-components/${jobId}`);
        
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            setMetadataFiles(result.components || []);
          } else {
            console.error('API returned error:', result.error);
            setMetadataFiles([]);
          }
        } else {
          console.error('HTTP error:', response.status);
          setMetadataFiles([]);
        }
      } else {
        // Fetch metadata components for specific type
        const typeToFetch = encodeURIComponent(activeType.type);
        const response = await fetch(`${API_BASE_URL}/metadata-components/${jobId}/type/${typeToFetch}`);
        
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            setMetadataFiles(result.components || []);
          } else {
            console.error('API returned error:', result.error);
            setMetadataFiles([]);
          }
        } else {
          console.error('HTTP error:', response.status);
          setMetadataFiles([]);
        }
      }
    } catch (error) {
      console.error('Error fetching metadata components:', error);
      setMetadataFiles([]);
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleTypeSelect = (typeObj) => {
    setActiveType(typeObj);
    setSearchTerm('');
  };

  const handleSearch = async (searchTerm) => {
    setSearchTerm(searchTerm);
    setLoadingFiles(true);
    
    try {
      if (activeType.type === 'All Types') {
        // For "All Types", we'll filter client-side since we already have all components
        setLoadingFiles(false);
        return;
      }
      
      if (searchTerm.trim() === '') {
        // If search is empty, load all components for the type
        await loadMetadataFiles();
        return;
      }
      
      // Use the search endpoint for specific types
      const typeToFetch = encodeURIComponent(activeType.type);
      const response = await fetch(`${API_BASE_URL}/metadata-components/${jobId}/type/${typeToFetch}/search?search_term=${encodeURIComponent(searchTerm)}`);
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setMetadataFiles(result.components || []);
        } else {
          console.error('Search API returned error:', result.error);
          setMetadataFiles([]);
        }
      } else {
        console.error('Search HTTP error:', response.status);
        setMetadataFiles([]);
      }
    } catch (error) {
      console.error('Error searching metadata components:', error);
      setMetadataFiles([]);
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleObjectSelect = (object) => {
    console.log('Object selected:', object);
    setSelectedObject(object);
  };

  const handleOpenDiagram = (object) => {
    console.log('Opening diagram for object:', object);
    
    if (onOpenDiagram) {
      onOpenDiagram(object);
    } else {
      console.error('onOpenDiagram function not provided to MetadataDetails');
    }
  };

  const handleAddToList = (selectedListIds, metadataObject, listName = null) => {
    console.log('Adding to list:', metadataObject, 'Lists:', selectedListIds);
    if (onAddToList) {
      onAddToList(selectedListIds, metadataObject, listName);
    } else {
      console.error('onAddToList function not provided to MetadataDetails');
    }
  };

  const handleShowListModal = (metadataObject) => {
    console.log('Showing list modal for object:', metadataObject);
    if (onShowListModal) {
      onShowListModal(metadataObject);
    } else {
      console.error('onShowListModal function not provided to MetadataDetails');
    }
  };

  const handleNavigateToDependency = (dependencyComponent) => {
    console.log('Navigating to dependency component:', dependencyComponent);
    
    // Set the dependency component as the selected object
    setSelectedObject({
      amc_id: dependencyComponent.amc_id,
      amc_dev_name: dependencyComponent.amc_dev_name,
      amc_label: dependencyComponent.amc_label,
      amc_notes: dependencyComponent.amc_notes,
      amc_created_timestamp: dependencyComponent.amc_created_timestamp,
      amc_last_modified: dependencyComponent.amc_last_modified,
      metadata_type_name: dependencyComponent.metadata_type_name,
      name: dependencyComponent.amc_dev_name || dependencyComponent.amc_label
    });
    
    // If there's a parent navigation handler, call it too
    if (onNavigateToDependency) {
      onNavigateToDependency(dependencyComponent);
    }
  };

  // For "All Types", filter client-side since we have all components
  // For specific types, the filtering is done server-side
  const filteredObjects = activeType.type === 'All Types' 
    ? metadataFiles.filter(obj =>
        obj.amc_dev_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        obj.amc_label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        obj.amc_notes?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : metadataFiles;

  if (!jobId) {
    return (
      <div className="metadata-details-empty">
        <p>No extraction job found. Please select a metadata type from the dashboard.</p>
        <button onClick={onBackToDashboard} className="primary-button">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="metadata-explorer">
      <div className="explorer-layout">
        {/* Left Sidebar - Metadata Types */}
        <div className="explorer-sidebar">
          <div className="sidebar-header">
            <h3>Metadata Types</h3>
            <button className="collapse-btn" onClick={onBackToDashboard} title="Back to Dashboard">
              ← Back
            </button>
          </div>
          <div className="sidebar-search">
            <input 
              type="text" 
              placeholder="Search for Metadata"
              className="search-input"
            />
            <span className="search-icon">🔍</span>
          </div>
          <div className="types-list">
            {metadataTypes.map((typeObj, index) => (
              <div
                key={index}
                className={`type-item ${activeType.type === typeObj.type ? 'active' : ''}`}
                onClick={() => handleTypeSelect(typeObj)}
              >
                <span className="type-name">{typeObj.type}</span>
                <span className="type-count">{typeObj.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content - Objects List */}
        <div className="explorer-main">
          <div className="main-header">
            <div className="header-content">
              <h2>{activeType.type}</h2>
              <div className="main-search">
                <input 
                  type="text" 
                  placeholder="Search objects"
                  className="search-input"
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                />
                <span className="search-icon">🔍</span>
              </div>
            </div>
          </div>
          
          <div className="objects-content">
            {loadingFiles ? (
              <div className="loading-state">
                <div className="loading-spinner small"></div>
                <p>Loading {activeType.type}...</p>
              </div>
            ) : (
              <div className="objects-list">
                <div className="objects-count" style={{ 
                  marginBottom: '20px', 
                  color: '#ccc',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span>
                    <strong style={{ color: 'white' }}>{filteredObjects.length}</strong> objects
                    {searchTerm && ` matching "${searchTerm}"`}
                  </span>
                </div>

                {filteredObjects.length > 0 ? (
                  filteredObjects.map((object, index) => (
                    <div 
                      key={index}
                      className={`object-item ${selectedObject?.amc_dev_name === object.amc_dev_name ? 'active' : ''}`}
                      onClick={() => handleObjectSelect(object)}
                    >
                      <div className="object-main">
                        <h4 className="object-name">{object.amc_dev_name || object.amc_label}</h4>
                        <div className="object-meta">
                          <span className="meta-item">
                            <strong>Type:</strong> {object.metadata_type_name || activeType.type}
                          </span>
                          <span className="meta-item">
                            <strong>Created:</strong> {new Date(object.amc_created_timestamp).toLocaleDateString()}
                          </span>
                          {object.amc_last_modified && (
                            <span className="meta-item">
                              <strong>Modified:</strong> {new Date(object.amc_last_modified).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="object-actions">
                        <button 
                          className="add-to-list-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleShowListModal(object);
                          }}
                          title="Add to List"
                        >
                          ⊕
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <div className="empty-icon">📄</div>
                    <h3>No {activeType.type} found</h3>
                    <p>
                      {searchTerm 
                        ? `No components matching "${searchTerm}" found.`
                        : `No ${activeType.type} components available for this extraction job.`
                      }
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar - Object Details */}
        <div className="explorer-details">
          <div className="details-header">
            <div className="header-content">
              <h3>Metadata Details</h3>
              <button className="collapse-btn">📁</button>
            </div>
          </div>
          <div className="details-content">
            {selectedObject ? (
              <MetadataObjectView
                selectedObject={selectedObject}
                jobId={jobId}
                onOpenDiagram={handleOpenDiagram}
                onAddToList={handleAddToList}
                onShowListModal={handleShowListModal}
                lastUsedListId={lastUsedListId}
                lists={lists}
                onNavigateToDependency={handleNavigateToDependency}
              />
            ) : (
              <div className="no-selection">
                <div className="no-selection-icon">📄</div>
                <h4>Select an object</h4>
                <p>Choose an object from the list to see its metadata details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetadataDetails;