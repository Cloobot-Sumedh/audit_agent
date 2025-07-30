# Dashboard Functionality Guide

## Overview

The dashboard functionality allows users to:
1. **View all integrated accounts** on page refresh
2. **Click extract button** to retrieve metadata from database
3. **Access metadata dashboard** with all stored information
4. **No re-extraction needed** - uses stored data from database tables

## API Endpoints

### 1. Get User Dashboard
```bash
GET /api/dashboard/user/{user_id}/org/{org_id}
```
**Response:**
```json
{
  "success": true,
  "integrations": [
    {
      "integration": {
        "i_id": 1,
        "i_name": "My Salesforce Integration",
        "i_instance_url": "https://test.salesforce.com/services/Soap/c/62.0",
        "i_org_type": "sandbox",
        "has_credentials": true
      },
      "latest_job": {
        "aej_id": 1,
        "aej_job_status": "completed",
        "aej_total_files": 150,
        "aej_created_timestamp": "2024-01-01T10:00:00Z"
      },
      "metadata_stats": {
        "total_components": 150,
        "by_type": [
          {
            "metadata_type": "ApexClass",
            "component_count": 50
          },
          {
            "metadata_type": "ApexTrigger", 
            "component_count": 30
          }
        ]
      }
    }
  ],
  "count": 1
}
```

### 2. Get Integration Dashboard
```bash
GET /api/dashboard/integration/{integration_id}
```
**Response:**
```json
{
  "success": true,
  "dashboard_data": {
    "integration": { /* integration details */ },
    "latest_job": { /* latest extraction job */ },
    "metadata_stats": { /* metadata statistics */ },
    "metadata_components": [ /* all metadata components */ ],
    "total_components": 150
  }
}
```

### 3. Extract Metadata for Dashboard
```bash
POST /api/dashboard/extract/{integration_id}
```
**Response:**
```json
{
  "success": true,
  "job_id": "uuid-here",
  "message": "Metadata extraction started for dashboard"
}
```

### 4. Get Dashboard Job Status
```bash
GET /api/dashboard/job-status/{job_id}
```
**Response:**
```json
{
  "success": true,
  "status": "success",
  "progress": ["Step 1", "Step 2", "Step 3"],
  "dashboard_data": { /* complete dashboard data */ },
  "duration": "0:02:30"
}
```

## Frontend Integration

### 1. Page Refresh - Load User Dashboard
```javascript
// On page load/refresh
const loadUserDashboard = async () => {
  try {
    const response = await fetch('/api/dashboard/user/243/org/409');
    const data = await response.json();
    
    if (data.success) {
      // Display all integrations
      displayIntegrations(data.integrations);
    }
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
};
```

### 2. Extract Button Click
```javascript
// When user clicks extract button
const handleExtract = async (integrationId) => {
  try {
    // Start extraction
    const response = await fetch(`/api/dashboard/extract/${integrationId}`, {
      method: 'POST'
    });
    const data = await response.json();
    
    if (data.success) {
      const jobId = data.job_id;
      
      // Poll for job completion
      pollJobStatus(jobId);
    }
  } catch (error) {
    console.error('Error starting extraction:', error);
  }
};

// Poll job status
const pollJobStatus = async (jobId) => {
  const checkStatus = async () => {
    try {
      const response = await fetch(`/api/dashboard/job-status/${jobId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        // Job completed, load dashboard data
        loadDashboardData(data.dashboard_data);
      } else if (data.status === 'error') {
        // Handle error
        console.error('Extraction failed:', data.error);
      } else {
        // Still running, poll again
        setTimeout(checkStatus, 2000);
      }
    } catch (error) {
      console.error('Error checking job status:', error);
    }
  };
  
  checkStatus();
};
```

### 3. Load Dashboard Data
```javascript
// Load complete dashboard data
const loadDashboardData = (dashboardData) => {
  const { integration, latest_job, metadata_stats, metadata_components } = dashboardData;
  
  // Display integration info
  displayIntegrationInfo(integration);
  
  // Display job status
  displayJobStatus(latest_job);
  
  // Display metadata statistics
  displayMetadataStats(metadata_stats);
  
  // Display metadata components
  displayMetadataComponents(metadata_components);
};
```

## Database Tables Used

### 1. `ids_integration`
- Stores Salesforce connection details
- Contains credentials for login

### 2. `ids_audit_extraction_job`
- Tracks extraction jobs
- Links to integration

### 3. `ids_audit_metadata_component`
- Stores individual metadata components
- Contains file content and AI summaries

### 4. `ids_audit_metadata_type`
- Defines metadata types (ApexClass, ApexTrigger, etc.)

## Workflow

### 1. Page Refresh
1. Frontend calls `/api/dashboard/user/{user_id}/org/{org_id}`
2. Backend retrieves all integrations for the user
3. For each integration, gets latest job and metadata stats
4. Returns complete dashboard data
5. Frontend displays all integrations with their status

### 2. Extract Button Click
1. Frontend calls `/api/dashboard/extract/{integration_id}`
2. Backend retrieves stored credentials
3. Starts metadata extraction in background
4. Returns job ID for tracking
5. Frontend polls job status

### 3. Job Completion
1. Backend stores extracted metadata in database
2. Job status becomes 'success'
3. Frontend receives complete dashboard data
4. Displays metadata dashboard with all information

## Benefits

1. **Fast Loading**: No re-extraction needed, uses stored data
2. **Persistent Data**: All metadata stored in database
3. **User-Friendly**: Simple extract button for fresh data
4. **Scalable**: Handles multiple integrations per user
5. **Real-time Updates**: Job status polling for progress

## Testing

Run the dashboard test script:
```bash
python test_dashboard.py
```

This will test:
- User dashboard loading
- Integration dashboard data
- Extraction job creation
- Job status polling

## Usage Example

1. **Store Integration**: Use `/api/store-integration` to store Salesforce credentials
2. **Load Dashboard**: Call `/api/dashboard/user/243/org/409` to get all integrations
3. **Extract Metadata**: Click extract button to trigger `/api/dashboard/extract/{id}`
4. **View Results**: Dashboard shows all metadata components and statistics

The system now provides a complete dashboard experience with persistent data storage and easy access to all metadata information! 