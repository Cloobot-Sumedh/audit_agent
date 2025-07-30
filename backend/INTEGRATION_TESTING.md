# Integration Storage Testing Guide

## Problem Fixed

The issue was that the system was storing session tokens instead of actual credentials in the `ids_integration` table. Session tokens expire quickly, so they weren't useful for subsequent logins.

## Solution Implemented

1. **Store Credentials Instead of Session Tokens**: The system now stores actual Salesforce credentials (username, password, security_token) in the database
2. **Secure Storage**: Credentials are stored as JSON in the `i_token` field
3. **Safe Retrieval**: When displaying integration details, sensitive information is hidden

## New Endpoints

### 1. Store Integration
```bash
POST /api/store-integration
```
**Body:**
```json
{
  "username": "your@email.com",
  "password": "yourpassword",
  "security_token": "yourtoken",
  "is_sandbox": true,
  "name": "My Salesforce Integration",
  "org_id": 409,
  "ext_app_id": 1001,
  "created_user_id": 243
}
```

### 2. Login with Stored Integration
```bash
POST /api/login-with-integration/{integration_id}
```

### 3. Get Integration Details (Safe)
```bash
GET /api/integrations/{integration_id}
```
*Returns integration details without exposing credentials*

## Testing Steps

### 1. Start the Server
```bash
cd backend
python server_db.py
```

### 2. Test Integration Storage
```bash
python test_integration_storage.py
```

### 3. Manual Testing with Real Credentials

#### Step 1: Store Integration
```bash
curl -X POST http://localhost:5000/api/store-integration \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your@email.com",
    "password": "yourpassword", 
    "security_token": "yourtoken",
    "is_sandbox": true,
    "name": "My Salesforce Integration"
  }'
```

#### Step 2: Check Stored Integration
```bash
curl -X GET http://localhost:5000/api/integrations/1
```

#### Step 3: Login with Stored Integration
```bash
curl -X POST http://localhost:5000/api/login-with-integration/1
```

## What You Should See

### In the Database (`ids_integration` table):
- `i_name`: "My Salesforce Integration"
- `i_instance_url`: "https://test.salesforce.com/services/Soap/c/62.0"
- `i_org_type`: "sandbox"
- `i_token`: JSON string with credentials
- `i_status`: 1 (active)

### In API Responses:
- Integration details without exposed credentials
- `has_credentials`: true
- `token_length`: length of stored credentials

## Benefits

1. **Persistent Storage**: Credentials are stored for future use
2. **No Re-entry**: Users don't need to enter credentials again
3. **Secure**: Credentials are stored but not exposed in API responses
4. **Flexible**: Can login with stored integration anytime

## Troubleshooting

### If integration storage fails:
1. Check database connection
2. Verify all required fields are provided
3. Ensure Salesforce credentials are valid

### If login with stored integration fails:
1. Check if credentials are still valid
2. Verify integration exists in database
3. Check if Salesforce session has expired

## Next Steps

1. Test with real Salesforce credentials
2. Integrate with frontend to use stored integrations
3. Add credential encryption for enhanced security
4. Implement credential refresh mechanism 