import React from 'react';

const MyList = ({ lists, selectedList, onListSelect }) => {
  return (
    <div className="my-list">
      <div className="my-list-header">
        <h3>My List</h3>
        <span className="list-count">{lists.length}</span>
      </div>
      
      <div className="search-container">
        <input 
          type="text" 
          placeholder="Search for Metadata"
          className="search-input small"
        />
        <span className="search-icon">🔍</span>
      </div>

      <div className="lists-container">
        {lists.map((list, index) => (
          <div 
            key={index}
            className={`list-item ${selectedList === list.name ? 'active' : ''}`}
            onClick={() => onListSelect(list.name)}
          >
            <div className="list-content">
              <span className="list-name">{list.name}</span>
              <span className="list-count-badge">{list.count}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="list-actions">
        <button className="add-list-btn">
          <span className="plus-icon">+</span>
          Add To List
        </button>
      </div>
    </div>
  );
};

export default MyList;