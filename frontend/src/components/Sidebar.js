import React from 'react';

const Sidebar = ({ currentScreen }) => {
  const sidebarItems = [
    { icon: '🏠', label: 'Home', id: 'home' },
    { icon: '📝', label: 'Inbox', id: 'inbox' },
    { icon: '💼', label: 'AI Chat', id: 'chat' },
    { icon: '⭐', label: 'AI Chat', id: 'ai' },
    { icon: '📊', label: 'Whiteboards', id: 'whiteboards' },
    { icon: '📈', label: 'Goals', id: 'goals' },
    { icon: '👥', label: 'Members', id: 'members' },
    { icon: '⚙️', label: 'Settings', id: 'settings' },
    { icon: '🔐', label: 'Knowledge Management', id: 'knowledge' },
    { icon: '📧', label: 'Email', id: 'email' },
    { icon: '📅', label: 'Calendar', id: 'calendar' },
    { icon: '📋', label: 'Template Library', id: 'templates' }
  ];

  const platforms = [
    { icon: '☁️', label: 'Salesforce', id: 'salesforce', active: true },
    { icon: '💼', label: 'SAP', id: 'sap' },
    { icon: '🔧', label: 'ServiceNow', id: 'servicenow' }
  ];

  const planningTools = [
    { icon: '📝', label: 'Asana', id: 'asana' },
    { icon: '📊', label: 'Jira', id: 'jira' },
    { icon: '📋', label: 'Trello', id: 'trello' }
  ];

  const drawingTools = [
    { icon: '✏️', label: 'Draw.io', id: 'drawio' },
    { icon: '📈', label: 'Lucid Charts', id: 'lucidcharts' }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">✕</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          {sidebarItems.map((item) => (
            <div 
              key={item.id} 
              className={`nav-item ${item.id === 'settings' ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </div>
          ))}
        </div>

        <div className="nav-section">
          <div className="section-header">
            <span className="section-icon">▼</span>
            <span className="section-title">Integrations</span>
          </div>
          
          <div className="subsection">
            <div className="subsection-header">
              <span className="subsection-icon">▼</span>
              <span className="subsection-title">Platforms</span>
            </div>
            {platforms.map((platform) => (
              <div 
                key={platform.id} 
                className={`nav-item subsection-item ${platform.active ? 'active' : ''}`}
              >
                <span className="nav-icon">{platform.icon}</span>
                <span className="nav-label">{platform.label}</span>
              </div>
            ))}
          </div>

          <div className="subsection">
            <div className="subsection-header">
              <span className="subsection-icon">▼</span>
              <span className="subsection-title">Planning Tools</span>
            </div>
            {planningTools.map((tool) => (
              <div key={tool.id} className="nav-item subsection-item">
                <span className="nav-icon">{tool.icon}</span>
                <span className="nav-label">{tool.label}</span>
              </div>
            ))}
          </div>

          <div className="subsection">
            <div className="subsection-header">
              <span className="subsection-icon">▼</span>
              <span className="subsection-title">Drawing Tools</span>
            </div>
            {drawingTools.map((tool) => (
              <div key={tool.id} className="nav-item subsection-item">
                <span className="nav-icon">{tool.icon}</span>
                <span className="nav-label">{tool.label}</span>
              </div>
            ))}
          </div>
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-avatar">
            <span>AI</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;