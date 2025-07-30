import React, { useState } from 'react';

const ListSelectionModal = ({ 
  isOpen, 
  onClose, 
  onSave, 
  availableLists, 
  selectedObject,
  onCreateNewList 
}) => {
  const [selectedLists, setSelectedLists] = useState(new Set());
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newListName, setNewListName] = useState('');

  if (!isOpen) return null;

  const handleListToggle = (listId) => {
    const newSelected = new Set(selectedLists);
    if (newSelected.has(listId)) {
      newSelected.delete(listId);
    } else {
      newSelected.add(listId);
    }
    setSelectedLists(newSelected);
  };

  const handleSave = () => {
    if (selectedLists.size > 0) {
      onSave(Array.from(selectedLists), selectedObject);
      onClose();
      setSelectedLists(new Set());
    }
  };

  const handleCreateNew = () => {
    setShowCreateForm(true);
  };

  const handleCreateSubmit = (e) => {
    e.preventDefault();
    if (newListName.trim()) {
      const newListId = onCreateNewList(newListName.trim());
      setSelectedLists(new Set([newListId]));
      setShowCreateForm(false);
      setNewListName('');
    }
  };

  const handleCancel = () => {
    setSelectedLists(new Set());
    setShowCreateForm(false);
    setNewListName('');
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '400px' }}>
        <div className="modal-header">
          <h2>Select Lists to add to</h2>
          <button className="close-btn" onClick={handleCancel}>×</button>
        </div>
        
        <div className="list-selection-content" style={{ padding: '20px' }}>
          {/* Create New List Button */}
          {!showCreateForm && (
            <button 
              className="create-new-list-btn"
              onClick={handleCreateNew}
              style={{
                width: '100%',
                background: 'none',
                border: '2px dashed #667eea',
                borderRadius: '8px',
                padding: '12px',
                color: '#667eea',
                fontSize: '0.9rem',
                cursor: 'pointer',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s'
              }}
            >
              <span style={{ fontSize: '1.2rem' }}>+</span>
              Create New List
            </button>
          )}

          {/* Create New List Form */}
          {showCreateForm && (
            <form onSubmit={handleCreateSubmit} style={{ marginBottom: '20px' }}>
              <div className="form-group">
                <input
                  type="text"
                  value={newListName}
                  onChange={(e) => setNewListName(e.target.value)}
                  placeholder="Enter list name"
                  style={{
                    width: '100%',
                    background: '#1a1a1a',
                    border: '1px solid #444',
                    borderRadius: '6px',
                    padding: '10px',
                    color: 'white',
                    fontSize: '0.9rem',
                    marginBottom: '10px'
                  }}
                  autoFocus
                />
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    type="submit" 
                    className="primary-button"
                    style={{ 
                      background: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '6px 12px',
                      fontSize: '0.8rem',
                      cursor: 'pointer'
                    }}
                  >
                    Create
                  </button>
                  <button 
                    type="button" 
                    onClick={() => {
                      setShowCreateForm(false);
                      setNewListName('');
                    }}
                    style={{ 
                      background: 'transparent',
                      color: '#ccc',
                      border: '1px solid #444',
                      borderRadius: '4px',
                      padding: '6px 12px',
                      fontSize: '0.8rem',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          )}

          {/* Lists Selection */}
          <div className="lists-selection">
            {availableLists.map((list) => (
              <div 
                key={list.id} 
                className="list-selection-item"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px',
                  border: `1px solid ${selectedLists.has(list.id) ? '#667eea' : '#444'}`,
                  borderRadius: '8px',
                  marginBottom: '8px',
                  cursor: 'pointer',
                  background: selectedLists.has(list.id) ? 'rgba(102, 126, 234, 0.1)' : '#2a2a2a',
                  transition: 'all 0.2s'
                }}
                onClick={() => handleListToggle(list.id)}
              >
                <div 
                  className="checkbox-custom"
                  style={{
                    width: '18px',
                    height: '18px',
                    border: `2px solid ${selectedLists.has(list.id) ? '#667eea' : '#666'}`,
                    borderRadius: '4px',
                    background: selectedLists.has(list.id) ? '#667eea' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px',
                    color: 'white'
                  }}
                >
                  {selectedLists.has(list.id) && '✓'}
                </div>
                <div className="list-info" style={{ flex: 1 }}>
                  <div style={{ color: 'white', fontSize: '0.9rem', fontWeight: '500' }}>
                    {list.title}
                  </div>
                  {list.count > 0 && (
                    <div style={{ color: '#888', fontSize: '0.8rem' }}>
                      {list.count} items
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Object Info */}
          {selectedObject && (
            <div 
              className="selected-object-info"
              style={{
                marginTop: '20px',
                padding: '12px',
                background: '#333',
                borderRadius: '6px',
                borderLeft: '3px solid #667eea'
              }}
            >
              <div style={{ color: '#888', fontSize: '0.8rem', marginBottom: '4px' }}>
                Adding to lists:
              </div>
              <div style={{ color: 'white', fontSize: '0.9rem', fontWeight: '500' }}>
                {selectedObject.name}
              </div>
            </div>
          )}
        </div>

        {/* Modal Actions */}
        <div className="modal-actions" style={{ padding: '0 20px 20px 20px' }}>
          <button 
            className="cancel-button" 
            onClick={handleCancel}
            style={{
              background: 'transparent',
              color: '#ccc',
              border: '1px solid #555',
              borderRadius: '6px',
              padding: '10px 20px',
              fontSize: '0.9rem',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            Cancel
          </button>
          <button 
            className="save-button"
            onClick={handleSave}
            disabled={selectedLists.size === 0}
            style={{
              background: selectedLists.size > 0 ? '#667eea' : '#444',
              color: selectedLists.size > 0 ? 'white' : '#888',
              border: 'none',
              borderRadius: '6px',
              padding: '10px 20px',
              fontSize: '0.9rem',
              cursor: selectedLists.size > 0 ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span>💾</span>
            Save ({selectedLists.size})
          </button>
        </div>
      </div>
    </div>
  );
};

export default ListSelectionModal;