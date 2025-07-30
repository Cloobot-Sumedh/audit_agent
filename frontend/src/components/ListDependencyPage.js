import React, { useState, useEffect } from 'react';
import '../zoom-controls.css';

const API_BASE_URL = 'http://localhost:5000/api';

const ListDependencyPage = ({ selectedList, onBack, onNavigateToDependency }) => {
  console.log('=== LIST DEPENDENCY PAGE RENDERED ===');
  console.log('selectedList:', selectedList);
  
  const [dependencyData, setDependencyData] = useState({
    network: { nodes: [], edges: [] },
    stats: { total_components: 0, total_relationships: 0 }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  
  // Right panel state
  const [rightPanelObject, setRightPanelObject] = useState(null);
  const [rightPanelDetails, setRightPanelDetails] = useState({
    summary: '',
    relationships: null,
    xml: '',
  });
  const [rightPanelLoading, setRightPanelLoading] = useState(false);

  useEffect(() => {
    if (selectedList && selectedList.id) {
      loadListDependencies();
    }
  }, [selectedList]);

  useEffect(() => {
    if (rightPanelObject) {
      loadRightPanelDetails();
    }
  }, [rightPanelObject]);

  const loadListDependencies = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log(`Loading dependencies for list: ${selectedList.id}`);
      
      const response = await fetch(`${API_BASE_URL}/mylists/${selectedList.id}/dependency-network`);
      const data = await response.json();
      
      if (data.success) {
        console.log('Dependency data loaded:', data);
        setDependencyData({
          network: data.network,
          stats: data.stats
        });
      } else {
        setError(data.error || 'Failed to load dependency data');
        console.error('Failed to load dependencies:', data.error);
      }
    } catch (error) {
      setError('Error loading dependency data');
      console.error('Error loading dependencies:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRightPanelDetails = async () => {
    if (!rightPanelObject) return;
    
    setRightPanelLoading(true);
    
    try {
      const objectId = rightPanelObject.amc_id || rightPanelObject.id;
      
      if (!objectId) {
        console.error('Cannot load object details: missing amc_id', rightPanelObject);
        setRightPanelDetails({
          summary: 'Unable to load details - missing object ID',
          relationships: null,
          xml: 'Unable to load XML - missing object ID'
        });
        return;
      }

      // Get component details
      const detailsResponse = await fetch(`${API_BASE_URL}/metadata-component/${objectId}/details`);
      const detailsData = await detailsResponse.json();
      
      let summary = 'Unable to load summary.';
      
      if (detailsData.success) {
        if (detailsData.ai_summary && detailsData.ai_summary.trim()) {
          summary = detailsData.ai_summary;
        } else {
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
            } else {
              summary = 'Unable to generate AI summary.';
            }
          } catch (error) {
            console.error('Error generating summary:', error);
            summary = 'Error generating AI summary.';
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

      setRightPanelDetails({
        summary: summary,
        relationships: relationshipsData.success ? relationshipsData : null,
        xml: xmlData.success ? xmlData.content : 'Unable to load XML content.'
      });
    } catch (error) {
      console.error('Error loading right panel details:', error);
      setRightPanelDetails({
        summary: 'Error loading summary.',
        relationships: null,
        xml: 'Error loading XML content.'
      });
    } finally {
      setRightPanelLoading(false);
    }
  };

  const handleNodeClick = async (nodeId) => {
    console.log('=== NODE CLICKED ===');
    console.log('Raw node ID:', nodeId);
    
    setSelectedNode(nodeId);
    
    // Find the actual node data from the network to get the correct info
    let nodeData = null;
    let componentId = null;
    let componentName = nodeId; // fallback to nodeId
    
    if (dependencyData.network && dependencyData.network.nodes) {
      const foundNode = dependencyData.network.nodes.find(n => 
        n.id === nodeId || n.label === nodeId
      );
      if (foundNode) {
        nodeData = foundNode;
        componentId = foundNode.component_id || foundNode.amc_id || nodeId;
        // Use the label (display name) or amc_dev_name instead of the ID
        componentName = foundNode.label || foundNode.amc_dev_name || foundNode.name || nodeId;
        console.log('Found node data from network:', nodeData);
        console.log('Component name extracted:', componentName);
      }
    }
    
    // If we don't have a component ID, try to search for it by name
    if (!componentId || componentId === nodeId) {
      try {
        const searchResponse = await fetch(`${API_BASE_URL}/search-metadata?search_term=${encodeURIComponent(componentName)}&org_id=409`);
        if (searchResponse.ok) {
          const searchData = await searchResponse.json();
          if (searchData.success && searchData.components && searchData.components.length > 0) {
            const bestMatch = searchData.components.find(comp => 
              comp.amc_dev_name === componentName || 
              comp.amc_dev_name.toLowerCase() === componentName.toLowerCase() ||
              comp.amc_label === componentName
            );
            if (bestMatch) {
              componentId = bestMatch.amc_id;
              componentName = bestMatch.amc_dev_name || bestMatch.amc_label;
              nodeData = { ...nodeData, ...bestMatch };
              console.log('Found component in database:', nodeData);
            }
          }
        }
      } catch (error) {
        console.error('Error searching for component:', error);
      }
    }
    
    // Create a proper object for the clicked node with the correct name
    const nodeObject = {
      name: componentName, // Use the extracted component name, not the ID
      originalId: nodeId,  // Keep the original ID for reference
      lastModified: nodeData?.amc_last_modified || nodeData?.lastModified || new Date().toISOString(),
      type: nodeData?.type || inferObjectTypeFromName(componentName),
      amc_id: componentId,
      amc_dev_name: componentName,
      amc_label: nodeData?.amc_label || componentName,
      ...nodeData
    };
    
    console.log('Created node object with proper name:', nodeObject);
    setRightPanelObject(nodeObject);
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
    if (!filename) return 'Custom Object';
    
    if (filename.endsWith('.cls')) return 'Apex Class';
    if (filename.endsWith('.trigger')) return 'Apex Trigger';
    if (filename.endsWith('.object')) return 'Custom Object';
    if (filename.endsWith('.flow')) return 'Flow';
    if (filename.endsWith('.layout')) return 'Layout';
    return 'Custom Object';
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

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.2, 0.3));
  };

  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handlePan = (direction) => {
    const panAmount = 50;
    setPan(prev => {
      switch (direction) {
        case 'up': return { ...prev, y: prev.y + panAmount };
        case 'down': return { ...prev, y: prev.y - panAmount };
        case 'left': return { ...prev, x: prev.x + panAmount };
        case 'right': return { ...prev, x: prev.x - panAmount };
        default: return prev;
      }
    });
  };

  const getNodeColor = (nodeType, isSelected = false) => {
    if (isSelected) return '#4CAF50';
    
    const type = nodeType?.toLowerCase() || '';
    if (type.includes('apexclass')) return '#2196F3';
    if (type.includes('apextrigger')) return '#FF9800';
    if (type.includes('customobject')) return '#9C27B0';
    if (type.includes('flow')) return '#4CAF50';
    if (type.includes('layout')) return '#607D8B';
    return '#757575';
  };

  const getNodeIcon = (nodeType) => {
    const type = nodeType?.toLowerCase() || '';
    if (type.includes('apexclass')) return '⚡';
    if (type.includes('apextrigger')) return '🔄';
    if (type.includes('customobject')) return '📦';
    if (type.includes('flow')) return '🔀';
    if (type.includes('layout')) return '📋';
    return '📄';
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

  const DependencyDiagram = ({ network, onNodeClick, selectedNodeName }) => {
    const createDiagramLayout = () => {
      const nodes = network.nodes || [];
      const edges = network.edges || [];
      
      if (nodes.length === 0) return { nodes: [], edges: [] };

      // Simple circular layout
      const centerX = 400;
      const centerY = 300;
      const radius = Math.min(200, Math.max(100, nodes.length * 20));
      
      const positionedNodes = nodes.map((node, index) => {
        const angle = (index / nodes.length) * 2 * Math.PI;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
      
        return {
          ...node,
          x: x + pan.x,
          y: y + pan.y,
          isSelected: selectedNodeName === node.id
        };
      });

      return { nodes: positionedNodes, edges };
    };

    const layout = createDiagramLayout();

    return (
      <div className="dependency-diagram" style={{ 
        position: 'relative', 
        width: '100%', 
        height: '600px',
        overflow: 'hidden',
        background: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #444'
      }}>
            {/* Zoom Controls */}
        <div className="zoom-controls" style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          zIndex: 10,
          display: 'flex',
          gap: '5px'
        }}>
          <button onClick={handleZoomIn} className="zoom-btn" title="Zoom In">+</button>
          <button onClick={handleZoomOut} className="zoom-btn" title="Zoom Out">-</button>
          <button onClick={handleResetZoom} className="zoom-btn" title="Reset">⟲</button>
            </div>

            {/* Pan Controls */}
        <div className="pan-controls" style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          gap: '2px'
        }}>
          <button onClick={() => handlePan('up')} className="pan-btn" title="Pan Up">↑</button>
          <div style={{ display: 'flex', gap: '2px' }}>
            <button onClick={() => handlePan('left')} className="pan-btn" title="Pan Left">←</button>
            <button onClick={() => handlePan('right')} className="pan-btn" title="Pan Right">→</button>
          </div>
          <button onClick={() => handlePan('down')} className="pan-btn" title="Pan Down">↓</button>
          </div>

        {/* Diagram Container */}
        <div className="diagram-container" style={{
          transform: `scale(${zoom})`,
              transformOrigin: 'center',
          width: '100%',
          height: '100%',
          position: 'relative'
        }}>
          {/* Edges */}
          <svg style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%',
            pointerEvents: 'none'
          }}>
            {layout.edges.map((edge, index) => {
              const fromNode = layout.nodes.find(n => n.id === edge.from);
              const toNode = layout.nodes.find(n => n.id === edge.to);
              
              if (!fromNode || !toNode) return null;
              
              return (
                  <line
                  key={`edge-${index}`}
                    x1={fromNode.x}
                    y1={fromNode.y}
                    x2={toNode.x}
                    y2={toNode.y}
                  stroke="#666"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
              );
            })}
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
              </marker>
            </defs>
          </svg>

          {/* Nodes */}
          {layout.nodes.map((node) => (
            <div
              key={node.id}
              className={`dependency-node ${node.isSelected ? 'selected' : ''}`}
              style={{
                position: 'absolute',
                left: node.x - 40,
                top: node.y - 30,
                width: 80,
                height: 60,
                background: getNodeColor(node.type, node.isSelected),
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                border: node.isSelected ? '2px solid #fff' : '1px solid #444',
                boxShadow: node.isSelected ? '0 0 10px rgba(76, 175, 80, 0.5)' : '0 2px 4px rgba(0,0,0,0.3)',
                transition: 'all 0.2s ease',
                fontSize: '0.8rem',
                color: 'white',
                textAlign: 'center',
                padding: '4px'
              }}
              onClick={() => onNodeClick(node.id)}
              onMouseEnter={(e) => {
                e.target.style.transform = 'scale(1.05)';
                e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.4)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'scale(1)';
                e.target.style.boxShadow = node.isSelected 
                  ? '0 0 10px rgba(76, 175, 80, 0.5)' 
                  : '0 2px 4px rgba(0,0,0,0.3)';
              }}
            >
              <div style={{ fontSize: '1.2rem', marginBottom: '2px' }}>
                {getNodeIcon(node.type)}
                  </div>
              <div style={{ 
                fontSize: '0.7rem', 
                fontWeight: 'bold',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '70px'
              }}>
                {node.label}
              </div>
          </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="dependency-page">
        <div className="dependency-header">
          <button className="back-btn" onClick={onBack}>
            ← Back to List
          </button>
          <h2>List Dependencies</h2>
        </div>
        <div className="loading-container" style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          color: '#888'
        }}>
          <div className="loading-spinner"></div>
          <p>Loading dependency data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dependency-page">
        <div className="dependency-header">
          <button className="back-btn" onClick={onBack}>
            ← Back to List
          </button>
          <h2>List Dependencies</h2>
        </div>
        <div className="error-container" style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          color: '#e53e3e'
        }}>
          <div>
            <h3>Error Loading Dependencies</h3>
            <p>{error}</p>
            <button onClick={loadListDependencies} className="retry-btn">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dependency-page">
      <div className="dependency-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to List
        </button>
        <h2>Dependencies for "{selectedList?.title}"</h2>
      </div>

      <div className="dependency-content-layout">
        {/* Left Side - Diagram */}
        <div className="dependency-left-panel">
          <div className="dependency-stats" style={{
            display: 'flex',
            gap: '20px',
            marginBottom: '20px',
            padding: '15px',
            background: '#2a2a2a',
            borderRadius: '8px',
            border: '1px solid #444'
          }}>
            <div className="stat-item">
              <span className="stat-label">Components:</span>
              <span className="stat-value">{dependencyData.stats.total_components}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Relationships:</span>
              <span className="stat-value">{dependencyData.stats.total_relationships}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Zoom:</span>
              <span className="stat-value">{Math.round(zoom * 100)}%</span>
            </div>
          </div>

          {dependencyData.network.nodes.length === 0 ? (
            <div className="no-dependencies" style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '400px',
              color: '#888',
              textAlign: 'center'
            }}>
              <div>
                <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🔗</div>
                <h3>No Dependencies Found</h3>
                <p>This list doesn't have any dependency relationships between its components.</p>
              </div>
            </div>
          ) : (
            <DependencyDiagram 
              network={dependencyData.network}
              onNodeClick={handleNodeClick}
              selectedNodeName={selectedNode}
            />
          )}
        </div>

        {/* Right Side - Component Details */}
        <div className="dependency-right-panel">
          <div className="right-panel-header">
            <h3>Component Details</h3>
            {rightPanelObject && (
              <button className="close-panel-btn" onClick={() => setRightPanelObject(null)}>
                ✕
              </button>
            )}
          </div>
          
          <div className="right-panel-content">
            {rightPanelObject ? (
              <>
                <div className="panel-object-header">
                  <h4>{rightPanelObject.name}</h4>
                  <span className="object-type-badge">
                    {getObjectTypeFromNodeType(rightPanelObject.type)}
                  </span>
                </div>

                <div className="panel-sections">
                  {/* Description */}
                  <div className="panel-section">
                    <h5>Description</h5>
                    {rightPanelLoading ? (
                      <p className="loading-text">Loading AI summary...</p>
                    ) : rightPanelDetails.summary.startsWith('Error') || rightPanelDetails.summary.startsWith('Unable') ? (
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
                          {getObjectTypeFromNodeType(rightPanelObject.type)}
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

                  {/* XML Preview */}
                  <div className="panel-section">
                    <div className="xml-header">
                      <h5>XML Preview</h5>
                      <button className="copy-btn" onClick={copyXmlToClipboard} title="Copy XML">
                        📋
                      </button>
                    </div>
                    {rightPanelLoading ? (
                      <p className="loading-text">Loading XML...</p>
                    ) : rightPanelDetails.xml.startsWith('Error') || rightPanelDetails.xml.startsWith('Unable') ? (
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
                <div className="no-selection-icon">📄</div>
                <h4>Select a Component</h4>
                <p>Click on any node in the diagram to view its details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListDependencyPage; 