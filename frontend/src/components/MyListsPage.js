import React, { useState, useEffect } from 'react';
import MetadataObjectView from './MetadataObjectView';
import ListDependencyPage from './ListDependencyPage';

const MyListsPage = ({ 
  lists, 
  onBack, 
  jobId, 
  onOpenDiagram, 
  onRemoveFromList,
  onDeleteList,
  onRenameList,
  onAddToList,
  onLoadListComponents
}) => {
  console.log('📋 MyListsPage received lists:', lists);
  
  const [selectedList, setSelectedList] = useState(lists[0] || null);
  const [selectedObject, setSelectedObject] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [listSearchTerm, setListSearchTerm] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [showRenameModal, setShowRenameModal] = useState(null);
  const [newListName, setNewListName] = useState('');
  const [showAddToListModal, setShowAddToListModal] = useState(false);
  const [objectToAdd, setObjectToAdd] = useState(null);
  const [listSummary, setListSummary] = useState('');
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [showDependencyView, setShowDependencyView] = useState(false);

  // Auto-generate summary when selectedList changes
  useEffect(() => {
    if (selectedList && selectedList.id && !showDependencyView) {
      generateListSummary(selectedList.id);
    }
  }, [selectedList, showDependencyView]);

  // Fix the toLowerCase error by adding null checks
  const filteredLists = lists.filter(list =>
    list && list.title && list.title.toLowerCase().includes(listSearchTerm.toLowerCase())
  );

  const filteredObjects = selectedList
    ? selectedList.items.filter(item =>
        item && (item.amc_dev_name || item.name) && (item.amc_dev_name || item.name).toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  const handleListSelect = async (list) => {
    setSelectedList(list);
    setSelectedObject(null);
    setSearchTerm('');
    setListSummary('');
    setIsGeneratingSummary(true);
    setShowDependencyView(false);
    
    // Load components for the selected list
    if (onLoadListComponents) {
      await onLoadListComponents(list.id);
    }
    
    // Generate list summary
    await generateListSummary(list.id);
  };

  const handleViewDependencies = () => {
    if (selectedList) {
      setShowDependencyView(true);
    }
  };

  const handleBackFromDependencies = () => {
    setShowDependencyView(false);
  };

  const generateListSummary = async (listId) => {
    try {
      console.log(`Generating summary for list ${listId}...`);
      
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api'}/mylists/${listId}/generate-summaries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('List summary generated successfully:', data);
        setListSummary(data.combined_summary);
      } else {
        console.error('Failed to generate list summary:', data.error);
        setListSummary('Failed to generate list summary.');
      }
    } catch (error) {
      console.error('Error generating list summary:', error);
      setListSummary('Error generating list summary.');
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const handleObjectSelect = (object) => {
    setSelectedObject(object);
  };

  const handleOpenDiagram = (object) => {
    if (onOpenDiagram) {
      onOpenDiagram(object);
    }
  };

  const handleDeleteList = (listId) => {
    if (onDeleteList) {
      onDeleteList(listId);
      // If we deleted the currently selected list, select another one
      if (selectedList && selectedList.id === listId) {
        const remainingLists = lists.filter(list => list.id !== listId);
        setSelectedList(remainingLists[0] || null);
        setSelectedObject(null);
      }
    }
    setShowDeleteConfirm(null);
  };

  const handleRenameList = () => {
    if (onRenameList && showRenameModal && newListName.trim()) {
      onRenameList(showRenameModal, newListName.trim());
      setShowRenameModal(null);
      setNewListName('');
    }
  };

  const handleAddToList = (object) => {
    setObjectToAdd(object);
    setShowAddToListModal(true);
  };

  const handleSaveToList = (listId) => {
    if (onAddToList && objectToAdd && listId) {
      onAddToList(listId, objectToAdd);
      setShowAddToListModal(false);
      setObjectToAdd(null);
    }
  };

  const getObjectIcon = (object) => {
    // Use the actual metadata type if available
    if (object.metadata_type_name) {
      const type = object.metadata_type_name.toLowerCase();
      if (type.includes('apexclass')) return '⚡';
      if (type.includes('apextrigger')) return '🔄';
      if (type.includes('customobject')) return '📦';
      if (type.includes('flow')) return '🔀';
      if (type.includes('layout')) return '📋';
    }
    
    // Fallback to filename-based logic
    const filename = object.amc_dev_name || object.name || '';
    if (filename.endsWith('.cls')) return '⚡';
    if (filename.endsWith('.trigger')) return '🔄';
    if (filename.endsWith('.object')) return '📦';
    if (filename.endsWith('.flow')) return '🔀';
    if (filename.endsWith('.layout')) return '📋';
    return '📄';
  };

  const getObjectType = (object) => {
    // Use the actual metadata type if available
    if (object.metadata_type_name) {
      return object.metadata_type_name;
    }
    
    // Fallback to filename-based logic
    const filename = object.amc_dev_name || object.name || '';
    if (filename.endsWith('.cls')) return 'Apex Class';
    if (filename.endsWith('.trigger')) return 'Apex Trigger';
    if (filename.endsWith('.object')) return 'Custom Object';
    if (filename.endsWith('.flow')) return 'Flow';
    if (filename.endsWith('.layout')) return 'Layout';
    return 'Unknown';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="metadata-explorer">
      {showDependencyView && selectedList ? (
        <ListDependencyPage
          selectedList={selectedList}
          onBack={handleBackFromDependencies}
          jobId={jobId}
        />
      ) : (
        <div className="explorer-layout">
          {/* Left Sidebar - My Lists */}
          <div className="explorer-sidebar">
            <div className="sidebar-header">
              <h3>My Lists</h3>
              <button className="collapse-btn" onClick={onBack} title="Back to Dashboard">
                ← Back
              </button>
            </div>
            
            <div className="sidebar-search">
              <input 
                type="text" 
                placeholder="Search lists"
                className="search-input"
                value={listSearchTerm}
                onChange={(e) => setListSearchTerm(e.target.value)}
              />
              <span className="search-icon">🔍</span>
            </div>
            
            <div className="types-list">
              {filteredLists.map((list) => (
                <div
                  key={list.id}
                  className={`type-item ${selectedList?.id === list.id ? 'active' : ''}`}
                  onClick={() => handleListSelect(list)}
                >
                  <div className="list-item-content">
                    <span className="type-name">{list.title}</span>
                    <span className="type-count">{list.items.length}</span>
                  </div>
                  <div className="list-item-actions">
                    <button
                      className="list-action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowRenameModal(list.id);
                        setNewListName(list.title);
                      }}
                      title="Rename list"
                    >
                      ✏️
                    </button>
                    <button
                      className="list-action-btn delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowDeleteConfirm(list.id);
                      }}
                      title="Delete list"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
              
              {filteredLists.length === 0 && (
                <div className="no-lists" style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
                  {listSearchTerm ? 'No lists match your search' : 'No lists created yet'}
                </div>
              )}
            </div>
          </div>

          {/* Main Content - Objects in Selected List */}
          <div className="explorer-main">
            <div className="main-header">
              <div className="header-content">
                <h2>{selectedList ? selectedList.title : 'Select a List'}</h2>
                {selectedList && (
                  <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
                    <div className="main-search">
                      <input 
                        type="text" 
                        placeholder="Search objects"
                        className="search-input"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                      <span className="search-icon">🔍</span>
                    </div>
                    <button 
                      className="view-dependencies-btn"
                      onClick={handleViewDependencies}
                      title="View Dependencies"
                      style={{
                        background: '#667eea',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '8px 15px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.9rem',
                        fontWeight: '500',
                        transition: 'all 0.2s ease',
                        whiteSpace: 'nowrap'
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#5a6fd8'}
                      onMouseLeave={(e) => e.target.style.background = '#667eea'}
                    >
                      🔗 View Dependencies
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            <div className="objects-content">
              {!selectedList ? (
                <div className="no-selection" style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '300px',
                  color: '#888'
                }}>
                  <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📋</div>
                  <h4 style={{ color: 'white', marginBottom: '8px' }}>Select a List</h4>
                  <p>Choose a list from the sidebar to view its metadata objects</p>
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
                    {selectedList.description && (
                      <span style={{ fontSize: '0.8rem', fontStyle: 'italic' }}>
                        {selectedList.description}
                      </span>
                    )}
                  </div>

                  {filteredObjects.length > 0 ? (
                    filteredObjects.map((object, index) => (
                      <div 
                        key={`${object.amc_dev_name || object.name}-${index}`}
                        className={`object-item ${selectedObject?.amc_dev_name === object.amc_dev_name ? 'active' : ''}`}
                        onClick={() => handleObjectSelect(object)}
                      >
                        <div className="object-main">
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                            <span style={{ fontSize: '1.5rem' }}>{getObjectIcon(object)}</span>
                            <h4 className="object-name">{object.amc_dev_name || object.name}</h4>
                          </div>
                          <div className="object-meta">
                            <span className="meta-item">
                              <strong>Type:</strong> {getObjectType(object)}
                            </span>
                            <span className="meta-item">
                              <strong>Added:</strong> {formatDate(object.addedToListAt)}
                            </span>
                            {object.amc_created_timestamp && (
                              <span className="meta-item">
                                <strong>Created:</strong> {new Date(object.amc_created_timestamp).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button 
                            className="add-to-list-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              onRemoveFromList && onRemoveFromList(selectedList.id, object.amc_dev_name || object.name);
                            }}
                            title="Remove from list"
                            style={{ color: '#e53e3e' }}
                          >
                            🗑️
                          </button>
                          <button 
                            className="add-to-list-btn" 
                            title="Add to another list"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleAddToList(object);
                            }}
                          >
                            ⊕
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="no-objects" style={{ 
                      textAlign: 'center', 
                      padding: '40px', 
                      color: '#888' 
                    }}>
                      {searchTerm 
                        ? `No objects match "${searchTerm}"` 
                        : `${selectedList.title} is empty`
                      }
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
                <h3>{selectedObject ? 'Object Details' : 'List Summary'}</h3>
                {selectedObject && selectedList && (
                  <div style={{ fontSize: '0.8rem', color: '#888' }}>
                    from {selectedList.title}
                  </div>
                )}
                {!selectedObject && selectedList && (
                  <div style={{ fontSize: '0.8rem', color: '#888' }}>
                    {selectedList.title}
                  </div>
                )}
              </div>
            </div>
            
            <div className="details-content" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {selectedList ? (
                <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {/* Always Show List Summary Section - Smaller and Separately Scrollable */}
                  <div className="static-list-summary" style={{ 
                    borderBottom: '1px solid #444',
                    padding: '15px',
                    background: '#1a1a1a',
                    flexShrink: 0,
                    height: '200px', // Fixed smaller height
                    overflowY: 'auto' // Make it separately scrollable
                  }}>
                    <h4 style={{ color: '#4CAF50', marginBottom: '15px', fontSize: '1rem' }}>
                      📋 List Summary
                    </h4>
                    
                    {isGeneratingSummary ? (
                      <div className="loading-summary">
                        <div className="loading-spinner"></div>
                        <p>Generating list summary...</p>
                      </div>
                    ) : listSummary ? (
                      <div className="summary-content">
                        <div 
                          className="markdown-content"
                          style={{
                            color: '#e0e0e0',
                            lineHeight: '1.4',
                            fontSize: '0.85rem'
                          }}
                          dangerouslySetInnerHTML={{
                            __html: listSummary
                              .replace(/\n/g, '<br>')
                              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                              .replace(/#{1,6}\s+(.*?)(?=\n|$)/g, '<h3 style="color: #4CAF50; margin: 15px 0 8px 0; font-size: 0.9rem;">$1</h3>')
                              .replace(/###\s+(.*?)(?=\n|$)/g, '<h4 style="color: #2196F3; margin: 12px 0 6px 0; font-size: 0.85rem;">$1</h4>')
                          }}
                        />
                      </div>
                    ) : (
                      <div className="no-summary">
                        <div className="no-summary-icon">📋</div>
                        <h4>No Summary Available</h4>
                        <p>Generating list summary...</p>
                      </div>
                    )}
                  </div>

                  {/* Object Details Section - Shows when object is selected, otherwise shows AI summaries */}
                  <div className="object-details-section" style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '15px',
                    borderTop: '1px solid #444'
                  }}>
            {selectedObject ? (
                      <div>
                        <h4 style={{ color: '#2196F3', marginBottom: '15px', fontSize: '1rem' }}>
                          🤖 {selectedObject.amc_dev_name || selectedObject.name} Details
                        </h4>
              <MetadataObjectView
                selectedObject={selectedObject}
                jobId={jobId}
                onOpenDiagram={handleOpenDiagram}
              />
                      </div>
                    ) : (
                      <div style={{ 
                        textAlign: 'center', 
                        padding: '40px', 
                        color: '#888' 
                      }}>
                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📄</div>
                        <h4 style={{ color: 'white', marginBottom: '8px' }}>Select an Object</h4>
                        <p>Click on any object from the list to view its details</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="no-selection">
                  <div className="no-selection-icon">📄</div>
                  <h4>Select a list</h4>
                  <p>Choose a list from the sidebar to view its summary and objects</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '400px' }}>
            <div className="modal-header">
              <h2>Delete List</h2>
              <button className="close-btn" onClick={() => setShowDeleteConfirm(null)}>×</button>
            </div>
            
            <div style={{ padding: '20px' }}>
              <p style={{ color: '#ccc', marginBottom: '20px' }}>
                Are you sure you want to delete "{lists.find(l => l.id === showDeleteConfirm)?.title}"? 
                This action cannot be undone.
              </p>
              
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button 
                  className="cancel-button"
                  onClick={() => setShowDeleteConfirm(null)}
                  style={{
                    background: 'transparent',
                    color: '#ccc',
                    border: '1px solid #555',
                    borderRadius: '6px',
                    padding: '10px 20px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button 
                  className="delete-button"
                  onClick={() => handleDeleteList(showDeleteConfirm)}
                  style={{
                    background: '#e53e3e',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '10px 20px',
                    cursor: 'pointer'
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rename Modal */}
      {showRenameModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '400px' }}>
            <div className="modal-header">
              <h2>Rename List</h2>
              <button className="close-btn" onClick={() => {
                setShowRenameModal(null);
                setNewListName('');
              }}>×</button>
            </div>
            
            <div style={{ padding: '20px' }}>
              <div className="form-group">
                <label style={{ color: '#ccc', marginBottom: '8px', display: 'block' }}>
                  List Name
                </label>
                <input
                  type="text"
                  value={newListName}
                  onChange={(e) => setNewListName(e.target.value)}
                  placeholder="Enter new name"
                  style={{
                    width: '100%',
                    background: '#1a1a1a',
                    border: '1px solid #444',
                    borderRadius: '6px',
                    padding: '10px',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}
                  autoFocus
                />
              </div>
              
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button 
                  className="cancel-button"
                  onClick={() => {
                    setShowRenameModal(null);
                    setNewListName('');
                  }}
                  style={{
                    background: 'transparent',
                    color: '#ccc',
                    border: '1px solid #555',
                    borderRadius: '6px',
                    padding: '10px 20px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button 
                  className="save-button"
                  onClick={handleRenameList}
                  disabled={!newListName.trim()}
                  style={{
                    background: newListName.trim() ? '#667eea' : '#444',
                    color: newListName.trim() ? 'white' : '#888',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '10px 20px',
                    cursor: newListName.trim() ? 'pointer' : 'not-allowed'
                  }}
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add to List Modal */}
      {showAddToListModal && objectToAdd && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h2>Add to List</h2>
              <button className="close-btn" onClick={() => {
                setShowAddToListModal(false);
                setObjectToAdd(null);
              }}>×</button>
            </div>
            
            <div style={{ padding: '20px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ color: 'white', marginBottom: '10px' }}>
                  Add "{objectToAdd.name}" to a list:
                </h4>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '10px',
                  padding: '10px',
                  background: '#2a2a2a',
                  borderRadius: '6px',
                  border: '1px solid #444'
                }}>
                  <span style={{ fontSize: '1.5rem' }}>{getObjectIcon(objectToAdd)}</span>
                  <div>
                    <div style={{ color: 'white', fontWeight: 'bold' }}>{objectToAdd.name}</div>
                    <div style={{ color: '#888', fontSize: '0.9rem' }}>{getObjectType(objectToAdd)}</div>
                  </div>
                </div>
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ color: 'white', marginBottom: '10px' }}>Select a list:</h4>
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {lists.filter(list => list.id !== selectedList?.id).map((list) => (
                    <div
                      key={list.id}
                      style={{
                        padding: '12px',
                        border: '1px solid #444',
                        borderRadius: '6px',
                        marginBottom: '8px',
                        cursor: 'pointer',
                        background: '#2a2a2a',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#3a3a3a'}
                      onMouseLeave={(e) => e.target.style.background = '#2a2a2a'}
                      onClick={() => handleSaveToList(list.id)}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ color: 'white', fontWeight: 'bold' }}>{list.title}</div>
                          <div style={{ color: '#888', fontSize: '0.9rem' }}>
                            {list.items.length} items
                          </div>
                        </div>
                        <button
                          style={{
                            background: '#667eea',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '6px 12px',
                            cursor: 'pointer',
                            fontSize: '0.8rem'
                          }}
                        >
                          Add
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button 
                  className="cancel-button"
                  onClick={() => {
                    setShowAddToListModal(false);
                    setObjectToAdd(null);
                  }}
                  style={{
                    background: 'transparent',
                    color: '#ccc',
                    border: '1px solid #555',
                    borderRadius: '6px',
                    padding: '10px 20px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyListsPage;