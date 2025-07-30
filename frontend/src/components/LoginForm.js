import React, { useState, useEffect } from 'react';
import './LoginForm.css';
import LoadingScreen from './LoadingScreen';

const LoginForm = ({ onExtract, onLoginTest, onNavigateToDashboard }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showLoginPopup, setShowLoginPopup] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [loginCredentials, setLoginCredentials] = useState({
    username: '',
    password: '',
    securityToken: ''
  });
  const [loginLoading, setLoginLoading] = useState(false);
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [extracting, setExtracting] = useState({});
  
  // Loading screen state
  const [showLoadingScreen, setShowLoadingScreen] = useState(false);
  const [extractionState, setExtractionState] = useState({
    status: 'loading',
    message: 'Starting extraction...',
    progress: []
  });

  // New state for auto-extraction after login
  const [newlyAddedIntegration, setNewlyAddedIntegration] = useState(null);
  const [showLoginSuccessPopup, setShowLoginSuccessPopup] = useState(false);

  // Load integrations on component mount
  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:5000/api/dashboard/user/243/org/409');
      const data = await response.json();
      
      if (data.success) {
        setIntegrations(data.integrations);
      } else {
        setError(data.error || 'Failed to load integrations');
      }
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error loading integrations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExtract = async (integrationId) => {
    try {
      setExtracting(prev => ({ ...prev, [integrationId]: true }));
      
      // Show loading screen
      setShowLoadingScreen(true);
      setExtractionState({
        status: 'loading',
        message: 'Starting metadata extraction...',
        progress: []
      });
      
      // Start extraction
      const response = await fetch(`http://localhost:5000/api/dashboard/extract/${integrationId}`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        const jobId = data.job_id;
        
        // Poll for job completion with progress updates
        pollJobStatus(jobId, integrationId);
      } else {
        setError(data.error || 'Failed to start extraction');
        setExtracting(prev => ({ ...prev, [integrationId]: false }));
        setShowLoadingScreen(false);
      }
    } catch (err) {
      setError('Failed to start extraction');
      setExtracting(prev => ({ ...prev, [integrationId]: false }));
      setShowLoadingScreen(false);
      console.error('Error starting extraction:', err);
    }
  };

  const pollJobStatus = async (jobId, integrationId) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/dashboard/job-status/${jobId}`);
        const data = await response.json();
        
        // Update loading screen with progress
        if (data.progress && Array.isArray(data.progress)) {
          setExtractionState(prev => ({
            ...prev,
            progress: data.progress,
            message: data.progress[data.progress.length - 1] || 'Processing...'
          }));
        }
        
        if (data.status === 'success') {
          // Job completed, navigate to dashboard
          setExtracting(prev => ({ ...prev, [integrationId]: false }));
          setShowLoadingScreen(false);
          onNavigateToDashboard(data.dashboard_data);
        } else if (data.status === 'error') {
          // Handle error
          setError(data.error || 'Extraction failed');
          setExtracting(prev => ({ ...prev, [integrationId]: false }));
          setShowLoadingScreen(false);
        } else {
          // Still running, poll again
          setTimeout(checkStatus, 2000);
        }
      } catch (error) {
        setError('Failed to check job status');
        setExtracting(prev => ({ ...prev, [integrationId]: false }));
        setShowLoadingScreen(false);
        console.error('Error checking job status:', error);
      }
    };
    
    checkStatus();
  };

  const getStatusBadge = (integration) => {
    const latestJob = integration.latest_job;
    const metadataStats = integration.metadata_stats;
    
    if (!latestJob) {
      return <span className="status-badge no-data">No Data</span>;
    }
    
    if (latestJob.aej_job_status === 'completed') {
      return <span className="status-badge completed">Ready</span>;
    }
    
    if (latestJob.aej_job_status === 'error') {
      return <span className="status-badge error">Error</span>;
    }
    
    return <span className="status-badge processing">Processing</span>;
  };

  const getMetadataSummary = (integration) => {
    const metadataStats = integration.metadata_stats;
    if (!metadataStats) return 'No metadata available';
    
    const totalComponents = metadataStats.total_components;
    const typeCount = metadataStats.by_type?.length || 0;
    
    return `${totalComponents} components across ${typeCount} types`;
  };

  const [formData, setFormData] = useState({
    name: '',
    technology: 'Salesforce',
    username: '',
    password: '',
    securityToken: '',
    environment: 'production',
    needsToken: false,
    outputDir: 'metadata_extracted'
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showToken, setShowToken] = useState(false);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleAddIntegration = () => {
    setShowAddForm(true);
    setFormData({
      name: '',
      technology: 'Salesforce',
      username: '',
      password: '',
      securityToken: '',
      environment: 'production',
      needsToken: false,
      outputDir: 'metadata_extracted'
    });
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setFormData({
      name: '',
      technology: 'Salesforce',
      username: '',
      password: '',
      securityToken: '',
      environment: 'production',
      needsToken: false,
      outputDir: 'metadata_extracted'
    });
  };

  // This handles the "Add" button in the modal - tests login and saves integration
  const handleSaveIntegration = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.name || !formData.username || !formData.password) {
      alert('Please fill in all required fields');
      return;
    }

    setLoginLoading(true);

    try {
      // Test login credentials first
      const loginResult = await onLoginTest({
        username: formData.username,
        password: formData.password,
        securityToken: formData.needsToken ? formData.securityToken : '',
        environment: formData.environment
      });
      
      if (loginResult.success) {
        // Login successful - store the integration in database
        const integrationData = {
          username: formData.username,
            password: formData.password,
          security_token: formData.needsToken ? formData.securityToken : '',
          is_sandbox: formData.environment === 'sandbox',
          name: formData.name,
          org_id: 409,
          ext_app_id: 1,
          created_user_id: 243
        };

        // Store integration in database
        const storeResponse = await fetch('http://localhost:5000/api/store-integration', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(integrationData)
        });

        const storeResult = await storeResponse.json();
        
        if (storeResult.success) {
          // Reload integrations to get the new one
          await loadIntegrations();
          
          // Wait a bit for the state to update, then find the newly added integration
          setTimeout(async () => {
            const response = await fetch('http://localhost:5000/api/dashboard/user/243/org/409');
            const data = await response.json();
            
            if (data.success) {
              // Find the newly added integration by name
              const newIntegration = data.integrations.find(integration => 
                integration.integration.i_name === formData.name
              );
              
              if (newIntegration) {
                setNewlyAddedIntegration(newIntegration);
                setShowLoginSuccessPopup(true);
              }
            }
          }, 500);
          
          setShowAddForm(false);
          
        } else {
          alert(`Failed to store integration: ${storeResult.error}`);
        }
        
      } else {
        alert(`Login failed: ${loginResult.error}`);
      }
      
    } catch (error) {
      alert('Login test failed. Please check your credentials.');
    } finally {
      setLoginLoading(false);
    }
  };

  // This handles clicking on an integration tile - starts extraction directly
  const handleIntegrationClick = async (integration) => {
    // Add null checks
    if (!integration || !integration.integration) {
      console.error('Invalid integration data:', integration);
      return;
    }

    if (extracting[integration.integration.i_id]) return;

    // Check if integration has stored credentials
    if (!integration.integration.i_token) {
      alert('This integration needs to be reconfigured. Please edit the integration and re-enter your credentials.');
      return;
    }

    // Show confirmation popup before starting extraction
    setSelectedIntegration(integration);
    setShowLoginPopup(true);
  };

  // This handles the final confirmation to start extraction
  const handleConfirmExtraction = async () => {
    if (!selectedIntegration || !selectedIntegration.integration) {
      console.error('No valid integration selected');
      return;
    }

    setShowLoginPopup(false);

    // Start extraction immediately with stored credentials
    try {
      await handleExtract(selectedIntegration.integration.i_id);
    } catch (error) {
      alert('Failed to start extraction. Please try again.');
    }
  };

  const handleCancelExtraction = () => {
    setShowLoginPopup(false);
    setSelectedIntegration(null);
  };

  const handleCancelLoading = () => {
    setShowLoadingScreen(false);
    setExtracting({});
    setExtractionState({
      status: 'loading',
      message: 'Starting extraction...',
      progress: []
    });
  };

  const getStatusIcon = (integration) => {
    const latestJob = integration.latest_job;
    
    if (!latestJob) return '⚪';
    if (latestJob.aej_job_status === 'completed') return '🟢';
    if (latestJob.aej_job_status === 'error') return '🔴';
    return '🔵';
  };

  const getStatusText = (integration) => {
    const latestJob = integration.latest_job;
    
    if (!latestJob) return 'Not configured';
    if (latestJob.aej_job_status === 'completed') return 'Connected';
    if (latestJob.aej_job_status === 'error') return 'Error';
    return 'Processing';
  };

  if (loading) {
    return (
      <div className="login-form-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your integrated accounts...</p>
        </div>
      </div>
    );
    }

  if (error) {
    return (
      <div className="login-form-container">
        <div className="error-container">
          <h2>Error Loading Integrations</h2>
          <p>{error}</p>
          <button onClick={loadIntegrations} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Show LoadingScreen during extraction */}
      {showLoadingScreen && (
        <LoadingScreen 
          extractionState={extractionState}
          onCancel={handleCancelLoading}
        />
      )}
      
    <div className="login-form-container">
      <div className="integrations-header">
        <div className="header-content">
          <div className="salesforce-integration">
            <div className="integration-icon">
              <span className="salesforce-icon">☁️</span>
            </div>
            <div className="integration-info">
              <h2>Manage your Salesforce Integrations</h2>
              <p>Connect and extract metadata from your Salesforce organization</p>
            </div>
            <div className="integration-actions">
              <button 
                className="add-integration-btn"
                onClick={handleAddIntegration}
                disabled={loginLoading}
              >
                <span>+</span> Add Integration
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="integration-cards">
        {integrations.length === 0 ? (
          <div className="no-integrations">
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>No Integrated Accounts</h3>
              <p>You haven't integrated any Salesforce accounts yet.</p>
              <button onClick={handleAddIntegration} className="add-integration-button">
                Add Your First Integration
              </button>
            </div>
          </div>
        ) : (
          integrations.map((integrationData) => {
            const integration = integrationData.integration;
            const latestJob = integrationData.latest_job;
            const metadataStats = integrationData.metadata_stats;
            
            // Skip rendering if integration is undefined
            if (!integration) {
              console.warn('Integration data is missing:', integrationData);
              return null;
            }
            
            return (
          <div 
                key={integration.i_id} 
                className={`integration-card ${latestJob?.aej_job_status === 'completed' ? 'active' : ''}`}
                onClick={() => !extracting[integration.i_id] && handleIntegrationClick(integrationData)}
                style={{ cursor: extracting[integration.i_id] ? 'not-allowed' : 'pointer' }}
          >
            <div className="card-header">
                  <h3>{integration.i_name || 'Unnamed Integration'}</h3>
              <div className="card-actions">
                    <span className="status-icon">{getStatusIcon(integrationData)}</span>
                    {getStatusBadge(integrationData)}
                <button className="card-action-btn" onClick={(e) => e.stopPropagation()}>⚙️</button>
                <button className="card-action-btn" onClick={(e) => e.stopPropagation()}>ℹ️</button>
              </div>
            </div>
            <div className="card-body">
              <div className="integration-details">
                    <p><strong>Technology:</strong> Salesforce</p>
                    <p><strong>Username:</strong> {integration.i_token ? '***' : 'Not configured'}</p>
                    <p><strong>Environment:</strong> {integration.i_org_type === 'sandbox' ? 'Sandbox' : 'Production'}</p>
                    <p><strong>Status:</strong> <span className={`status-${latestJob?.aej_job_status || 'not-configured'}`}>{getStatusText(integrationData)}</span></p>
                    <p><strong>Instance:</strong> {integration.i_instance_url || 'Not available'}</p>
                  </div>
                  
                  {metadataStats && (
                    <div className="metadata-summary">
                      <h4>Metadata Summary</h4>
                      <p>{getMetadataSummary(integrationData)}</p>
                      {metadataStats.by_type && metadataStats.by_type.length > 0 && (
                        <div className="type-breakdown">
                          {metadataStats.by_type.slice(0, 3).map((type, index) => (
                            <span key={index} className="type-badge">
                              {type.metadata_type}: {type.component_count}
                            </span>
                          ))}
                          {metadataStats.by_type.length > 3 && (
                            <span className="type-badge more">
                              +{metadataStats.by_type.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
              </div>
                  )}
                  
                  {!extracting[integration.i_id] && latestJob?.aej_job_status === 'completed' ? (
                    <button 
                      className="extract-button" 
                      style={{ marginTop: '15px', width: '100%' }}
                      onClick={(e) => {
                        e.stopPropagation();
                        onNavigateToDashboard(integrationData);
                      }}
                    >
                      <span className="button-icon">📊</span>
                      View Dashboard
                    </button>
                  ) : (
                <button 
                  className="extract-button" 
                  style={{ marginTop: '15px', width: '100%' }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleExtract(integration.i_id);
                      }}
                      disabled={extracting[integration.i_id]}
                >
                  <span className="button-icon">🚀</span>
                      {extracting[integration.i_id] ? 'Extracting...' : 'Extract Metadata'}
                </button>
              )}
                </div>
              </div>
            );
          }).filter(Boolean) // Remove null entries
              )}

        {/* Empty integration slots */}
        {Array.from({ length: Math.max(0, 8 - integrations.length) }, (_, index) => (
          <div key={`empty-${index}`} className="integration-card" style={{ opacity: 0.3 }}>
            <div className="card-header">
              <h3>SF Integration</h3>
              <div className="card-actions">
                <button className="card-action-btn">⚙️</button>
                <button className="card-action-btn">ℹ️</button>
              </div>
            </div>
            <div className="card-body">
              <p style={{ color: '#666', fontStyle: 'italic' }}>Available integration slot</p>
            </div>
          </div>
        ))}
      </div>

      {/* Extraction Confirmation Popup */}
      {showLoginPopup && selectedIntegration && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Start Metadata Extraction</h2>
              <button className="close-btn" onClick={handleCancelExtraction}>×</button>
            </div>
            
            <div className="extraction-form" style={{ padding: '25px' }}>
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <div className="integration-icon" style={{ fontSize: '3rem', marginBottom: '15px' }}>
                  ☁️
                </div>
                <h3 style={{ color: 'white', marginBottom: '10px' }}>{selectedIntegration.integration.i_name}</h3>
                <p style={{ color: '#ccc', marginBottom: '20px' }}>
                  Are you ready to extract metadata from this Salesforce {selectedIntegration.integration.i_org_type}?
                </p>
              </div>

              <div className="integration-details" style={{ background: '#333', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                <p><strong>Instance:</strong> {selectedIntegration.integration.i_instance_url}</p>
                <p><strong>Environment:</strong> {selectedIntegration.integration.i_org_type === 'sandbox' ? 'Sandbox' : 'Production'}</p>
                <p><strong>Output Directory:</strong> metadata_extracted</p>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="cancel-button" 
                  onClick={handleCancelExtraction}
                  disabled={extracting[selectedIntegration.integration.i_id]}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="extract-button"
                  onClick={handleConfirmExtraction}
                  disabled={extracting[selectedIntegration.integration.i_id]}
                >
                  <span className="button-icon">🚀</span>
                  Start Extraction
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Integration Modal */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Add Integration</h2>
              <button className="close-btn" onClick={handleCancel}>×</button>
            </div>
            
            <form onSubmit={handleSaveIntegration} className="extraction-form">
              <div className="form-group">
                <label htmlFor="technology">
                  <span className="label-icon">🔧</span>
                  Select Technology *
                </label>
                <select
                  id="technology"
                  name="technology"
                  value={formData.technology}
                  onChange={handleInputChange}
                  required
                  disabled={loginLoading}
                >
                  <option value="Salesforce">Salesforce</option>
                  <option value="SAP">SAP</option>
                  <option value="ServiceNow">ServiceNow</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="name">
                  <span className="label-icon">📝</span>
                  Integration Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Type Name here"
                  required
                  disabled={loginLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="username">
                  <span className="label-icon">👤</span>
                  Username *
                </label>
                <input
                  type="email"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="your.email@company.com"
                  required
                  disabled={loginLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  <span className="label-icon">🔒</span>
                  Password *
                </label>
                <div className="password-input">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Your Salesforce password"
                    required
                    disabled={loginLoading}
                  />
                  <button
                    type="button"
                    className="toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loginLoading}
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="needsToken"
                    checked={formData.needsToken}
                    onChange={handleInputChange}
                    disabled={loginLoading}
                  />
                  <span className="checkmark"></span>
                  I need to use a security token
                </label>
              </div>

              {formData.needsToken && (
                <div className="form-group">
                  <label htmlFor="securityToken">
                    <span className="label-icon">🛡️</span>
                    Token *
                  </label>
                  <div className="password-input">
                    <input
                      type={showToken ? "text" : "password"}
                      id="securityToken"
                      name="securityToken"
                      value={formData.securityToken}
                      onChange={handleInputChange}
                      placeholder="Your security token"
                      disabled={loginLoading}
                    />
                    <button
                      type="button"
                      className="toggle-password"
                      onClick={() => setShowToken(!showToken)}
                      disabled={loginLoading}
                    >
                      {showToken ? '👁️' : '👁️‍🗨️'}
                    </button>
                  </div>
                </div>
              )}

              <div className="form-group">
                <label>
                  <span className="label-icon">🌐</span>
                  Environment
                </label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="environment"
                      value="production"
                      checked={formData.environment === 'production'}
                      onChange={handleInputChange}
                      disabled={loginLoading}
                    />
                    <span className="radio-custom"></span>
                    Production / Developer
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="environment"
                      value="sandbox"
                      checked={formData.environment === 'sandbox'}
                      onChange={handleInputChange}
                      disabled={loginLoading}
                    />
                    <span className="radio-custom"></span>
                    Sandbox
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="outputDir">
                  <span className="label-icon">📁</span>
                  Output Directory
                </label>
                <input
                  type="text"
                  id="outputDir"
                  name="outputDir"
                  value={formData.outputDir}
                  onChange={handleInputChange}
                  placeholder="metadata_extracted"
                  disabled={loginLoading}
                />
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="cancel-button" 
                  onClick={handleCancel}
                  disabled={loginLoading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="extract-button"
                  disabled={loginLoading}
                >
                  {loginLoading ? (
                    <>
                      <div className="login-spinner"></div>
                      Testing Login...
                    </>
                  ) : (
                    <>
                      <span className="button-icon">💾</span>
                      Add Integration
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Login Success Popup */}
      {showLoginSuccessPopup && newlyAddedIntegration && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Login Successful!</h2>
              <button className="close-btn" onClick={() => setShowLoginSuccessPopup(false)}>×</button>
            </div>
            <div className="extraction-form" style={{ padding: '25px' }}>
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <div className="integration-icon" style={{ fontSize: '3rem', marginBottom: '15px' }}>
                  ✅
                </div>
                <h3 style={{ color: 'white', marginBottom: '10px' }}>{newlyAddedIntegration.integration.i_name}</h3>
                <p style={{ color: '#ccc', marginBottom: '20px' }}>
                  Your integration has been added successfully! Would you like to start metadata extraction now?
                </p>
              </div>

              <div className="integration-details" style={{ background: '#333', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                <p><strong>Instance:</strong> {newlyAddedIntegration.integration.i_instance_url}</p>
                <p><strong>Environment:</strong> {newlyAddedIntegration.integration.i_org_type === 'sandbox' ? 'Sandbox' : 'Production'}</p>
                <p><strong>Status:</strong> <span style={{ color: '#4CAF50' }}>Connected</span></p>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="cancel-button" 
                  onClick={() => setShowLoginSuccessPopup(false)}
                >
                  No, thanks
                </button>
                <button 
                  type="button" 
                  className="extract-button"
                  onClick={() => {
                    setShowLoginSuccessPopup(false);
                    handleExtract(newlyAddedIntegration.integration.i_id);
                  }}
                >
                  <span className="button-icon">🚀</span>
                  Start Extraction
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </>
  );
};

export default LoginForm;