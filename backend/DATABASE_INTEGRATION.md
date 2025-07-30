# Database Integration for Salesforce Metadata Extractor

## Overview

The application now uses PostgreSQL database to store all metadata extraction data, eliminating the need for local storage and enabling persistent data across sessions.

## Database Schema

The application uses the following tables from `audit_agent (2).sql`:

1. **`ids_integration`** - Stores Salesforce connection details
2. **`ids_audit_metadata_type`** - Defines metadata types (ApexClass, ApexTrigger, etc.)
3. **`ids_audit_extraction_job`** - Tracks extraction jobs
4. **`ids_audit_metadata_component`** - Stores individual metadata components
5. **`ids_audit_metadata_dependency`** - Tracks relationships between components
6. **`ids_audit_mylist`** - User-defined lists
7. **`ids_audit_list_metadata_mappings`** - Maps components to lists

## Key Features

### 1. Integration Storage
- When a user logs in successfully, integration details are automatically stored in the database
- Session tokens and instance URLs are preserved for future use
- No need to re-enter credentials for subsequent sessions

### 2. Metadata Persistence
- All extracted metadata is stored in the database
- Components are linked to extraction jobs and integrations
- AI summaries are generated and stored for each component

### 3. Quick Access
- Retrieve metadata without re-extraction using stored integration details
- Search and filter metadata components
- Access historical extraction jobs

## API Endpoints

### Integration Management
- `POST /api/integrations` - Create new integration
- `GET /api/integrations/<id>` - Get integration by ID
- `GET /api/integrations/org/<org_id>` - Get integrations by organization
- `GET /api/integrations/user/<user_id>` - Get user integrations
- `PUT /api/integrations/<id>` - Update integration
- `DELETE /api/integrations/<id>` - Delete integration

### Metadata Access
- `GET /api/metadata-from-integration/<integration_id>` - Get metadata from stored integration
- `GET /api/metadata-components/<job_id>` - Get components by extraction job
- `GET /api/metadata-component/<component_id>` - Get specific component
- `GET /api/search-metadata` - Search metadata components

### Extraction Jobs
- `POST /api/extraction-jobs` - Create extraction job
- `GET /api/extraction-jobs/<id>` - Get job by ID
- `GET /api/extraction-jobs/integration/<id>` - Get jobs by integration
- `PUT /api/extraction-jobs/<id>` - Update job status

### Metadata Types
- `POST /api/metadata-types` - Create metadata type
- `GET /api/metadata-types/org/<org_id>` - Get metadata types

## Workflow

### First Time Login
1. User enters Salesforce credentials
2. System validates login and stores integration details
3. Metadata extraction process runs
4. All components are stored in database with AI summaries
5. User can access metadata immediately

### Subsequent Logins
1. User logs in with same credentials
2. System retrieves stored integration details
3. User can access previously extracted metadata instantly
4. No need for re-extraction unless new metadata is needed

## Database Configuration

The application uses the following database configuration:
- **Host**: cloobotx.postgres.database.azure.com
- **Database**: cloobotx_testing
- **User**: azureusercloobotx
- **Port**: 5432

## Testing

Run the test script to verify database integration:
```bash
python test_integration.py
```

## Benefits

1. **Persistent Storage**: All data is stored in database, not lost on server restart
2. **Faster Access**: No need to re-extract metadata for subsequent logins
3. **Scalability**: Can handle multiple users and organizations
4. **Search & Filter**: Advanced search capabilities across all metadata
5. **Historical Data**: Track extraction jobs and their results over time
6. **AI Integration**: Automatic generation of summaries for all components

## Usage

1. Start the server: `python server_db.py`
2. Initialize database: `python init_database.py`
3. Test functionality: `python test_integration.py`
4. Access the frontend to use the application

The frontend will now work seamlessly with the database backend, providing a much more robust and scalable solution. 