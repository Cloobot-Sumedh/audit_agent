import React from 'react';

const DependencyDiagram = ({ relationships, selectedObject }) => {
  if (!relationships || !relationships.network || relationships.network.nodes.length === 0) {
    return (
      <div className="dependency-diagram empty">
        <div className="empty-dependencies">
          <p>No dependencies found for this object</p>
        </div>
      </div>
    );
  }

  const { network, stats } = relationships;
  
  // Create a simple dependency visualization
  const createDependencyTree = () => {
    const centerX = 200;
    const centerY = 150;
    const radius = 100;
    
    const targetNode = network.nodes.find(n => n.isTarget);
    const otherNodes = network.nodes.filter(n => !n.isTarget);
    
    // Position nodes in a radial layout
    const positionedNodes = [
      { ...targetNode, x: centerX, y: centerY }
    ];
    
    otherNodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / otherNodes.length;
      positionedNodes.push({
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });

    return positionedNodes;
  };

  const getNodeColor = (nodeType) => {
    const colors = {
      'ApexClass': '#3b82f6',
      'ApexTrigger': '#10b981',
      'CustomObject': '#f59e0b',
      'Flow': '#8b5cf6',
      'Layout': '#06b6d4'
    };
    return colors[nodeType] || '#6b7280';
  };

  const getDependencyLevel = (nodeId, targetId, edges) => {
    // Determine if this is a parent or child dependency
    const isParent = edges.some(edge => edge.from === nodeId && edge.to === targetId);
    const isChild = edges.some(edge => edge.from === targetId && edge.to === nodeId);
    
    if (isParent) return 'parent';
    if (isChild) return 'child';
    return 'neutral';
  };

  const positionedNodes = createDependencyTree();
  const targetNodeName = selectedObject?.name?.replace(/\.(cls|trigger|object|flow|layout)$/, '') || '';

  return (
    <div className="dependency-diagram">
      <div className="dependency-stats">
        <div className="stat-item">
          <span className="stat-value">{stats?.total_relationships || 0}</span>
          <span className="stat-label">Dependencies</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{stats?.incoming || 0}</span>
          <span className="stat-label">Dependency A</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{stats?.outgoing || 0}</span>
          <span className="stat-label">Dependency 2</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">3</span>
          <span className="stat-label">Dependency 3</span>
        </div>
      </div>

      <div className="diagram-container">
        <svg width="400" height="300" className="dependency-svg">
          {/* Draw connections first */}
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
                  stroke="#e5e7eb"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                />
              </g>
            );
          })}
          
          {/* Arrow marker definition */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="#e5e7eb"
              />
            </marker>
          </defs>
          
          {/* Draw nodes */}
          {positionedNodes.map((node, index) => {
            const dependencyLevel = getDependencyLevel(node.id, targetNodeName, network.edges);
            
            return (
              <g key={index}>
                <rect
                  x={node.x - 30}
                  y={node.y - 15}
                  width="60"
                  height="30"
                  rx="15"
                  fill={getNodeColor(node.type)}
                  stroke={node.isTarget ? "#1f2937" : "#ffffff"}
                  strokeWidth={node.isTarget ? 3 : 2}
                  className="dependency-node"
                />
                <text
                  x={node.x}
                  y={node.y + 5}
                  textAnchor="middle"
                  fontSize="10"
                  fill="white"
                  fontWeight="bold"
                >
                  {dependencyLevel === 'parent' ? 'A' : 
                   dependencyLevel === 'child' ? node.id.charAt(0).toUpperCase() :
                   node.id.charAt(0).toUpperCase()}
                </text>
                <text
                  x={node.x}
                  y={node.y + 45}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#374151"
                  className="node-label"
                >
                  {`Dependency ${dependencyLevel === 'parent' ? 'A' : node.id.charAt(0).toUpperCase()}`}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {relationships.relationships && relationships.relationships.length > 0 && (
        <div className="relationships-details">
          <h5>Relationship Details</h5>
          <div className="relationships-list">
            {relationships.relationships.slice(0, 3).map((rel, index) => (
              <div key={index} className="relationship-item">
                <div className="relationship-type">
                  <span className="type-badge">{rel.type.replace('_', ' ')}</span>
                </div>
                <div className="relationship-description">
                  {rel.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DependencyDiagram;