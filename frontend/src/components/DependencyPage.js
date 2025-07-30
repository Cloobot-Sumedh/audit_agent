import React, { useState, useEffect } from 'react';
import '../zoom-controls.css';

const API_BASE_URL = 'http://localhost:5000/api';

const DependencyPage = ({ selectedObject, jobId, onBack, onNavigateToDependency }) => {
  console.log('=== DEPENDENCY PAGE RENDERED ===');
  console.log('selectedObject:', selectedObject);
  console.log('selectedObject type:', typeof selectedObject);
  console.log('selectedObject.name:', selectedObject?.name);
  console.log('selectedObject.amc_id:', selectedObject?.amc_id);
  
  const [objectDetails, setObjectDetails] = useState({
    summary: '',
    relationships: null,
    xml: '',
  });
  const [rightPanelObject, setRightPanelObject] = useState(null);
  const [rightPanelDetails, setRightPanelDetails] = useState({
    summary: '',
    relationships: null,
    xml: '',
  });
  const [loading, setLoading] = useState({
    summary: false,
    relationships: false,
    xml: false,
  });
  const [rightPanelLoading, setRightPanelLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('diagram');

  useEffect(() => {
    if (selectedObject && jobId) {
      loadObjectDetails();
      setRightPanelObject(selectedObject);
    }
  }, [selectedObject, jobId]);

  useEffect(() => {
    if (rightPanelObject && jobId) {
      loadRightPanelDetails();
    }
  }, [rightPanelObject, jobId]);

  const loadObjectDetails = async () => {
    const objectId = selectedObject.amc_id || selectedObject.id;
    
    if (!selectedObject || !objectId) {
      console.error('Cannot load object details: missing selectedObject or amc_id', selectedObject);
      return;
    }

    setLoading({ summary: true, relationships: true, xml: true });

    try {
      // First, get component details to check for existing summary
      const detailsResponse = await fetch(`${API_BASE_URL}/metadata-component/${objectId}/details`);
      const detailsData = await detailsResponse.json();
      
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
            const generateResponse = await fetch(`${API_BASE_URL}/metadata-component/${objectId}/generate-summary`, {
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

      // Get other details
      const [relationshipsRes, xmlRes] = await Promise.all([
        fetch(`${API_BASE_URL}/metadata-component/${objectId}/dependency-network`),
        fetch(`${API_BASE_URL}/metadata-component/${objectId}/content`),
      ]);

      const relationshipsData = await relationshipsRes.json();
      const xmlData = await xmlRes.json();

      setObjectDetails({
        summary: summary,
        relationships: relationshipsData.success ? relationshipsData : null,
        xml: xmlData.success ? xmlData.content : 'Unable to load XML content.',
      });

    } catch (error) {
      console.error('Error loading object details:', error);
      setObjectDetails({
        summary: 'Error loading summary.',
        relationships: null,
        xml: 'Error loading XML content.',
      });
    } finally {
      setLoading({ summary: false, relationships: false, xml: false });
    }
  };

  const loadRightPanelDetails = async () => {
    const objectId = rightPanelObject.amc_id || rightPanelObject.id;
    
    if (!rightPanelObject || !objectId) {
      console.error('Cannot load right panel details: missing rightPanelObject or amc_id', rightPanelObject);
      return;
    }

    setRightPanelLoading(true);

    try {
      console.log('=== LOADING RIGHT PANEL DETAILS ===');
      console.log('Object:', rightPanelObject);
      console.log('Component ID:', objectId);
      
      // First, get component details to check for existing summary
      const detailsResponse = await fetch(`${API_BASE_URL}/metadata-component/${objectId}/details`);
      const detailsData = await detailsResponse.json();
      
      let summary = `Unable to load summary for "${rightPanelObject.name}".`;
      
      if (detailsData.success) {
        // Check if AI summary exists
        if (detailsData.ai_summary && detailsData.ai_summary.trim()) {
          // Use existing summary
          summary = detailsData.ai_summary;
          console.log('Using existing AI summary for right panel');
        } else {
          // Automatically generate summary if it doesn't exist
          console.log('No existing summary found for right panel, generating automatically...');
          try {
            const generateResponse = await fetch(`${API_BASE_URL}/metadata-component/${objectId}/generate-summary`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              }
            });

            const generateData = await generateResponse.json();
            
            if (generateData.success) {
              summary = generateData.summary;
              console.log('AI summary generated automatically for right panel');
            } else {
              summary = `Unable to generate AI summary for "${rightPanelObject.name}".`;
              console.error('Failed to generate summary automatically for right panel:', generateData.error);
            }
          } catch (error) {
            console.error('Error generating summary automatically for right panel:', error);
            summary = `Error generating AI summary for "${rightPanelObject.name}".`;
          }
        }
      }
      
      // Get other details
      const [relationshipsRes, xmlRes] = await Promise.all([
        fetch(`${API_BASE_URL}/metadata-component/${objectId}/dependency-network`),
        fetch(`${API_BASE_URL}/metadata-component/${objectId}/content`),
      ]);

      console.log(`API responses for component ${objectId}:`, {
        details: detailsResponse.status,
        relationships: relationshipsRes.status,
        xml: xmlRes.status
      });

      const relationshipsData = await relationshipsRes.json();
      const xmlData = await xmlRes.json();

      console.log('Data received:', {
        detailsSuccess: detailsData.success,
        relationshipsSuccess: relationshipsData.success,
        xmlSuccess: xmlData.success
      });

      setRightPanelDetails({
        summary: summary,
        relationships: relationshipsData?.success ? relationshipsData : null,
        xml: xmlData?.success ? xmlData.content : `Unable to load XML content for "${rightPanelObject.name}".`,
      });

    } catch (error) {
      console.error('Error loading right panel details:', error);
      setRightPanelDetails({
        summary: `Error loading summary for "${rightPanelObject.name}".`,
        relationships: null,
        xml: `Error loading XML content for "${rightPanelObject.name}".`,
      });
    } finally {
      setRightPanelLoading(false);
    }
  };

  const handleNodeClick = async (nodeName) => {
    console.log('=== NODE CLICKED ===');
    console.log('Raw node name:', nodeName);
    
    // Clean up the node name for better matching
    let cleanNodeName = nodeName;
    
    // Remove layout suffixes and clean up
    cleanNodeName = cleanNodeName.replace(/-.*Layout.*$/, ''); // Remove layout parts
    cleanNodeName = cleanNodeName.replace(/\s+Layout$/, ''); // Remove " Layout"
    cleanNodeName = cleanNodeName.trim();
    
    console.log('Cleaned node name:', cleanNodeName);
    
    // Find the actual node data from the relationships to get the correct type
    let nodeType = 'Unknown';
    let nodeData = null;
    let componentId = null;
    
    if (objectDetails.relationships && objectDetails.relationships.network) {
      const foundNode = objectDetails.relationships.network.nodes.find(n => 
        n.id === nodeName || n.id === cleanNodeName || n.label === nodeName
      );
      if (foundNode) {
        nodeType = foundNode.type || 'Unknown';
        nodeData = foundNode;
        componentId = foundNode.component_id; // Get the component ID from the node data
        console.log('Found node data from network:', nodeData);
      }
    }
    
    // If we couldn't find it in the network, try to infer from the name
    if (nodeType === 'Unknown') {
      nodeType = inferObjectTypeFromName(cleanNodeName);
      console.log('Inferred node type from name:', nodeType);
    }
    
    // If we don't have a component ID from the network, try to find it by searching
    if (!componentId) {
      try {
        // Search for the component by name
        const searchResponse = await fetch(`${API_BASE_URL}/search-metadata?search_term=${encodeURIComponent(cleanNodeName)}&org_id=409`);
        if (searchResponse.ok) {
          const searchData = await searchResponse.json();
          if (searchData.success && searchData.components && searchData.components.length > 0) {
            // Find the best match
            const bestMatch = searchData.components.find(comp => 
              comp.amc_dev_name === cleanNodeName || 
              comp.amc_dev_name.toLowerCase() === cleanNodeName.toLowerCase()
            );
            if (bestMatch) {
              componentId = bestMatch.amc_id;
              nodeData = bestMatch;
              console.log('Found component in database:', nodeData);
            }
          }
        }
      } catch (error) {
        console.error('Error searching for component:', error);
      }
    }
    
    // Create a proper object for the clicked node
    const nodeObject = {
      name: cleanNodeName,
      originalName: nodeName,
      lastModified: new Date().toISOString(),
      type: nodeType,
      amc_id: componentId, // This is crucial for the new database endpoints
      amc_dev_name: cleanNodeName, // Add the database property name
      ...nodeData // Include any additional data from the database
    };
    
    console.log('Created node object:', nodeObject);
    setRightPanelObject(nodeObject);
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

  const inferObjectTypeFromName = (name) => {
    // Try to infer type from common naming patterns
    if (name.endsWith('Layout') || name.includes('Layout')) return 'Layout';
    if (name.endsWith('_mdt') || name.endsWith('__mdt')) return 'CustomObject';
    if (name.endsWith('_c') || name.endsWith('__c')) return 'CustomObject';
    if (name.includes('Trigger')) return 'ApexTrigger';
    if (name.includes('Flow')) return 'Flow';
    
    // Default fallback
    return 'CustomObject';
  };

  const getObjectType = (filename) => {
    if (!filename) return 'Custom Object'; // Handle undefined/null filename
    
    if (filename.endsWith('.cls')) return 'Apex Class';
    if (filename.endsWith('.trigger')) return 'Apex Trigger';
    if (filename.endsWith('.object')) return 'Custom Object';
    if (filename.endsWith('.flow')) return 'Flow';
    if (filename.endsWith('.layout')) return 'Layout';
    return 'Custom Object'; // Default
  };

  const getObjectTypeFromNodeType = (nodeType) => {
    const typeMapping = {
      'ApexClass': 'Apex Class',
      'ApexTrigger': 'Apex Trigger',
      'CustomObject': 'Custom Object',
      'Flow': 'Flow',
      'Layout': 'Layout'
    };
    return typeMapping[nodeType] || 'Custom Object';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  };

  const copyXmlToClipboard = () => {
    navigator.clipboard.writeText(rightPanelDetails.xml);
  };

  const DependencyDiagram = ({ relationships, onNodeClick, selectedNodeName }) => {
    const [zoomLevel, setZoomLevel] = useState(1);
    const [panX, setPanX] = useState(0);
    const [panY, setPanY] = useState(0);
    
    if (!relationships || !relationships.network || relationships.network.nodes.length === 0) {
      return (
        <div className="dependency-diagram-empty">
          <div className="empty-diagram">
            <div className="empty-icon">🔗</div>
            <h3>No Dependencies Found</h3>
            <p>This metadata component has no dependencies</p>
          </div>
        </div>
      );
    }

    const { network, stats } = relationships;
    
    // Create positioning for nodes - improved layout from the reference project
    const createDiagramLayout = () => {
      const centerX = 400;
      const centerY = 200;
      const radius = 120;
      
      const targetNode = network.nodes.find(n => n.isTarget) || network.nodes[0];
      const otherNodes = network.nodes.filter(n => !n.isTarget);
      
      const positionedNodes = [
        { ...targetNode, x: centerX, y: centerY, level: 'target' }
      ];
      
      // Position other nodes in a circle
      otherNodes.forEach((node, index) => {
        const angle = (2 * Math.PI * index) / otherNodes.length;
        positionedNodes.push({
          ...node,
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
          level: 'connected'
        });
      });

      return positionedNodes;
    };

    const getNodeColor = (nodeType, level, isSelected = false) => {
      if (isSelected) return '#a855f7'; // Purple for selected node
      if (level === 'target') return '#0ea5e9'; // Blue for target
      
      // Use the same color scheme as the reference project
      const colors = {
        'ApexClass': '#667eea',
        'ApexTrigger': '#48bb78',
        'CustomObject': '#ed8936',
        'Flow': '#9f7aea',
        'Layout': '#38b2ac'
      };
      return colors[nodeType] || '#f97316'; // Orange for unknown types
    };

    const getNodeIcon = (nodeType) => {
      const icons = {
        'ApexClass': '⚡',
        'ApexTrigger': '🔄',
        'CustomObject': '📦',
        'Flow': '🔀',
        'Layout': '📋'
      };
      return icons[nodeType] || '📄';
    };

    const handleZoomIn = () => {
      setZoomLevel(prev => Math.min(prev + 0.2, 3)); // Max zoom 3x
    };

    const handleZoomOut = () => {
      setZoomLevel(prev => Math.max(prev - 0.2, 0.5)); // Min zoom 0.5x
    };

    const handleResetZoom = () => {
      setZoomLevel(1);
      setPanX(0);
      setPanY(0);
    };

    const handlePan = (direction) => {
      const panStep = 50; // Pixels to move per click
      
      switch (direction) {
        case 'up':
          setPanY(prev => prev - panStep);
          break;
        case 'down':
          setPanY(prev => prev + panStep);
          break;
        case 'left':
          setPanX(prev => prev - panStep);
          break;
        case 'right':
          setPanX(prev => prev + panStep);
          break;
        default:
          break;
      }
    };

    const positionedNodes = createDiagramLayout();

    return (
      <div className="dependency-diagram-main">
        <div className="diagram-canvas-container">
          {/* Zoom and Pan Controls */}
          <div className="diagram-controls">
            {/* Zoom Controls */}
            <div className="zoom-controls">
              <button 
                onClick={handleZoomOut} 
                className="zoom-btn zoom-out-btn"
                title="Zoom Out"
              >
                −
              </button>
              <span className="zoom-level-display">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button 
                onClick={handleZoomIn} 
                className="zoom-btn zoom-in-btn"
                title="Zoom In"
              >
                +
              </button>
              <button 
                onClick={handleResetZoom} 
                className="zoom-btn reset-btn"
                title="Reset View"
              >
                🔄
              </button>
            </div>

            {/* Pan Controls */}
            <div className="pan-controls">
              <div className="pan-row">
                <button 
                  onClick={() => handlePan('up')} 
                  className="pan-btn pan-up-btn"
                  title="Move Up"
                >
                  ↑
                </button>
              </div>
              <div className="pan-row">
                <button 
                  onClick={() => handlePan('left')} 
                  className="pan-btn pan-left-btn"
                  title="Move Left"
                >
                  ←
                </button>
                <div className="pan-center"></div>
                <button 
                  onClick={() => handlePan('right')} 
                  className="pan-btn pan-right-btn"
                  title="Move Right"
                >
                  →
                </button>
              </div>
              <div className="pan-row">
                <button 
                  onClick={() => handlePan('down')} 
                  className="pan-btn pan-down-btn"
                  title="Move Down"
                >
                  ↓
                </button>
              </div>
            </div>
          </div>

          <svg 
            width="800" 
            height="400" 
            className="dependency-svg-main"
            style={{
              transform: `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`,
              transformOrigin: 'center',
              transition: 'transform 0.2s ease-in-out'
            }}
          >
            {/* Grid background */}
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#374151" strokeWidth="0.5"/>
              </pattern>
              <marker
                id="arrowhead"
                markerWidth="8"
                markerHeight="6"
                refX="8"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 8 3, 0 6" fill="#cbd5e0" />
              </marker>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            {/* Draw connections */}
            {network.edges.map((edge, index) => {
              const fromNode = positionedNodes.find(n => n.id === edge.from);
              const toNode = positionedNodes.find(n => n.id === edge.to);
              
              if (!fromNode || !toNode) return null;
              
              return (
                <g key={index}>
                  <line
                    x1={fromNode.x}
                    y1={fromNode.y}
                    x2={toNode.x}
                    y2={toNode.y}
                    stroke="#cbd5e0"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
                  {/* Edge label */}
                  <text
                    x={(fromNode.x + toNode.x) / 2}
                    y={(fromNode.y + toNode.y) / 2 - 10}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#4a5568"
                    className="edge-label"
                  >
                    {edge.type ? edge.type.replace('_', ' ') : ''}
                  </text>
                </g>
              );
            })}
            
            {/* Draw nodes */}
            {positionedNodes.map((node, index) => {
              const nodeSize = node.level === 'target' ? 40 : 30;
              const isSelected = selectedNodeName && (
                node.id === selectedNodeName || 
                node.id === selectedNodeName.replace(/\.(cls|trigger|object|flow|layout)$/, '')
              );
              
              return (
                <g key={index}>
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={nodeSize}
                    fill={getNodeColor(node.type, node.level, isSelected)}
                    stroke={isSelected ? "#ffffff" : node.level === 'target' ? "#ffffff" : "none"}
                    strokeWidth={isSelected ? 3 : node.level === 'target' ? 2 : 0}
                    className="dependency-node-clickable"
                    onClick={() => onNodeClick(node.id)}
                    style={{ cursor: 'pointer' }}
                  />
                  <text
                    x={node.x}
                    y={node.y - 5}
                    textAnchor="middle"
                    fontSize="20"
                    fill="white"
                    style={{ pointerEvents: 'none' }}
                  >
                    {getNodeIcon(node.type)}
                  </text>
                  <text
                    x={node.x}
                    y={node.y + nodeSize + 15}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#d1d5db"
                    style={{ pointerEvents: 'none' }}
                  >
                    {node.id.length > 15 ? node.id.substring(0, 15) + '...' : node.id}
                  </text>
                  <text
                    x={node.x}
                    y={node.y + nodeSize + 27}
                    textAnchor="middle"
                    fontSize="8"
                    fill="#9ca3af"
                    style={{ pointerEvents: 'none' }}
                  >
                    {node.type || 'Object'}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Relationship Details */}
        <div className="relationship-details-section">
          <h4>Dependencies</h4>
          <div className="relationship-cards-clean">
            {relationships.relationships && relationships.relationships.length > 0 ? (
              relationships.relationships.map((rel, index) => (
                <div key={index} className="relationship-detail-card-clean">
                  <div className="relationship-main">
                    <span className="relationship-icon">
                      {rel.amd_dependency_type?.includes('flow') ? '🔀' : 
                       rel.amd_dependency_type?.includes('object') ? '📦' : 
                       rel.amd_dependency_type?.includes('class') ? '⚡' : '🔗'}
                    </span>
                    <div className="relationship-path-clean">
                      {(() => {
                        const currentComponentName = selectedObject?.amc_dev_name || selectedObject?.name;
                        const fromName = rel.from_dev_name || rel.amd_from_component_id;
                        const toName = rel.to_dev_name || rel.amd_to_component_id;
                        const isFromCurrent = fromName === currentComponentName;
                        const isToCurrent = toName === currentComponentName;
                        
                        return (
                          <span className="path-text-clean">
                            {isFromCurrent ? (
                              <span className="current-component-clean">
                                {fromName}
                              </span>
                            ) : (
                              <span 
                                className="clickable-dependency-clean"
                                onClick={() => handleDependencyClick(fromName)}
                                style={{ 
                                  cursor: 'pointer', 
                                  color: '#2196F3', 
                                  textDecoration: 'underline',
                                  fontWeight: '500'
                                }}
                                title={`Click to view ${fromName} details`}
                              >
                                {fromName}
                              </span>
                            )}
                            <span style={{ margin: '0 8px', color: '#666' }}>→</span>
                            {isToCurrent ? (
                              <span className="current-component-clean">
                                {toName}
                              </span>
                            ) : (
                              <span 
                                className="clickable-dependency-clean"
                                onClick={() => handleDependencyClick(toName)}
                                style={{ 
                                  cursor: 'pointer', 
                                  color: '#2196F3', 
                                  textDecoration: 'underline',
                                  fontWeight: '500'
                                }}
                                title={`Click to view ${toName} details`}
                              >
                                {toName}
                              </span>
                            )}
                          </span>
                        );
                      })()}
                    </div>
                    <span className="relationship-type-clean">
                      {rel.amd_dependency_type?.replace('_', ' ').toUpperCase() || 'REFERENCE'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-relationships">
                <p>No dependencies found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (!selectedObject) {
    return (
      <div className="dependency-page-empty">
        <div className="empty-state">
          <div className="empty-icon">🔗</div>
          <h3>No Object Selected</h3>
          <p>Please select a metadata object to view its dependencies</p>
        </div>
      </div>
    );
  }

  // Handle both old and new object structures
  const objectName = selectedObject.name || selectedObject.amc_dev_name || selectedObject.dev_name;
  const objectId = selectedObject.amc_id || selectedObject.id;
  
  // Additional safety check for object name
  if (!objectName) {
    console.error('Object has no valid name:', selectedObject);
    return (
      <div className="dependency-page-empty">
        <div className="empty-state">
          <div className="empty-icon">⚠️</div>
          <h3>Invalid Object</h3>
          <p>The selected object does not have a valid name</p>
          <pre style={{ fontSize: '10px', color: '#666' }}>
            {JSON.stringify(selectedObject, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  const stats = objectDetails.relationships?.stats || {
    total_relationships: 0,
    incoming: 0,
    outgoing: 0
  };

  const connectedObjects = objectDetails.relationships?.network?.nodes?.length || 0;

  return (
    <div className="dependency-page-layout">
      {/* Header */}
      <div className="dependency-page-header">
        <button onClick={onBack} className="back-to-explorer-btn">
          ← Back to Explorer
        </button>
        <div className="header-object-info">
          <h1>{objectName}</h1>
          <span className="object-type-badge">{getObjectType(objectName)}</span>
        </div>
      </div>

      {/* Content Layout */}
      <div className="dependency-content-layout">
        {/* Left Side - Diagram */}
        <div className="dependency-left-panel">
          {/* Tabs */}
          <div className="dependency-tabs">
            <button 
              className={`dependency-tab ${activeTab === 'diagram' ? 'active' : ''}`}
              onClick={() => setActiveTab('diagram')}
            >
              📊 Dependency Diagram
            </button>
            <button 
              className={`dependency-tab ${activeTab === 'details' ? 'active' : ''}`}
              onClick={() => setActiveTab('details')}
            >
              📄 Object Details
            </button>
            <button 
              className={`dependency-tab ${activeTab === 'xml' ? 'active' : ''}`}
              onClick={() => setActiveTab('xml')}
            >
              🔧 XML Source
            </button>
          </div>

          {/* Statistics */}
          <div className="dependency-statistics">
            <div className="stat-card">
              <div className="stat-number">{stats.total_relationships}</div>
              <div className="stat-label">Total Dependencies</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.incoming}</div>
              <div className="stat-label">Incoming</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.outgoing}</div>
              <div className="stat-label">Outgoing</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{connectedObjects}</div>
              <div className="stat-label">Connected Objects</div>
            </div>
          </div>

          {/* Tab Content */}
          <div className="dependency-tab-content">
            {activeTab === 'diagram' && (
              <div className="dependency-diagram-container">
                {loading.relationships ? (
                  <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading dependency diagram...</p>
                  </div>
                ) : (
                  <DependencyDiagram 
                    relationships={objectDetails.relationships} 
                    onNodeClick={handleNodeClick}
                    selectedNodeName={rightPanelObject?.name}
                  />
                )}
              </div>
            )}

            {activeTab === 'details' && (
              <div className="object-details-content">
                <div className="details-section">
                  <h3>Description</h3>
                  {loading.summary ? (
                    <p className="loading-text">Loading AI summary...</p>
                  ) : (
                    <p className="description-text">{objectDetails.summary}</p>
                  )}
                </div>
                
                <div className="details-section">
                  <h3>Metadata Info</h3>
                  <div className="info-grid">
                    <div className="info-row">
                      <span className="info-label">Type</span>
                      <span className="info-value">{getObjectType(objectName)}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Last Modified</span>
                      <span className="info-value">
                        {selectedObject?.lastModified ? formatDate(selectedObject.lastModified) : "Unknown"}
                      </span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Dependencies</span>
                      <span className="info-value">
                        {stats.total_relationships} Dependencies
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'xml' && (
              <div className="xml-content">
                <div className="xml-header">
                  <h3>XML Source</h3>
                  <button className="copy-btn" onClick={copyXmlToClipboard}>
                    📋 Copy XML
                  </button>
                </div>
                {loading.xml ? (
                  <p className="loading-text">Loading XML...</p>
                ) : (
                  <div className="xml-container">
                    <pre className="xml-code">
                      <code>{objectDetails.xml}</code>
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Side - Object Details */}
        <div className="dependency-right-panel">
          <div className="right-panel-header">
            <h3>Metadata Details</h3>
            <button className="close-panel-btn" onClick={() => setRightPanelObject(selectedObject)}>
              🏠
            </button>
          </div>
          
          <div className="right-panel-content">
            {rightPanelObject ? (
              <>
                <div className="panel-object-header">
                  <h4>{rightPanelObject.name}</h4>
                  <button className="add-to-list-panel-btn">
                    📋 Add to List
                  </button>
                </div>

                <div className="panel-sections">
                  {/* Description */}
                  <div className="panel-section">
                    <h5>Description</h5>
                    {rightPanelLoading ? (
                      <p className="loading-text">Loading AI summary...</p>
                    ) : rightPanelDetails.summary.startsWith('Error') || rightPanelDetails.summary.startsWith('Failed') ? (
                      <p className="api-error-text">{rightPanelDetails.summary}</p>
                    ) : (
                      <p className="description-text">
                        {rightPanelDetails.summary}
                      </p>
                    )}
                  </div>

                  {/* Metadata Info */}
                  <div className="panel-section">
                    <h5>Metadata Info</h5>
                    <div className="panel-info-grid">
                      <div className="panel-info-row">
                        <span className="panel-info-label">Type</span>
                        <span className="panel-info-value">
                          {rightPanelObject.type ? getObjectTypeFromNodeType(rightPanelObject.type) : getObjectType(rightPanelObject?.name)}
                        </span>
                      </div>
                      <div className="panel-info-row">
                        <span className="panel-info-label">Last Modified</span>
                        <span className="panel-info-value">
                          {rightPanelObject.lastModified ? formatDate(rightPanelObject.lastModified) : "Unknown"}
                        </span>
                      </div>
                      <div className="panel-info-row">
                        <span className="panel-info-label">Dependencies</span>
                        <span className="panel-info-value">
                          {rightPanelLoading ? (
                            'Loading...'
                          ) : (
                            rightPanelDetails.relationships?.stats?.total_relationships || 
                            rightPanelDetails.relationships?.total_relationships || 
                            rightPanelDetails.relationships?.relationships?.length || 
                            0
                          )} Dependencies
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* XML */}
                  <div className="panel-section">
                    <h5>XML Preview</h5>
                    {rightPanelLoading ? (
                      <p className="loading-text">Loading XML...</p>
                    ) : rightPanelDetails.xml.startsWith('Error') || rightPanelDetails.xml.startsWith('Failed') ? (
                      <p className="api-error-text">{rightPanelDetails.xml}</p>
                    ) : (
                      <div className="panel-xml-container">
                        <pre className="panel-xml-code">
                          <code>{rightPanelDetails.xml.length > 500 ? 
                            rightPanelDetails.xml.substring(0, 500) + '\n\n... (truncated)' : 
                            rightPanelDetails.xml}
                          </code>
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="no-panel-selection">
                <p>Click on a node to see its details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DependencyPage;