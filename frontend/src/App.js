import React, { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LoginForm from './components/LoginForm';
import LoadingScreen from './components/LoadingScreen';
import MetadataDashboard from './components/MetadataDashboard';
import MetadataDetails from './components/MetadataDetails';
import DependencyPage from './components/DependencyPage';
import MyListsPage from './components/MyListsPage';
import ListSelectionModal from './components/ListSelectionModal';
import NotificationToast from './components/NotificationToast';
import QuickAddNotification from './components/QuickAddNotification';
import ErrorScreen from './components/ErrorScreen';

// Configure API base URL
const API_BASE_URL = 'http://localhost:5000/api';

const App = () => {
  const [currentScreen, setCurrentScreen] = useState('home'); // home, dashboard, explorer, dependency, details, lists
  const [selectedMetadataType, setSelectedMetadataType] = useState(null);
  const [selectedObject, setSelectedObject] = useState(null);
  const [dependencyObject, setDependencyObject] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([
    { label: 'Home', screen: 'home' }
  ]);

  // Lists state
  const [lists, setLists] = useState([]);

  // Load lists from database
  const loadListsFromDatabase = async () => {
    try {
      console.log('🔄 Loading lists from database...');
      const response = await fetch('http://localhost:5000/api/mylists/user/243/org/409');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          console.log('📋 Raw lists data:', data.mylists);
          
          // Transform database format to frontend format and load components for each list
          const transformedLists = await Promise.all(
            data.mylists.map(async (mylist) => {
              console.log(`🔄 Loading components for list: ${mylist.aml_name} (ID: ${mylist.aml_id})`);
              
              // Load components for this list
              const componentsResponse = await fetch(`http://localhost:5000/api/mylists/${mylist.aml_id}/components`);
              let items = [];
              
              if (componentsResponse.ok) {
                const componentsData = await componentsResponse.json();
                if (componentsData.success) {
                  // Transform database components to frontend format
                  items = componentsData.components.map(comp => ({
                    name: comp.amc_dev_name,
                    amc_id: comp.almm_component_id,
                    type: comp.metadata_type_name,
                    addedToListAt: comp.almm_created_timestamp,
                    content: comp.amc_content,
                    ai_summary: comp.amc_ai_summary
                  }));
                  console.log(`✅ List "${mylist.aml_name}" has ${items.length} components`);
                } else {
                  console.log(`❌ Failed to load components for "${mylist.aml_name}":`, componentsData.error);
                }
              } else {
                console.log(`❌ HTTP error loading components for "${mylist.aml_name}":`, componentsResponse.status);
              }
              
              return {
                id: mylist.aml_id,
                title: mylist.aml_name,
                description: mylist.aml_description,
                items: items,
                createdAt: mylist.aml_created_timestamp
              };
            })
          );
          
          console.log('📋 Final transformed lists:', transformedLists);
          setLists(transformedLists);
        } else {
          console.error('❌ Failed to load lists:', data.error);
        }
      } else {
        console.error('❌ HTTP error loading lists:', response.status);
      }
    } catch (error) {
      console.error('❌ Error loading lists:', error);
    }
  };

  // Load components for a specific list
  const loadListComponents = async (listId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/mylists/${listId}/components`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Preserve the original database structure for MetadataObjectView compatibility
          const transformedComponents = data.components.map(comp => ({
            // Keep original database properties for MetadataObjectView
            amc_id: comp.amc_id, // Use the actual amc_id from the component table
            amc_dev_name: comp.amc_dev_name,
            amc_label: comp.amc_label,
            amc_notes: comp.amc_notes,
            amc_content: comp.amc_content,
            amc_ai_summary: comp.amc_ai_summary,
            amc_ai_model: comp.amc_ai_model,
            amc_last_modified: comp.amc_last_modified,
            amc_api_version: comp.amc_api_version,
            amc_created_timestamp: comp.amc_created_timestamp,
            metadata_type_name: comp.metadata_type_name,
            // Add frontend-specific properties for MyListsPage display
            name: comp.amc_dev_name, // For display in list
            type: comp.metadata_type_name,
            addedToListAt: comp.almm_created_timestamp,
            // Keep the component ID for list operations
            component_id: comp.almm_component_id
          }));

          setLists(prevLists => {
            const listIndex = prevLists.findIndex(list => list.id === listId);
            if (listIndex !== -1) {
              // Update existing list
              const updatedLists = [...prevLists];
              updatedLists[listIndex] = { ...updatedLists[listIndex], items: transformedComponents };
              return updatedLists;
            } else {
              // List doesn't exist yet, add it
              return [...prevLists, {
                id: listId,
                title: `List ${listId}`,
                description: '',
                items: transformedComponents,
                createdAt: new Date().toISOString()
              }];
            }
          });
        }
      }
    } catch (error) {
      console.error('Error loading list components:', error);
    }
  };

  // List modal state
  const [showListModal, setShowListModal] = useState(false);
  const [objectToAdd, setObjectToAdd] = useState(null);

  // Last used list tracking
  const [lastUsedListId, setLastUsedListId] = useState(null);

  // Quick add notification state
  const [quickAddNotification, setQuickAddNotification] = useState({
    isVisible: false,
    objectName: '',
    listName: '',
    objectData: null,
    listIds: []
  });

  // Notification state
  const [notification, setNotification] = useState({
    isVisible: false,
    message: '',
    type: 'success'
  });

  const [extractionState, setExtractionState] = useState({
    status: 'idle', // idle, loading, success, error
    message: '',
    progress: [],
    extractedData: null,
    jobId: null,
    duration: null
  });

  // Load lists from database on component mount
  useEffect(() => {
    loadListsFromDatabase();
  }, []);

  // Navigation functions
  const navigateToHome = () => {
    setCurrentScreen('home');
    setBreadcrumbs([{ label: 'Home', screen: 'home' }]);
    setSelectedMetadataType(null);
    setSelectedObject(null);
    setDependencyObject(null);
  };

  const navigateToDashboardWithData = (dashboardData) => {
    // Set the extraction state with dashboard data
    setExtractionState({
      status: 'success',
      message: 'Metadata loaded successfully',
      progress: [],
      extractedData: {
        totalFiles: dashboardData.total_components || 0,
        outputPath: '',
        types: dashboardData.metadata_stats?.by_type?.map(type => ({
          type: type.metadata_type,
          count: type.component_count,
          icon: '📄',
          description: type.metadata_type
        })) || []
      },
      jobId: dashboardData.latest_job?.aej_id?.toString() || null,
      duration: null
    });
    
    setCurrentScreen('dashboard');
    setBreadcrumbs([
      { label: 'Home', screen: 'home' },
      { label: 'Dashboard', screen: 'dashboard' }
    ]);
  };

  const navigateToDashboard = () => {
    setCurrentScreen('dashboard');
    setBreadcrumbs([
      { label: 'Home', screen: 'home' },
      { label: 'Dashboard', screen: 'dashboard' }
    ]);
  };

  const navigateToExplorer = () => {
    setCurrentScreen('explorer');
    setBreadcrumbs([
      { label: 'Home', screen: 'home' },
      { label: 'Dashboard', screen: 'dashboard' },
      { label: 'Metadata Explorer', screen: 'explorer' }
    ]);
  };

  const navigateToLists = async () => {
    // Load lists from database when navigating to lists page
    await loadListsFromDatabase();
    setCurrentScreen('lists');
    setBreadcrumbs([
      { label: 'Home', screen: 'home' },
      { label: 'Dashboard', screen: 'dashboard' },
      { label: 'My Lists', screen: 'lists' }
    ]);
  };

  const navigateToDependency = (object) => {
    console.log('Navigating to dependency page with object:', object);
    setCurrentScreen('dependency');
    setDependencyObject(object);
    setBreadcrumbs([
      { label: 'Home', screen: 'home' },
      { label: 'Integrations', screen: 'integrations' },
      { label: 'Metadata Dashboard', screen: 'dashboard' },
      { label: 'Metadata Details', screen: 'explorer' },
      { label: 'Dependency Diagram', screen: 'dependency' }
    ]);
  };

  const navigateToDetails = (metadataType, object = null) => {
    setCurrentScreen('details');
    setSelectedMetadataType(metadataType);
    setSelectedObject(object);
    
    const newBreadcrumbs = [
      { label: 'Home', screen: 'home' },
      { label: 'Integrations', screen: 'integrations' },
      { label: 'Metadata Dashboard', screen: 'dashboard' },
      { label: 'Metadata Explorer', screen: 'details' }
    ];
    setBreadcrumbs(newBreadcrumbs);
  };

  const navigateToBreadcrumb = (targetScreen) => {
    if (targetScreen === 'home') {
      navigateToHome();
    } else if (targetScreen === 'dashboard') {
      navigateToDashboard();
    } else if (targetScreen === 'explorer') {
      navigateToExplorer();
    } else if (targetScreen === 'lists') {
      navigateToLists();
    }
  };

  // Smart add to list function
  const handleSmartAddToList = (selectedListIds, metadataObject, listName = null) => {
    console.log('🔄 handleSmartAddToList called with:', { selectedListIds, metadataObject, listName });
    console.log('🔄 metadataObject properties:', Object.keys(metadataObject));
    console.log('🔄 metadataObject.name:', metadataObject.name);
    console.log('🔄 metadataObject.amc_dev_name:', metadataObject.amc_dev_name);
    
    // Update lists
    setLists(prevLists => {
      const updatedLists = [...prevLists];
      
      selectedListIds.forEach(listId => {
        const listIndex = updatedLists.findIndex(list => list.id === listId);
        if (listIndex !== -1) {
          // Check if object already exists in the list
          const objectExists = updatedLists[listIndex].items.some(
            item => item.name === metadataObject.name
          );
          
          if (!objectExists) {
            // Add object to the list with timestamp
            updatedLists[listIndex].items.push({
              ...metadataObject,
              addedToListAt: new Date().toISOString()
            });
          }
        }
      });
      
      return updatedLists;
    });

    // Update last used list
    if (selectedListIds.length > 0) {
      setLastUsedListId(selectedListIds[0]);
    }

    // Determine list name for notification
    const displayListName = listName || 
      (selectedListIds.length === 1 
        ? lists.find(list => list.id === selectedListIds[0])?.title 
        : `${selectedListIds.length} lists`);

    // Use the correct property name for the object name
    const objectDisplayName = metadataObject.name || metadataObject.amc_dev_name || 'Unknown Object';

    // Show quick add notification
    setQuickAddNotification({
      isVisible: true,
      objectName: objectDisplayName,
      listName: displayListName,
      objectData: metadataObject,
      listIds: selectedListIds
    });
  };

  // List management functions
  const handleAddToList = async (listId, metadataObject) => {
    try {
      // Find the list
      const list = lists.find(l => l.id === listId);
      if (!list) {
        showNotification('List not found', 'error');
        return;
      }

      // Check if object is already in the list
      const isAlreadyInList = list.items.some(item => 
        item.name === metadataObject.name || 
        item.amc_id === metadataObject.amc_id
      );
      
      if (isAlreadyInList) {
        showNotification(`${metadataObject.name} is already in this list`, 'warning');
        return;
      }

      // Add to database first
      const response = await fetch(`http://localhost:5000/api/mylists/${listId}/components`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          org_id: 409,
          component_id: metadataObject.amc_id || metadataObject.id,
          notes: `Added via frontend on ${new Date().toISOString()}`
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          showNotification(`${metadataObject.name} added to ${list.title}`, 'success');
          // Reload all lists to ensure counts are updated
          await loadListsFromDatabase();
        } else {
          showNotification(`Failed to add to database: ${data.error}`, 'error');
        }
      } else {
        const errorData = await response.json();
        if (errorData.error && errorData.error.includes('duplicate key')) {
          showNotification(`${metadataObject.name} is already in this list`, 'warning');
        } else {
          showNotification(`Failed to add to database: ${errorData.error}`, 'error');
        }
      }
    } catch (error) {
      console.error('Error adding to list:', error);
      showNotification('Failed to add to list', 'error');
    }
  };

  const handleShowListModal = (metadataObject) => {
    setObjectToAdd(metadataObject);
    setShowListModal(true);
  };

  const handleSaveToLists = async (selectedListIds, metadataObject) => {
    console.log('🔄 Saving to lists:', selectedListIds, metadataObject);
    
    try {
      // Add to each selected list
      for (const listId of selectedListIds) {
        await handleAddToList(listId, metadataObject);
      }
      
      // Show success notification
      if (selectedListIds.length === 1) {
        const list = lists.find(l => l.id === selectedListIds[0]);
        showNotification(`${metadataObject.name} added to ${list?.title || 'list'}`, 'success');
      } else {
        showNotification(`${metadataObject.name} added to ${selectedListIds.length} lists`, 'success');
      }
    } catch (error) {
      console.error('Error saving to lists:', error);
      showNotification('Failed to add to lists', 'error');
    }
  };

  const handleCreateNewList = async (listName) => {
    try {
      console.log('🔄 Creating new list:', listName);
      
      // Create list in database
      const response = await fetch('http://localhost:5000/api/mylists', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          org_id: 409,
          user_id: 243,
          integration_id: 6,
          name: listName,
          description: `Created on ${new Date().toLocaleDateString()}`,
          notes: 'Created via frontend'
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          const newListId = data.list_id;
          
          // Add to local state
    const newList = {
            id: newListId,
      title: listName,
      description: `Created on ${new Date().toLocaleDateString()}`,
      items: [],
      createdAt: new Date().toISOString()
    };
    
    setLists(prevLists => [...prevLists, newList]);
    showNotification(`List "${listName}" created successfully`, 'success');
    
          return newListId;
        } else {
          showNotification(`Failed to create list: ${data.error}`, 'error');
          return null;
        }
      } else {
        const errorData = await response.json();
        showNotification(`Failed to create list: ${errorData.error}`, 'error');
        return null;
      }
    } catch (error) {
      console.error('Error creating new list:', error);
      showNotification('Failed to create list', 'error');
      return null;
    }
  };

  const handleRemoveFromList = async (listId, objectName) => {
    try {
      // Find the object to get its component ID
      const list = lists.find(l => l.id === listId);
      const object = list?.items.find(item => item.name === objectName);
      
      if (!object) {
        showNotification('Object not found in list', 'error');
        return;
      }

      // Remove from local state
      setLists(prevLists => 
        prevLists.map(list => 
          list.id === listId 
            ? { ...list, items: list.items.filter(item => item.name !== objectName) }
            : list
        )
      );

      // Remove from database
      const componentId = object.amc_id || object.id;
      if (componentId) {
        const response = await fetch(`http://localhost:5000/api/mylists/${listId}/components/${componentId}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          showNotification(`${objectName} removed from list`, 'success');
          // Reload all lists to ensure counts are updated
          await loadListsFromDatabase();
        } else {
          const errorData = await response.json();
          showNotification(`Failed to remove from database: ${errorData.error}`, 'error');
        }
      } else {
        showNotification(`${objectName} removed from list`, 'success');
      }
    } catch (error) {
      console.error('Error removing from list:', error);
      showNotification('Failed to remove from list', 'error');
    }
  };

  const handleDeleteList = (listId) => {
    const listToDelete = lists.find(list => list.id === listId);
    setLists(prevLists => prevLists.filter(list => list.id !== listId));
    
    // If we deleted the last used list, clear the last used list ID
    if (lastUsedListId === listId) {
      setLastUsedListId(null);
    }
    
    showNotification(`List "${listToDelete?.title}" deleted`, 'success');
  };

  const handleRenameList = (listId, newName) => {
    setLists(prevLists => {
      const updatedLists = [...prevLists];
      const listIndex = updatedLists.findIndex(list => list.id === listId);
      
      if (listIndex !== -1) {
        updatedLists[listIndex].title = newName;
      }
      
      return updatedLists;
    });

    showNotification(`List renamed to "${newName}"`, 'success');
  };

  // Quick add notification handlers
  const handleQuickAddClose = () => {
    setQuickAddNotification(prev => ({ ...prev, isVisible: false }));
  };

  const handleQuickAddUndo = () => {
    const { objectData, listIds } = quickAddNotification;
    
    if (objectData && listIds.length > 0) {
      // Remove object from all lists it was added to
      setLists(prevLists => {
        const updatedLists = [...prevLists];
        
        listIds.forEach(listId => {
          const listIndex = updatedLists.findIndex(list => list.id === listId);
          if (listIndex !== -1) {
            updatedLists[listIndex].items = updatedLists[listIndex].items.filter(
              item => item.name !== objectData.name
            );
          }
        });
        
        return updatedLists;
      });
      
      showNotification(`Removed ${objectData.name} from list(s)`, 'info');
    }
    
    setQuickAddNotification(prev => ({ ...prev, isVisible: false }));
  };

  const handleQuickAddChangeList = () => {
    console.log('🔄 handleQuickAddChangeList called');
    const { objectData } = quickAddNotification;
    console.log('🔄 Object data:', objectData);
    setQuickAddNotification(prev => ({ ...prev, isVisible: false }));
    
    // Show the list selection modal
    if (objectData) {
      console.log('🔄 Calling handleShowListModal with objectData');
      handleShowListModal(objectData);
    } else {
      console.log('🔄 No objectData available');
    }
  };

  // Notification function
  const showNotification = (message, type = 'success') => {
    setNotification({
      isVisible: true,
      message,
      type
    });
  };

  const hideNotification = () => {
    setNotification(prev => ({ ...prev, isVisible: false }));
  };

  // Poll for job status updates
  useEffect(() => {
    let intervalId;
    
    if (extractionState.status === 'loading' && extractionState.jobId) {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/job-status/${extractionState.jobId}`);
          const result = await response.json();
          
          if (result.success) {
            setExtractionState(prev => ({
              ...prev,
              status: result.status === 'starting' ? 'loading' : result.status,
              progress: result.progress || [],
              extractedData: result.data,
              error: result.error,
              duration: result.duration,
              message: result.status === 'success' ? 'Metadata extraction completed successfully!' :
                      result.status === 'error' ? result.error :
                      'Processing...'
            }));
            
            // Navigate to dashboard when extraction is successful
            if (result.status === 'success') {
              clearInterval(intervalId);
              navigateToDashboard();
            } else if (result.status === 'error') {
              clearInterval(intervalId);
            }
          }
        } catch (error) {
          console.error('Error polling job status:', error);
          setExtractionState(prev => ({
            ...prev,
            status: 'error',
            message: 'Error checking job status'
          }));
          clearInterval(intervalId);
        }
      }, 2000);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [extractionState.status, extractionState.jobId]);

  // Handle login testing (separate from extraction)
  const handleLoginTest = async (credentials) => {
    try {
      const response = await fetch(`${API_BASE_URL}/login-test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
          security_token: credentials.securityToken || '',
          is_sandbox: credentials.environment === 'sandbox'
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        return { success: true, message: result.message };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const handleExtraction = async (formData) => {
    setExtractionState({
      status: 'loading',
      message: 'Starting metadata extraction...',
      progress: ['Initializing extraction process...'],
      extractedData: null,
      jobId: null,
      duration: null
    });

    try {
      // Use the new endpoint that includes login verification
      const response = await fetch(`${API_BASE_URL}/extract-metadata-with-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          security_token: formData.needsToken ? formData.securityToken : '',
          is_sandbox: formData.environment === 'sandbox',
          output_dir: formData.outputDir
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setExtractionState(prev => ({
          ...prev,
          jobId: result.job_id,
          message: result.message || 'Job started successfully'
        }));
      } else {
        throw new Error(result.error || 'Extraction failed');
      }
    } catch (error) {
      setExtractionState({
        status: 'error',
        message: error.message,
        progress: [],
        extractedData: null,
        jobId: null,
        duration: null
      });
    }
  };

  const resetForm = () => {
    setExtractionState({
      status: 'idle',
      message: '',
      progress: [],
      extractedData: null,
      jobId: null,
      duration: null
    });
    navigateToHome();
  };

  const handleNavigateToDependency = (dependencyComponent) => {
    console.log('Navigating to dependency component from App:', dependencyComponent);
    
    // Navigate to the metadata details screen with the dependency component selected
    setCurrentScreen('details');
    setSelectedMetadataType({ type: dependencyComponent.metadata_type_name || 'Unknown', count: 1 });
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
    
    setBreadcrumbs([
      { label: 'Home', screen: 'home' },
      { label: 'Integrations', screen: 'integrations' },
      { label: 'Metadata Dashboard', screen: 'dashboard' },
      { label: 'Metadata Explorer', screen: 'details' }
    ]);
  };

  const renderCurrentScreen = () => {
    if (extractionState.status === 'loading') {
      return (
        <LoadingScreen 
          extractionState={extractionState} 
          onCancel={resetForm}
        />
      );
    }

    if (extractionState.status === 'error') {
      return (
        <ErrorScreen 
          extractionState={extractionState} 
          onRetry={resetForm}
        />
      );
    }

    switch (currentScreen) {
      case 'home':
        return (
          <LoginForm 
            onExtract={handleExtraction}
            onLoginTest={handleLoginTest}
            onNavigateToDashboard={navigateToDashboardWithData}
          />
        );
      
      case 'dashboard':
        return (
          <MetadataDashboard 
            extractionData={extractionState.extractedData}
            jobId={extractionState.jobId}
            lists={lists}
            onMetadataTypeClick={navigateToDetails}
            onExploreMetadata={navigateToExplorer}
            onViewLists={navigateToLists}
            onNewExtraction={resetForm}
          />
        );

      case 'explorer':
        return (
          <MetadataDetails 
            initialSelectedType={selectedMetadataType}
            allTypes={extractionState.extractedData?.types || []}
            totalFiles={extractionState.extractedData?.totalFiles || 0}
            jobId={extractionState.jobId}
            onBackToDashboard={navigateToDashboard}
            onOpenDiagram={navigateToDependency}
            onAddToList={handleSmartAddToList}
            onShowListModal={handleShowListModal}
            lastUsedListId={lastUsedListId}
            lists={lists}
            onNavigateToDependency={handleNavigateToDependency}
          />
        );

      case 'dependency':
        return (
          <DependencyPage
            selectedObject={dependencyObject}
            jobId={extractionState.jobId}
            onBack={navigateToExplorer}
            onNavigateToDependency={handleNavigateToDependency}
          />
        );

      case 'lists':
        return (
          <MyListsPage
            lists={lists}
            onBack={navigateToDashboard}
            jobId={extractionState.jobId}
            onOpenDiagram={navigateToDependency}
            onRemoveFromList={handleRemoveFromList}
            onDeleteList={handleDeleteList}
            onRenameList={handleRenameList}
            onAddToList={handleAddToList}
            onLoadListComponents={loadListComponents}
            onNavigateToDependency={handleNavigateToDependency}
          />
        );
      
      case 'details':
        return (
          <MetadataDetails 
            initialSelectedType={selectedMetadataType}
            allTypes={extractionState.extractedData?.types || []}
            totalFiles={extractionState.extractedData?.totalFiles || 0}
            jobId={extractionState.jobId}
            onBackToDashboard={navigateToDashboard}
            onOpenDiagram={navigateToDependency}
            onAddToList={handleSmartAddToList}
            onShowListModal={handleShowListModal}
            lastUsedListId={lastUsedListId}
            lists={lists}
            onNavigateToDependency={handleNavigateToDependency}
          />
        );
      
      default:
        return (
          <LoginForm 
            onExtract={handleExtraction}
            onLoginTest={handleLoginTest}
            onNavigateToDashboard={navigateToDashboardWithData}
          />
        );
    }
  };

  return (
    <div className="app">
      <Sidebar currentScreen={currentScreen} />
      <div className="main-content">
        <Header 
          breadcrumbs={breadcrumbs}
          onBreadcrumbClick={navigateToBreadcrumb}
        />
        <div className="content-area">
          {renderCurrentScreen()}
        </div>
      </div>

      {/* List Selection Modal */}
      <ListSelectionModal
        isOpen={showListModal}
        onClose={() => {
          setShowListModal(false);
          setObjectToAdd(null);
        }}
        onSave={handleSaveToLists}
        availableLists={lists}
        selectedObject={objectToAdd}
        onCreateNewList={handleCreateNewList}
      />

      {/* Quick Add Notification */}
      <QuickAddNotification
        isVisible={quickAddNotification.isVisible}
        objectName={quickAddNotification.objectName}
        listName={quickAddNotification.listName}
        onClose={handleQuickAddClose}
        onUndo={handleQuickAddUndo}
        onChangeList={handleQuickAddChangeList}
      />

      {/* Notification Toast */}
      <NotificationToast
        isVisible={notification.isVisible}
        message={notification.message}
        type={notification.type}
        onClose={hideNotification}
      />
    </div>
  );
};

export default App;