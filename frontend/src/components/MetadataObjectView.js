import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000/api';

const MetadataObjectView = ({ 
  selectedObject, 
  jobId, 
  onOpenDiagram, 
  onAddToList,
  lastUsedListId,
  lists = [],
  onShowListModal,
  onNavigateToDependency  // Add new prop for dependency navigation
}) => {
  const [objectDetails, setObjectDetails] = useState({
    summary: '',
    relationships: null,
    xml: '',
  });
  const [loading, setLoading] = useState({
    summary: false,
    relationships: false,
    xml: false,
  });
  const [notes, setNotes] = useState('');
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [savingNotes, setSavingNotes] = useState(false);

  useEffect(() => {
    if (selectedObject && selectedObject.amc_id) {
      loadAllDetails();
      setNotes(selectedObject.amc_notes || '');
    }
  }, [selectedObject, selectedObject?.amc_id]);

  useEffect(() => {
    if (selectedObject) {
      setNotes(selectedObject.amc_notes || '');
    }
  }, [selectedObject]);

  const loadAllDetails = async () => {
    if (!selectedObject || !selectedObject.amc_id) return;

    setLoading({ summary: true, relationships: true, xml: true });

    try {
      // Get component details including summary and dependencies
      const detailsResponse = await fetch(`${API_BASE_URL}/metadata-component/${selectedObject.amc_id}/details`);
      const detailsData = await detailsResponse.json();
      
      // Get content/XML
      const contentResponse = await fetch(`${API_BASE_URL}/metadata-component/${selectedObject.amc_id}/content`);
      const contentData = await contentResponse.json();

      console.log('Details API response:', detailsData);
      console.log('Content API response:', contentData);

      let summary = 'Unable to load summary.';
      
      if (detailsData.success) {
        // Check if AI summary exists
        if (detailsData.ai_summary && detailsData.ai_summary.trim()) {
          // Use existing summary
          summary = detailsData.ai_summary;
          console.log('Using existing AI summary');
        } else {
          // Automatically generate summary if it doesn't exist
          console.log('No existing summary found, generating automatically...');
          try {
            const generateResponse = await fetch(`${API_BASE_URL}/metadata-component/${selectedObject.amc_id}/generate-summary`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              }
            });

            const generateData = await generateResponse.json();
            
            if (generateData.success) {
              summary = generateData.summary;
              console.log('AI summary generated automatically');
            } else {
              summary = 'Unable to generate AI summary automatically.';
              console.error('Failed to generate summary automatically:', generateData.error);
            }
          } catch (error) {
            console.error('Error generating summary automatically:', error);
            summary = 'Error generating AI summary automatically.';
          }
        }
      }

      setObjectDetails({
        summary: summary,
        relationships: detailsData.success ? detailsData.dependencies : [],
        xml: contentData.success ? contentData.content : 'Unable to load XML content.',
      });

    } catch (error) {
      console.error('Error loading object details:', error);
      setObjectDetails({
        summary: 'Error loading summary.',
        relationships: [],
        xml: 'Error loading XML content.',
      });
    } finally {
      setLoading({ summary: false, relationships: false, xml: false });
    }
  };

  const copyXmlToClipboard = () => {
    navigator.clipboard.writeText(objectDetails.xml);
  };

  const getObjectType = (object) => {
    if (!object) return 'Unknown';
    
    // Use the metadata_type_name from the database if available
    if (object.metadata_type_name) {
      return object.metadata_type_name;
    }
    
    // Fallback to filename-based detection
    const filename = object.amc_dev_name || object.amc_label || '';
    if (filename.endsWith('.cls')) return 'ApexClass';
    if (filename.endsWith('.trigger')) return 'ApexTrigger';
    if (filename.endsWith('.object')) return 'CustomObject';
    if (filename.endsWith('.flow')) return 'Flow';
    if (filename.endsWith('.layout')) return 'Layout';
    return 'Unknown';
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  };

  const handleOpenDiagram = () => {
    console.log('=== DIAGRAM BUTTON CLICKED ===');
    console.log('Selected object:', selectedObject);
    console.log('onOpenDiagram function available:', !!onOpenDiagram);
    console.log('Relationships data:', objectDetails.relationships);
    
    if (onOpenDiagram && selectedObject && selectedObject.amc_id) {
      console.log('Calling onOpenDiagram with component ID:', selectedObject.amc_id);
      
      // Fetch dependency network data
      fetch(`${API_BASE_URL}/metadata-component/${selectedObject.amc_id}/dependency-network`)
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            console.log('Dependency network data:', data);
            onOpenDiagram(selectedObject, data.network);
          } else {
            console.error('Failed to get dependency network:', data.error);
            alert('Failed to load dependency diagram data.');
          }
        })
        .catch(error => {
          console.error('Error fetching dependency network:', error);
          alert('Error loading dependency diagram data.');
        });
    } else {
      console.error('Cannot open diagram:', {
        hasFunction: !!onOpenDiagram,
        hasObject: !!selectedObject,
        hasComponentId: !!(selectedObject && selectedObject.amc_id)
      });
      alert('Diagram functionality not available. Check console for details.');
    }
  };

  const handleAddToList = () => {
    console.log('=== ADD TO LIST BUTTON CLICKED ===');
    console.log('Selected object:', selectedObject);
    console.log('Last used list ID:', lastUsedListId);
    console.log('Available lists:', lists);
    
    if (!selectedObject) {
      console.error('No object selected');
      return;
    }

    // If we have a last used list, add directly to it
    if (lastUsedListId && lists.length > 0) {
      const lastUsedList = lists.find(list => list.id === lastUsedListId);
      if (lastUsedList) {
        // Check if object already exists in the list
        const objectExists = lastUsedList.items.some(item => item.name === selectedObject.name);
        
        if (!objectExists) {
          // Add to the last used list directly
          if (onAddToList) {
            onAddToList([lastUsedListId], selectedObject, lastUsedList.title);
          }
          return;
        }
      }
    }

    // Fallback: show the list selection modal
    if (onShowListModal) {
      onShowListModal(selectedObject);
    } else if (onAddToList) {
      // Legacy fallback
      onAddToList(selectedObject);
    } else {
      console.error('No add to list functionality available');
      alert('Add to list functionality not available. Check console for details.');
    }
  };

  // Check if we should show the diagram button
  const shouldShowDiagramButton = () => {
    // Always show the button if we have onOpenDiagram function
    // The dependency page can handle cases with no relationships
    return !!onOpenDiagram;
  };

  const getDependencyCount = () => {
    if (!objectDetails.relationships) return 0;
    return Array.isArray(objectDetails.relationships) ? objectDetails.relationships.length : 0;
  };

  const getLastUsedListName = () => {
    if (!lastUsedListId || !lists.length) return null;
    const list = lists.find(l => l.aml_id === lastUsedListId);
    return list ? list.aml_name : null;
  };

  const handleEditNotes = () => {
    setIsEditingNotes(true);
  };

  const handleSaveNotes = async () => {
    if (!selectedObject || !selectedObject.amc_id) return;
    
    setSavingNotes(true);
    try {
      const response = await fetch(`${API_BASE_URL}/metadata-component/${selectedObject.amc_id}/update-notes`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          notes: notes,
          user_id: 243 // Default user ID
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setIsEditingNotes(false);
        // Update the selectedObject with new notes
        if (data.component) {
          selectedObject.amc_notes = data.component.amc_notes;
        }
      } else {
        console.error('Failed to save notes:', data.error);
        alert('Failed to save notes. Please try again.');
      }
    } catch (error) {
      console.error('Error saving notes:', error);
      alert('Error saving notes. Please try again.');
    } finally {
      setSavingNotes(false);
    }
  };

  const handleCancelEditNotes = () => {
    setNotes(selectedObject.amc_notes || '');
    setIsEditingNotes(false);
  };

  const handleDependencyClick = async (dependencyName) => {
    if (!dependencyName || !onNavigateToDependency) return;
    
    try {
      // Search for the dependency component by name
      const response = await fetch(`${API_BASE_URL}/search-metadata?org_id=409&search_term=${encodeURIComponent(dependencyName)}`);
      const data = await response.json();
      
      if (data.success && data.components && data.components.length > 0) {
        // Find exact match by dev_name
        const exactMatch = data.components.find(comp => 
          comp.amc_dev_name === dependencyName || 
          comp.amc_label === dependencyName
        );
        
        const targetComponent = exactMatch || data.components[0];
        
        // Navigate to the dependency's details in the same tab
        onNavigateToDependency(targetComponent);
      } else {
        console.warn('Dependency component not found:', dependencyName);
        alert(`Could not find component: ${dependencyName}`);
      }
    } catch (error) {
      console.error('Error searching for dependency:', error);
      alert('Error finding dependency component');
    }
  };

  if (!selectedObject) {
    return (
      <div className="metadata-object-view empty">
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h3>Metadata Details</h3>
          <p>Select an item from the list to see its details.</p>
        </div>
      </div>
    );
  }

  const lastUsedListName = getLastUsedListName();

  return (
    <div className="metadata-object-view-enhanced">
      <div className="object-header">
        <h3 className="object-title">{selectedObject.name}</h3>
        <button 
          className="add-to-list-btn-enhanced"
          onClick={handleAddToList}
          title={lastUsedListName ? `Add to ${lastUsedListName}` : "Add to list"}
        >
          <span className="list-icon">⊕</span>
          {lastUsedListName ? `Add to ${lastUsedListName}` : 'Add to List'}
        </button>
      </div>

      <div className="object-sections">
        {/* Description Section */}
        <div className="section description-section">
          <div className="section-header">
            <h4 className="section-title">Description</h4>
          </div>
          <div className="section-content">
            {loading.summary ? (
              <p className="loading-text">Loading description and checking for AI summary...</p>
            ) : (
              <p className="description-text">
                {objectDetails.summary}
              </p>
            )}
          </div>
        </div>

        {/* Metadata Info Section */}
        <div className="section metadata-info-section">
          <h4 className="section-title">Metadata Info</h4>
          <div className="section-content">
            <div className="info-grid-enhanced">
              <div className="info-row">
                <span className="info-label">Name</span>
                <span className="info-value">{selectedObject.amc_dev_name || selectedObject.amc_label || 'Unknown'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Type</span>
                <span className="info-value">{getObjectType(selectedObject)}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Created</span>
                <span className="info-value">{formatDate(selectedObject.amc_created_timestamp)}</span>
              </div>
              {selectedObject.amc_last_modified && (
                <div className="info-row">
                  <span className="info-label">Modified</span>
                  <span className="info-value">{formatDate(selectedObject.amc_last_modified)}</span>
                </div>
              )}
              <div className="info-row">
                <span className="info-label">Notes</span>
                <div className="info-value notes-section">
                  {isEditingNotes ? (
                    <div className="notes-editor">
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Enter your notes here..."
                        className="notes-textarea"
                        rows={3}
                      />
                      <div className="notes-actions">
                        <button 
                          onClick={handleSaveNotes} 
                          disabled={savingNotes}
                          className="save-notes-btn"
                        >
                          {savingNotes ? 'Saving...' : 'Save'}
                        </button>
                        <button 
                          onClick={handleCancelEditNotes}
                          className="cancel-notes-btn"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="notes-display">
                      <span className="notes-text">
                        {selectedObject.amc_notes || 'No notes added yet.'}
                      </span>
                      <button 
                        onClick={handleEditNotes}
                        className="edit-notes-btn"
                        title="Edit notes"
                      >
                        ✏️
                      </button>
                    </div>
                  )}
                </div>
              </div>
              <div className="info-row">
                <span className="info-label">Dependencies</span>
                <span className="info-value dependencies-link">
                  {getDependencyCount()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Dependency Diagram Section */}
        <div className="section dependency-section">
          <h4 className="section-title">Dependencies</h4>
          <div className="section-content">
            {loading.relationships ? (
              <p className="loading-text">Loading dependencies...</p>
            ) : (
              <div className="dependencies-list">
                {objectDetails.relationships && objectDetails.relationships.length > 0 ? (
                  <div className="dependencies-grid-clean">
                    {objectDetails.relationships.map((dep, index) => {
                      const currentComponentName = selectedObject.amc_dev_name || selectedObject.amc_label || selectedObject.name;
                      const fromName = dep.from_dev_name || '';
                      const toName = dep.to_dev_name || '';
                      
                      // Determine which component is the dependency (the other one, not current)
                      let dependencyName = '';
                      let isClickable = false;
                      
                      if (fromName === currentComponentName && toName !== currentComponentName) {
                        // Current component is 'from', so dependency is 'to'
                        dependencyName = toName;
                        isClickable = true;
                      } else if (toName === currentComponentName && fromName !== currentComponentName) {
                        // Current component is 'to', so dependency is 'from'
                        dependencyName = fromName;
                        isClickable = true;
                      } else if (fromName !== currentComponentName) {
                        // Neither matches current, default to 'from'
                        dependencyName = fromName;
                        isClickable = true;
                      } else if (toName !== currentComponentName) {
                        // Neither matches current, use 'to'
                        dependencyName = toName;
                        isClickable = true;
                      } else {
                        // Fallback to whatever is available
                        dependencyName = fromName || toName || 'Unknown';
                        isClickable = dependencyName !== currentComponentName;
                      }
                      
                      return (
                        <div key={index} className="dependency-item-clean">
                          <div className="dependency-main-info">
                            <span className="dependency-icon">
                              {dep.amd_dependency_type?.includes('flow') ? '🔀' : 
                               dep.amd_dependency_type?.includes('object') ? '📦' : 
                               dep.amd_dependency_type?.includes('class') ? '⚡' : '🔗'}
                            </span>
                            {isClickable ? (
                              <span 
                                className="dependency-name-clean clickable-dependency"
                                onClick={() => handleDependencyClick(dependencyName)}
                                title={`Click to view ${dependencyName} details`}
                                style={{ 
                                  cursor: 'pointer', 
                                  color: '#2196F3', 
                                  textDecoration: 'underline',
                                  fontWeight: '500',
                                  fontSize: '0.95rem'
                                }}
                              >
                                {dependencyName}
                              </span>
                            ) : (
                              <span 
                                className="dependency-name-clean current-component"
                                style={{ 
                                  color: '#888',
                                  fontSize: '0.95rem'
                                }}
                              >
                                {dependencyName}
                              </span>
                            )}
                            <span 
                              className="dependency-type-clean"
                              style={{
                                color: '#666',
                                fontSize: '0.8rem',
                                textTransform: 'uppercase',
                                marginLeft: '8px'
                              }}
                            >
                              {dep.amd_dependency_type?.replace('_', ' ') || 'REFERENCE'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="no-dependencies">No dependencies found for this component.</p>
                )}
              </div>
            )}
            <div className="diagram-preview">
              <button 
                className="open-diagram-btn"
                onClick={handleOpenDiagram}
                disabled={!shouldShowDiagramButton()}
                title={shouldShowDiagramButton() ? 'Open dependency diagram' : 'Diagram not available'}
              >
                {loading.relationships ? 'Loading...' : 
                 shouldShowDiagramButton() ? 'Open Diagram' : 'Diagram Not Available'}
              </button>
            </div>
          </div>
        </div>

        {/* XML Section */}
        <div className="section xml-section">
          <div className="xml-header">
            <h4 className="section-title">XML</h4>
          </div>
          <div className="section-content">
            {loading.xml ? (
              <p className="loading-text">Loading XML...</p>
            ) : (
              <div className="xml-container">
                <pre className="xml-code-enhanced">
                  <code>{objectDetails.xml}</code>
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetadataObjectView;