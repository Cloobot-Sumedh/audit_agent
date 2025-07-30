#!/usr/bin/env python3
"""
Flask Backend for Salesforce Metadata Extractor with Database Integration
Starting with Integration table functionality
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import base64
import zipfile
import time
import re
import threading
import uuid
from datetime import datetime, date
import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from database import get_db_manager
import io
from comprehensive_metadata_extraction import get_comprehensive_metadata_retrieve_body

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Get database manager
db = get_db_manager()

# Store active extraction jobs (temporary until we fully migrate to database)
extraction_jobs = {}

def login_to_salesforce(username, password, security_token, is_sandbox):
    """Login and return session details"""
    
    login_url = "https://test.salesforce.com" if is_sandbox else "https://login.salesforce.com"
    
    login_body = f'''<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:enterprise.soap.sforce.com">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:login>
         <urn:username>{username}</urn:username>
         <urn:password>{password}{security_token}</urn:password>
      </urn:login>
   </soapenv:Body>
</soapenv:Envelope>'''
    
    headers = {
        'Content-Type': 'text/xml; charset=UTF-8',
        'SOAPAction': 'login'
    }
    
    try:
        response = requests.post(f"{login_url}/services/Soap/c/62.0", data=login_body, headers=headers)
        
        if response.status_code != 200:
            return None, None, f"HTTP Error: {response.status_code}"
        
        response_text = response.text
        
        # Check for faults
        if '<soapenv:Fault>' in response_text:
            fault_match = re.search(r'<faultstring>(.*?)</faultstring>', response_text)
            if fault_match:
                return None, None, fault_match.group(1)
            return None, None, "Unknown login error"
        
        # Extract session info
        session_match = re.search(r'<sessionId>(.*?)</sessionId>', response_text)
        server_match = re.search(r'<serverUrl>(.*?)</serverUrl>', response_text)
        
        if not session_match or not server_match:
            return None, None, "Could not extract session details"
        
        return session_match.group(1), server_match.group(1), None
        
    except Exception as e:
        return None, None, f"Login exception: {str(e)}"

# ============================================================================
# INTEGRATION TABLE API ENDPOINTS
# ============================================================================

@app.route('/api/integrations', methods=['POST'])
def create_integration():
    """Create a new integration record"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['org_id', 'name', 'instance_url', 'org_type', 'token', 'ext_app_id', 'created_user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create integration in database
        integration_id = db.create_integration(
            org_id=data['org_id'],
            name=data['name'],
            instance_url=data['instance_url'],
            org_type=data['org_type'],
            token=data['token'],
            ext_app_id=data['ext_app_id'],
            created_user_id=data['created_user_id']
        )
        
        if integration_id:
            return jsonify({
                'success': True,
                'integration_id': integration_id,
                'message': 'Integration created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create integration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def parse_stored_credentials(token_data, org_type):
    """Parse stored credentials handling both old and new formats"""
    try:
        # Try JSON format first (new format)
        return json.loads(token_data)
    except:
        # Try old format (username:password:token)
        if ':' in token_data:
            parts = token_data.split(':', 2)
            if len(parts) >= 2:
                return {
                    'username': parts[0],
                    'password': parts[1],
                    'security_token': parts[2] if len(parts) > 2 else '',
                    'is_sandbox': org_type == 'sandbox'
                }
    return None

@app.route('/api/integrations/<int:integration_id>', methods=['GET'])
def get_integration(integration_id):
    """Get integration by ID"""
    try:
        integration = db.get_integration(integration_id)
        
        if integration:
            # Parse credentials to check format
            credentials = parse_stored_credentials(integration['i_token'], integration['i_org_type'])
            
            # Create a safe version of the integration data (hide sensitive info)
            safe_integration = {
                'i_id': integration['i_id'],
                'i_org_id': integration['i_org_id'],
                'i_name': integration['i_name'],
                'i_instance_url': integration['i_instance_url'],
                'i_org_type': integration['i_org_type'],
                'i_ext_app_id': integration['i_ext_app_id'],
                'i_created_user_id': integration['i_created_user_id'],
                'i_created_timestamp': integration['i_created_timestamp'],
                'i_last_updated_user_id': integration['i_last_updated_user_id'],
                'i_last_updated_timestamp': integration['i_last_updated_timestamp'],
                'i_status': integration['i_status'],
                'has_credentials': bool(integration['i_token']),  # Just indicate if credentials exist
                'token_length': len(integration['i_token']) if integration['i_token'] else 0,
                'credentials_format': 'json' if credentials and isinstance(credentials, dict) else 'legacy'
            }
            
            return jsonify({
                'success': True,
                'integration': safe_integration
            })
        else:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/integrations/org/<int:org_id>', methods=['GET'])
def get_integrations_by_org(org_id):
    """Get all integrations for an organization"""
    try:
        integrations = db.get_integrations_by_org(org_id)
        
        return jsonify({
            'success': True,
            'integrations': integrations,
            'count': len(integrations)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/integrations/<int:integration_id>', methods=['PUT'])
def update_integration(integration_id):
    """Update integration record"""
    try:
        data = request.json
        
        # Get existing integration
        integration = db.get_integration(integration_id)
        if not integration:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
        
        # Update integration in database
        rows_updated = db.update_integration(
            integration_id=integration_id,
            name=data.get('name'),
            instance_url=data.get('instance_url'),
            org_type=data.get('org_type'),
            token=data.get('token'),
            ext_app_id=data.get('ext_app_id'),
            last_updated_user_id=data.get('last_updated_user_id')
        )
        
        if rows_updated > 0:
            # Get updated integration
            updated_integration = db.get_integration(integration_id)
            return jsonify({
                'success': True,
                'message': 'Integration updated successfully',
                'integration': updated_integration
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update integration'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/integrations/<int:integration_id>', methods=['DELETE'])
def delete_integration(integration_id):
    """Soft delete integration (set status to -1)"""
    try:
        # Get existing integration
        integration = db.get_integration(integration_id)
        if not integration:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
        
        # Soft delete integration
        rows_updated = db.delete_integration(
            integration_id=integration_id,
            last_updated_user_id=request.json.get('last_updated_user_id') if request.json else None
        )
        
        if rows_updated > 0:
            return jsonify({
                'success': True,
                'message': 'Integration deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete integration'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# METADATA TYPE TABLE API ENDPOINTS
# ============================================================================

@app.route('/api/metadata-types', methods=['POST'])
def create_metadata_type():
    """Create a new metadata type record"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['org_id', 'name', 'display_name', 'description', 'icon', 'file_extension', 'created_user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create metadata type in database
        type_id = db.create_metadata_type(
            org_id=data['org_id'],
            name=data['name'],
            display_name=data['display_name'],
            description=data['description'],
            icon=data['icon'],
            file_extension=data['file_extension'],
            created_user_id=data['created_user_id']
        )
        
        if type_id:
            return jsonify({
                'success': True,
                'type_id': type_id,
                'message': 'Metadata type created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create metadata type'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-types/org/<int:org_id>', methods=['GET'])
def get_metadata_types(org_id):
    """Get all metadata types for an organization"""
    try:
        metadata_types = db.get_metadata_types(org_id)
        
        return jsonify({
            'success': True,
            'metadata_types': metadata_types,
            'count': len(metadata_types)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# EXTRACTION JOB TABLE API ENDPOINTS
# ============================================================================

@app.route('/api/extraction-jobs', methods=['POST'])
def create_extraction_job():
    """Create a new extraction job record"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['org_id', 'integration_id', 'job_status', 'total_files', 'created_user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create extraction job in database
        job_id = db.create_extraction_job(
            org_id=data['org_id'],
            integration_id=data['integration_id'],
            job_status=data['job_status'],
            total_files=data['total_files'],
            created_user_id=data['created_user_id']
        )
        
        if job_id:
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': 'Extraction job created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create extraction job'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/extraction-jobs/<int:job_id>', methods=['GET'])
def get_extraction_job(job_id):
    """Get extraction job by ID"""
    try:
        job = db.get_extraction_job(job_id)
        
        if job:
            return jsonify({
                'success': True,
                'job': job
            })
        else:
            return jsonify({'success': False, 'error': 'Extraction job not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/extraction-jobs/integration/<int:integration_id>', methods=['GET'])
def get_extraction_jobs_by_integration(integration_id):
    """Get all extraction jobs for an integration"""
    try:
        jobs = db.get_extraction_jobs_by_integration(integration_id)
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/extraction-jobs/<int:job_id>', methods=['PUT'])
def update_extraction_job(job_id):
    """Update extraction job status and data"""
    try:
        data = request.json
        
        # Get existing job
        job = db.get_extraction_job(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Extraction job not found'}), 404
        
        # Update job
        db.update_extraction_job(
            job_id=job_id,
            job_status=data.get('job_status'),
            completed_at=data.get('completed_at'),
            total_files=data.get('total_files'),
            log=data.get('log'),
            job_data=data.get('job_data')
        )
        
        return jsonify({
            'success': True,
            'message': 'Extraction job updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@app.route('/api/login-test', methods=['POST'])
def test_login():
    """Test login credentials and store integration details"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'password', 'is_sandbox']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        username = data['username']
        password = data['password'] 
        security_token = data.get('security_token', '')
        is_sandbox = data['is_sandbox']
        
        # Test login
        session_id, server_url, error = login_to_salesforce(username, password, security_token, is_sandbox)
        
        if error:
            return jsonify({'success': False, 'error': error}), 401
        
        # Login successful - store integration details in database
        try:
            # Create integration record with credentials (not session token)
            integration_id = db.create_integration(
                org_id=409,  # Using default org_id from test_db.py
                name=f"Integration for {username}",
                instance_url=server_url,
                org_type="sandbox" if is_sandbox else "production",
                token=f"{username}:{password}:{security_token}",  # Store credentials instead of session token
                ext_app_id=1001,  # Default app ID
                created_user_id=243  # Using default user_id from test_db.py
            )
            
            if integration_id:
                return jsonify({
                    'success': True, 
                    'message': 'Login successful and integration stored',
                    'session_valid': True,
                    'environment': 'Sandbox' if is_sandbox else 'Production',
                    'integration_id': integration_id,
                    'instance_url': server_url
                })
            else:
                return jsonify({
                    'success': True, 
                    'message': 'Login successful but failed to store integration',
                    'session_valid': True,
                    'environment': 'Sandbox' if is_sandbox else 'Production'
                })
                
        except Exception as db_error:
            # Login worked but database storage failed
            return jsonify({
                'success': True, 
                'message': 'Login successful but database storage failed',
                'session_valid': True,
                'environment': 'Sandbox' if is_sandbox else 'Production',
                'db_error': str(db_error)
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/store-integration', methods=['POST'])
def store_integration():
    """Store integration details with credentials"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'password', 'is_sandbox', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        username = data['username']
        password = data['password'] 
        security_token = data.get('security_token', '')
        is_sandbox = data['is_sandbox']
        name = data['name']
        
        # Test login first to validate credentials
        session_id, server_url, error = login_to_salesforce(username, password, security_token, is_sandbox)
        
        if error:
            return jsonify({'success': False, 'error': error}), 401
        
        # Store credentials in a more secure format
        credentials = {
            'username': username,
            'password': password,
            'security_token': security_token,
            'is_sandbox': is_sandbox
        }
        
        # Create integration record
        integration_id = db.create_integration(
            org_id=data.get('org_id', 409),
            name=name,
            instance_url=server_url,
            org_type="sandbox" if is_sandbox else "production",
            token=json.dumps(credentials),  # Store credentials as JSON
            ext_app_id=data.get('ext_app_id', 1001),
            created_user_id=data.get('created_user_id', 243)
        )
        
        if integration_id:
            return jsonify({
                'success': True,
                'message': 'Integration stored successfully',
                'integration_id': integration_id,
                'instance_url': server_url
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to store integration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login-with-integration/<int:integration_id>', methods=['POST'])
def login_with_integration(integration_id):
    """Login using stored integration credentials"""
    try:
        # Get integration details
        integration = db.get_integration(integration_id)
        if not integration:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
        
        # Parse stored credentials using utility function
        credentials = parse_stored_credentials(integration['i_token'], integration['i_org_type'])
        
        if not credentials:
            return jsonify({'success': False, 'error': 'Invalid stored credentials format'}), 400
        
        # Login using stored credentials
        session_id, server_url, error = login_to_salesforce(
            credentials['username'],
            credentials['password'],
            credentials.get('security_token', ''),
            credentials['is_sandbox']
        )
        
        if error:
            return jsonify({'success': False, 'error': error}), 401
        
        return jsonify({
            'success': True,
            'message': 'Login successful using stored integration',
            'session_valid': True,
            'environment': 'Sandbox' if credentials['is_sandbox'] else 'Production',
            'integration_id': integration_id,
            'instance_url': server_url
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/integrations/user/<int:user_id>', methods=['GET'])
def get_user_integrations(user_id):
    """Get all integrations for a user"""
    try:
        # Get integrations for the user's organization
        integrations = db.get_integrations_by_org(org_id=409)  # Using default org_id
        
        return jsonify({
            'success': True,
            'integrations': integrations,
            'count': len(integrations)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/user/<int:user_id>/org/<int:org_id>', methods=['GET'])
def get_user_dashboard(user_id, org_id):
    """Get dashboard data for a user - all integrations with their latest job stats"""
    try:
        # Get all integrations for the user with their latest job stats
        integrations_with_stats = db.get_user_integrations_with_stats(user_id, org_id)
        
        return jsonify({
            'success': True,
            'integrations': integrations_with_stats,
            'count': len(integrations_with_stats)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/integration/<int:integration_id>', methods=['GET'])
def get_integration_dashboard(integration_id):
    """Get complete dashboard data for a specific integration"""
    try:
        # Get complete dashboard data for the integration
        dashboard_data = db.get_dashboard_data(integration_id)
        
        if dashboard_data:
            return jsonify({
                'success': True,
                'dashboard_data': dashboard_data
            })
        else:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/extract/<int:integration_id>', methods=['POST'])
def extract_metadata_for_dashboard(integration_id):
    """Extract metadata for dashboard - triggers extraction and returns dashboard data"""
    try:
        # Get integration details
        integration = db.get_integration(integration_id)
        if not integration:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
        
        # Parse stored credentials using utility function
        credentials = parse_stored_credentials(integration['i_token'], integration['i_org_type'])
        
        if not credentials:
            return jsonify({'success': False, 'error': 'Invalid stored credentials format'}), 400
        
        # Create job ID for this extraction
        job_id = str(uuid.uuid4())
        
        # Initialize job
        extraction_jobs[job_id] = {
            'id': job_id,
            'status': 'starting',
            'progress': ['Starting metadata extraction for dashboard...'],
            'start_time': datetime.now(),
            'data': None,
            'error': None,
            'integration_id': integration_id  # Store integration ID for database storage
        }
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=extract_metadata_async_for_dashboard,
            args=(job_id, credentials, integration_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True, 
            'job_id': job_id,
            'message': 'Metadata extraction started for dashboard'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/job-status/<job_id>', methods=['GET'])
def get_dashboard_job_status(job_id):
    """Get the status of a dashboard extraction job"""
    if job_id not in extraction_jobs:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    job = extraction_jobs[job_id]
    
    response_data = {
        'success': True,
        'status': job['status'],
        'progress': job['progress'],
        'data': job.get('data'),
        'error': job.get('error')
    }
    
    # If job is complete, get dashboard data
    if job['status'] == 'success' and 'integration_id' in job:
        try:
            dashboard_data = db.get_dashboard_data(job['integration_id'])
            response_data['dashboard_data'] = dashboard_data
        except Exception as e:
            response_data['dashboard_error'] = str(e)
    
    # Calculate duration if job is complete
    if job['status'] in ['success', 'error'] and 'end_time' in job:
        duration = job['end_time'] - job['start_time']
        response_data['duration'] = str(duration).split('.')[0]  # Remove microseconds
    
    return jsonify(response_data)

@app.route('/api/metadata-from-integration/<int:integration_id>', methods=['GET'])
def get_metadata_from_integration(integration_id):
    """Get metadata using stored integration details without re-extraction"""
    try:
        # Get integration details
        integration = db.get_integration(integration_id)
        if not integration:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
        
        # Get the latest extraction job for this integration
        jobs = db.get_extraction_jobs_by_integration(integration_id)
        if not jobs:
            return jsonify({'success': False, 'error': 'No extraction jobs found for this integration'}), 404
        
        latest_job = jobs[0]  # Most recent job
        
        # Get metadata components for this job
        components = db.get_metadata_components_by_job(latest_job['aej_id'])
        
        # Get metadata statistics
        stats = db.get_metadata_stats_by_job(latest_job['aej_id'])
        
        return jsonify({
            'success': True,
            'integration': integration,
            'latest_job': latest_job,
            'metadata_components': components,
            'metadata_stats': stats,
            'total_components': len(components)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-components/<int:job_id>', methods=['GET'])
def get_metadata_components(job_id):
    """Get all metadata components for a specific extraction job"""
    try:
        components = db.get_metadata_components_by_job(job_id)
        
        return jsonify({
            'success': True,
            'components': components,
            'count': len(components)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-components/<int:job_id>/type/<metadata_type>', methods=['GET'])
def get_metadata_components_by_type(job_id, metadata_type):
    """Get metadata components for a specific job and metadata type"""
    try:
        # Get metadata type ID first
        metadata_types = db.get_metadata_types(org_id=409)
        type_mapping = {mt['amt_name']: mt['amt_id'] for mt in metadata_types}
        
        type_id = type_mapping.get(metadata_type)
        if not type_id:
            return jsonify({'success': False, 'error': f'Unknown metadata type: {metadata_type}'}), 400
        
        # Get components for this job and type
        components = db.get_metadata_components_by_job_and_type(job_id, type_id)
        
        return jsonify({
            'success': True,
            'components': components,
            'count': len(components),
            'metadata_type': metadata_type
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-components/<int:job_id>/type/<metadata_type>/search', methods=['GET'])
def search_metadata_components_by_type(job_id, metadata_type):
    """Search metadata components for a specific job and metadata type"""
    try:
        search_term = request.args.get('search_term', '')
        
        # Get metadata type ID first
        metadata_types = db.get_metadata_types(org_id=409)
        type_mapping = {mt['amt_name']: mt['amt_id'] for mt in metadata_types}
        
        type_id = type_mapping.get(metadata_type)
        if not type_id:
            return jsonify({'success': False, 'error': f'Unknown metadata type: {metadata_type}'}), 400
        
        # Search components for this job and type
        components = db.search_metadata_components_by_job_and_type(job_id, type_id, search_term)
        
        return jsonify({
            'success': True,
            'components': components,
            'count': len(components),
            'metadata_type': metadata_type,
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-component/<int:component_id>', methods=['GET'])
def get_metadata_component(component_id):
    """Get a specific metadata component"""
    try:
        component = db.get_metadata_component(component_id)
        
        if component:
            return jsonify({
                'success': True,
                'component': component
            })
        else:
            return jsonify({'success': False, 'error': 'Component not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-component/<int:component_id>/details', methods=['GET'])
def get_metadata_component_details(component_id):
    """Get detailed information for a metadata component including summary and dependencies"""
    try:
        # Get the component
        component = db.get_metadata_component(component_id)
        if not component:
            return jsonify({'success': False, 'error': 'Component not found'}), 404
        
        # Get dependencies for this component
        dependencies = db.get_dependencies_for_component(component_id)
        
        # Get AI summary (if available)
        ai_summary = component.get('amc_ai_summary', '')
        
        return jsonify({
            'success': True,
            'component': component,
            'dependencies': dependencies,
            'ai_summary': ai_summary,
            'content': component.get('amc_content', ''),
            'last_modified': component.get('amc_last_modified'),
            'created_timestamp': component.get('amc_created_timestamp')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-component/<int:component_id>/dependencies', methods=['GET'])
def get_metadata_component_dependencies(component_id):
    """Get dependencies for a metadata component"""
    try:
        dependencies = db.get_dependencies_for_component(component_id)
        
        return jsonify({
            'success': True,
            'dependencies': dependencies,
            'count': len(dependencies)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-component/<int:component_id>/content', methods=['GET'])
def get_metadata_component_content(component_id):
    """Get the content/XML for a metadata component"""
    try:
        component = db.get_metadata_component(component_id)
        
        if component:
            return jsonify({
                'success': True,
                'content': component.get('amc_content', ''),
                'component_name': component.get('amc_dev_name', ''),
                'metadata_type': component.get('metadata_type_name', '')
            })
        else:
            return jsonify({'success': False, 'error': 'Component not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-component/<int:component_id>/dependency-network', methods=['GET'])
def get_metadata_component_dependency_network(component_id):
    """Get dependency network data for diagram visualization"""
    try:
        # Get the component
        component = db.get_metadata_component(component_id)
        if not component:
            return jsonify({'success': False, 'error': 'Component not found'}), 404
        
        # Get dependencies for this component
        dependencies = db.get_dependencies_for_component(component_id)
        
        # Get all related components
        related_component_ids = set()
        for dep in dependencies:
            related_component_ids.add(dep['amd_from_component_id'])
            related_component_ids.add(dep['amd_to_component_id'])
        
        # Get component details for all related components
        components_data = {}
        for comp_id in related_component_ids:
            comp = db.get_metadata_component(comp_id)
            if comp:
                components_data[comp_id] = comp
        
        # Create network data for visualization
        nodes = []
        edges = []
        
        # Add all components as nodes
        for comp_id, comp_data in components_data.items():
            # Get metadata type name
            metadata_type_name = comp_data.get('metadata_type_name', 'Unknown')
            if not metadata_type_name:
                # Try to get from metadata type ID
                type_id = comp_data.get('amc_metadata_type_id')
                if type_id:
                    type_query = "SELECT amt_name FROM ids_audit_metadata_type WHERE amt_id = %s"
                    type_result = db.execute_query(type_query, (type_id,), fetch_one=True)
                    if type_result:
                        metadata_type_name = type_result['amt_name']
            
            nodes.append({
                'id': comp_data.get('amc_dev_name', 'Unknown'),
                'label': comp_data.get('amc_dev_name', 'Unknown'),
                'type': metadata_type_name,
                'isTarget': comp_id == component_id,
                'component_id': comp_id
            })
        
        # Add dependencies as edges
        for dep in dependencies:
            from_comp = components_data.get(dep['amd_from_component_id'])
            to_comp = components_data.get(dep['amd_to_component_id'])
            
            if from_comp and to_comp:
                edges.append({
                    'from': from_comp.get('amc_dev_name', 'Unknown'),
                    'to': to_comp.get('amc_dev_name', 'Unknown'),
                    'type': dep['amd_dependency_type'],
                    'description': dep['amd_description'],
                    'from_component_id': dep['amd_from_component_id'],
                    'to_component_id': dep['amd_to_component_id']
                })
        
        # Calculate statistics
        total_relationships = len(dependencies)
        incoming = len([d for d in dependencies if d['amd_to_component_id'] == component_id])
        outgoing = len([d for d in dependencies if d['amd_from_component_id'] == component_id])
        
        return jsonify({
            'success': True,
            'component': component,
            'network': {
                'nodes': nodes,
                'edges': edges
            },
            'relationships': dependencies,  # Add raw relationships for the frontend
            'stats': {
                'total_relationships': total_relationships,
                'incoming': incoming,
                'outgoing': outgoing
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metadata-component/<int:component_id>/generate-summary', methods=['POST'])
def generate_component_summary(component_id):
    """Generate AI summary for a metadata component on-demand"""
    try:
        # Get the component
        component = db.get_metadata_component(component_id)
        if not component:
            return jsonify({'success': False, 'error': 'Component not found'}), 404
        
        # Get component content
        content = component.get('amc_content', '')
        if not content:
            return jsonify({'success': False, 'error': 'No content available for this component'}), 400
        
        # Get filename for summary generation
        filename = component.get('amc_dev_name', 'Unknown')
        if component.get('metadata_type_name'):
            # Add file extension based on type
            type_name = component['metadata_type_name']
            if type_name == 'ApexClass':
                filename += '.cls'
            elif type_name == 'ApexTrigger':
                filename += '.trigger'
            elif type_name == 'CustomObject':
                filename += '.object'
            elif type_name == 'Flow':
                filename += '.flow'
            elif type_name == 'Layout':
                filename += '.layout'
        
        # Generate AI summary
        ai_summary = generate_metadata_summary(filename, content)
        
        # Update the component with the new AI summary
        success = db.update_metadata_component(
            component_id=component_id,
            ai_summary=ai_summary,
            ai_model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            last_updated_user_id=243
        )
        
        if success:
            return jsonify({
                'success': True,
                'summary': ai_summary,
                'message': 'AI summary generated and stored successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update component with AI summary'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/extract-metadata-with-login', methods=['POST'])
def extract_metadata_with_login():
    """API endpoint to start metadata extraction with login verification"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'password', 'is_sandbox', 'output_dir']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        username = data['username']
        password = data['password'] 
        security_token = data.get('security_token', '')
        is_sandbox = data['is_sandbox']
        output_dir = data['output_dir']
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job WITHOUT login success message
        extraction_jobs[job_id] = {
            'id': job_id,
            'status': 'starting',
            'progress': ['Initializing metadata extraction...'],
            'start_time': datetime.now(),
            'data': None,
            'error': None
        }
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=extract_metadata_async,
            args=(job_id, username, password, security_token, is_sandbox, output_dir)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'job_id': job_id, 'message': 'Starting extraction'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/extract-metadata', methods=['POST'])
def extract_metadata_api():
    """API endpoint to start metadata extraction"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'password', 'is_sandbox', 'output_dir']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        username = data['username']
        password = data['password'] 
        security_token = data.get('security_token', '')
        is_sandbox = data['is_sandbox']
        output_dir = data['output_dir']
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job
        extraction_jobs[job_id] = {
            'id': job_id,
            'status': 'starting',
            'progress': ['Initializing extraction process...'],
            'start_time': datetime.now(),
            'data': None,
            'error': None
        }
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=extract_metadata_async,
            args=(job_id, username, password, security_token, is_sandbox, output_dir)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'job_id': job_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status of an extraction job"""
    if job_id not in extraction_jobs:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    job = extraction_jobs[job_id]
    
    response_data = {
        'success': True,
        'status': job['status'],
        'progress': job['progress'],
        'data': job.get('data'),
        'error': job.get('error')
    }
    
    # Calculate duration if job is complete
    if job['status'] in ['success', 'error'] and 'end_time' in job:
        duration = job['end_time'] - job['start_time']
        response_data['duration'] = str(duration).split('.')[0]  # Remove microseconds
    
    return jsonify(response_data)

@app.route('/api/metadata-files/<job_id>/<metadata_type>', methods=['GET'])
def get_metadata_files(job_id, metadata_type):
    """Get list of files for a specific metadata type"""
    if job_id not in extraction_jobs:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    job = extraction_jobs[job_id]
    if job['status'] != 'success':
        return jsonify({'success': False, 'error': 'Job not completed successfully'}), 400
    
    try:
        # Get the output directory from job data
        if 'data' not in job or not job['data'] or 'outputPath' not in job['data']:
            return jsonify({'success': False, 'error': 'Output path not found'}), 404
        
        output_path = job['data']['outputPath']
        
        # Map metadata types to directory names
        type_to_directory = {
            'Apex Classes': 'classes',
            'Apex Triggers': 'triggers', 
            'Custom Objects': 'objects',
            'Flows': 'flows',
            'Layouts': 'layouts'
        }
        
        directory_name = type_to_directory.get(metadata_type)
        if not directory_name:
            return jsonify({'success': False, 'error': f'Unknown metadata type: {metadata_type}'}), 400
        
        # Look for the directory in the extracted files
        files_list = []
        
        for root, dirs, files in os.walk(output_path):
            folder_name = os.path.basename(root).lower()
            
            if directory_name in folder_name:
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        files_list.append({
                            'name': file,
                            'path': os.path.relpath(file_path, output_path),
                            'size': stat.st_size,
                            'lastModified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except OSError:
                        # Skip files that can't be accessed
                        files_list.append({
                            'name': file,
                            'path': os.path.relpath(file_path, output_path),
                            'size': 0,
                            'lastModified': None
                        })
        
        # Sort files by name
        files_list.sort(key=lambda x: x['name'])
        
        return jsonify({
            'success': True,
            'files': files_list,
            'metadata_type': metadata_type,
            'total_files': len(files_list)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error listing files: {str(e)}'}), 500

# ============================================================================
# METADATA EXTRACTION FUNCTIONS (from original server.py)
# ============================================================================

def extract_metadata_corrected(job_id, session_id, metadata_url, output_dir):
    """Extract metadata using COMPREHENSIVE extraction for ALL metadata types"""
    job = extraction_jobs[job_id]
    
    try:
        # Use the comprehensive metadata extraction function
        retrieve_body = get_comprehensive_metadata_retrieve_body(session_id)
        
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'retrieve'
        }
        
        job['progress'].append('Submitting retrieve request for ALL metadata types...')
        
        response = requests.post(metadata_url, data=retrieve_body, headers=headers, timeout=300)  # 5 minutes timeout for comprehensive extraction
        
        if response.status_code != 200:
            job['status'] = 'error'
            job['error'] = f"Retrieve failed: {response.status_code}"
            return False
        
        response_text = response.text
        
        # Check for faults
        if '<soapenv:Fault>' in response_text:
            fault_match = re.search(r'<faultstring>(.*?)</faultstring>', response_text)
            job['status'] = 'error'
            job['error'] = fault_match.group(1) if fault_match else "Unknown SOAP fault"
            return False
        
        # Extract async ID
        id_match = re.search(r'<id>(.*?)</id>', response_text)
        if not id_match:
            job['status'] = 'error'
            job['error'] = "No async ID found in response"
            return False
        
        async_id = id_match.group(1)
        job['progress'].append(f'Job ID: {async_id}')
        
        # Check if immediately done
        done_match = re.search(r'<done>(.*?)</done>', response_text)
        if done_match and done_match.group(1).lower() == 'true':
            job['progress'].append('Job completed immediately!')
            return download_and_extract(job_id, response_text, output_dir)
        
        # Poll for completion
        return poll_and_download_corrected(job_id, session_id, metadata_url, async_id, output_dir)
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = f"Retrieve exception: {str(e)}"
        return False

def poll_and_download_corrected(job_id, session_id, metadata_url, async_id, output_dir):
    """Poll for completion and download when ready - INCREASED TIMEOUT FOR COMPREHENSIVE EXTRACTION"""
    job = extraction_jobs[job_id]
    
    check_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{session_id}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:checkRetrieveStatus>
         <met:asyncProcessId>{async_id}</met:asyncProcessId>
      </met:checkRetrieveStatus>
   </soapenv:Body>
</soapenv:Envelope>'''
    
    headers = {
        'Content-Type': 'text/xml; charset=UTF-8',
        'SOAPAction': 'checkRetrieveStatus'
    }
    
    job['progress'].append('Polling for completion (comprehensive extraction - this may take 15-30 minutes)...')
    
    # INCREASED TIMEOUT: 60 attempts × 60 seconds = 60 minutes max
    max_attempts = 60  # Increased from 15 to 60
    for i in range(max_attempts):
        time.sleep(60)  # Increased from 30 to 60 seconds
        job['progress'].append(f'Checking status... ({i+1}/{max_attempts}) - Comprehensive extraction in progress')
        
        try:
            response = requests.post(metadata_url, data=check_body, headers=headers, timeout=180)  # Increased timeout to 3 minutes
            
            if response.status_code != 200:
                job['progress'].append(f'Status check failed: {response.status_code}')
                continue
            
            response_text = response.text
            
            # Check for critical errors first
            if 'INVALID_LOCATOR' in response_text:
                job['status'] = 'error'
                job['error'] = 'Result expired! The retrieve result was deleted by Salesforce.'
                return False
            
            if '<soapenv:Fault>' in response_text:
                fault_match = re.search(r'<faultstring>(.*?)</faultstring>', response_text)
                job['status'] = 'error'
                job['error'] = fault_match.group(1) if fault_match else "Unknown fault"
                return False
            
            # Check if done
            done_match = re.search(r'<done>(.*?)</done>', response_text)
            if done_match and done_match.group(1).lower() == 'true':
                job['progress'].append('✅ Job completed! Downloading immediately...')
                return download_and_extract(job_id, response_text, output_dir)
            
            # Show current state
            state_match = re.search(r'<state>(.*?)</state>', response_text)
            if state_match:
                job['progress'].append(f'Current state: {state_match.group(1)}')
            
        except requests.exceptions.Timeout:
            job['progress'].append('Request timed out, retrying...')
        except Exception as e:
            job['progress'].append(f'Error: {str(e)}')
            continue
    
    job['status'] = 'error'
    job['error'] = 'Timed out waiting for completion (60 minutes) - Comprehensive extraction may take longer'
    return False

def download_and_extract(job_id, response_text, output_dir):
    """Download and extract the metadata zip and store in database"""
    job = extraction_jobs[job_id]
    
    try:
        # Verify success
        success_match = re.search(r'<success>(.*?)</success>', response_text)
        if success_match and success_match.group(1).lower() == 'false':
            job['status'] = 'error'
            job['error'] = 'Retrieve operation was not successful'
            # Look for error messages
            messages = re.findall(r'<message>(.*?)</message>', response_text)
            for msg in messages:
                job['progress'].append(f'Error message: {msg}')
            return False
        
        # Extract zip file content
        zip_match = re.search(r'<zipFile>(.*?)</zipFile>', response_text, re.DOTALL)
        if not zip_match:
            job['status'] = 'error'
            job['error'] = 'No zip file found in response'
            return False
        
        zip_b64 = zip_match.group(1).strip()
        
        job['progress'].append('Decoding and extracting zip file...')
        zip_data = base64.b64decode(zip_b64)
        job['progress'].append(f'Zip file size: {len(zip_data):,} bytes')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save zip file
        zip_path = os.path.join(output_dir, 'metadata.zip')
        with open(zip_path, 'wb') as f:
            f.write(zip_data)
        job['progress'].append(f'Zip saved: {zip_path}')
        
        # Extract files
        extract_dir = os.path.join(output_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        job['progress'].append('Extracting files...')
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(extract_dir)
        
        # Count and analyze extracted files
        metadata_stats = analyze_extracted_metadata(extract_dir)
        
        # Store metadata components in database
        job['progress'].append('Storing metadata components in database...')
        store_metadata_components_in_db(job_id, extract_dir, metadata_stats)
        
        job['progress'].append('Successfully extracted {total_files} files!'.format(total_files=metadata_stats["totalFiles"]))
        job['progress'].append(f'Output directory: {os.path.abspath(extract_dir)}')
        
        job['status'] = 'success'
        job['data'] = metadata_stats
        job['end_time'] = datetime.now()
        
        return True
        
    except zipfile.BadZipFile:
        job['status'] = 'error'
        job['error'] = 'Received invalid zip file'
        return False
    except Exception as e:
        job['status'] = 'error'
        job['error'] = f'Error processing zip: {str(e)}'
        return False

def extract_metadata_async_for_dashboard(job_id, credentials, integration_id):
    """Extract metadata for dashboard using stored integration - NO LOCAL FILES"""
    job = extraction_jobs[job_id]
    
    try:
        # Step 1: Login using stored credentials
        session_id, server_url, error = login_to_salesforce(
            credentials['username'],
            credentials['password'],
            credentials.get('security_token', ''),
            credentials['is_sandbox']
        )
        
        if error:
            job['status'] = 'error'
            job['error'] = error
            return
        
        # Step 2: Extract metadata
        job['progress'].append('Preparing metadata extraction...')
        metadata_url = server_url.replace('/services/Soap/c/', '/services/Soap/m/')
        
        # Extract metadata directly to memory (no local files)
        success = extract_metadata_to_database(job_id, session_id, metadata_url, integration_id)
        
        if not success and job['status'] != 'success':
            if job['status'] != 'error':
                job['status'] = 'error'
                job['error'] = 'Failed to extract metadata'
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = f'Extraction process failed: {str(e)}'

def store_metadata_components_in_db(job_id, extract_dir, metadata_stats):
    """Store extracted metadata components in the database WITHOUT AI summaries (generated on-demand)"""
    job = extraction_jobs[job_id]
    
    try:
        # Get metadata types for mapping
        metadata_types = db.get_metadata_types(org_id=409)
        type_mapping = {mt['amt_name']: mt['amt_id'] for mt in metadata_types}
        
        # Get the integration ID from the job
        integration_id = job.get('integration_id', 4)  # Default fallback
        
        # Create extraction job in database if it doesn't exist
        db_job_id = db.create_extraction_job(
            org_id=409,
            integration_id=integration_id,
            job_status="completed",
            total_files=metadata_stats["totalFiles"],
            created_user_id=243
        )
        
        if not db_job_id:
            job['progress'].append('Warning: Failed to create extraction job in database')
            return
        
        # Update job with completion data
        db.update_extraction_job(
            job_id=db_job_id,
            job_status="completed",
            completed_at=datetime.now(),
            total_files=metadata_stats["totalFiles"],
            job_data=metadata_stats
        )
        
        components_stored = 0
        dependencies_stored = 0
        
        # Store all components first
        component_map = {}  # Map filename to component_id for dependency creation
        
        # Process each file and store in database
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Determine metadata type
                metadata_type = get_file_type_from_path(file_path)
                type_id = type_mapping.get(metadata_type)
                
                if not type_id:
                    continue  # Skip unknown types
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Create metadata component in database WITHOUT AI summary
                    component_id = db.create_metadata_component(
                        org_id=409,
                        integration_id=integration_id,
                        extraction_job_id=db_job_id,
                        metadata_type_id=type_id,
                        label=file,
                        dev_name=file.replace('.cls', '').replace('.trigger', '').replace('.object', '').replace('.flow', '').replace('.layout', ''),
                        notes=f"Extracted from {file_path}",
                        content=content,
                        ai_summary=None,  # No AI summary during extraction
                        ai_model=None,     # No AI model during extraction
                        last_modified=datetime.fromtimestamp(os.path.getmtime(file_path)),
                        api_version="62.0",
                        created_user_id=243
                    )
                    
                    if component_id:
                        components_stored += 1
                        component_map[file] = component_id
                    
                except Exception as e:
                    job['progress'].append(f'Warning: Failed to store component {file}: {str(e)}')
                    continue
        
        # Now analyze and store dependencies
        job['progress'].append('Analyzing dependencies between components...')
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file not in component_map:
                    continue
                
                source_component_id = component_map[file]
                
                # Analyze dependencies based on file type
                dependencies = []
                
                if file.endswith('.cls'):
                    dependencies = analyze_apex_class_dependencies(file_path, file, component_map)
                elif file.endswith('.trigger'):
                    dependencies = analyze_apex_trigger_dependencies(file_path, file, component_map)
                elif file.endswith('.object'):
                    dependencies = analyze_custom_object_dependencies(file_path, file, component_map)
                elif file.endswith('.flow'):
                    dependencies = analyze_flow_dependencies(file_path, file, component_map)
                elif file.endswith('.layout'):
                    dependencies = analyze_layout_dependencies(file_path, file, component_map)
                
                # Store dependencies in database
                for dep in dependencies:
                    try:
                        dependency_id = db.create_dependency(
                            org_id=409,
                            from_component_id=source_component_id,
                            to_component_id=dep['to_component_id'],
                            dependency_type=dep['type'],
                            description=dep['description'],
                            created_user_id=243
                        )
                        if dependency_id:
                            dependencies_stored += 1
                    except Exception as e:
                        job['progress'].append(f'Warning: Failed to store dependency: {str(e)}')
                        continue
        
        job['progress'].append(f'Stored {components_stored} metadata components and {dependencies_stored} dependencies in database')
        
    except Exception as e:
        job['progress'].append(f'Error storing metadata in database: {str(e)}')

def get_file_type_from_path(file_path):
    """Determine metadata type from file path - COMPREHENSIVE VERSION"""
    filename = os.path.basename(file_path)
    
    # Apex and Visualforce
    if filename.endswith('.cls'):
        return "ApexClass"
    elif filename.endswith('.trigger'):
        return "ApexTrigger"
    elif filename.endswith('.page'):
        return "ApexPage"
    elif filename.endswith('.component'):
        return "ApexComponent"
    
    # Custom Objects and Fields
    elif filename.endswith('.object'):
        return "CustomObject"
    elif filename.endswith('.field'):
        return "CustomField"
    
    # Automation and Workflow
    elif filename.endswith('.flow'):
        return "Flow"
    elif filename.endswith('.workflow'):
        return "WorkflowRule"
    elif filename.endswith('.workflowAlert'):
        return "WorkflowAlert"
    elif filename.endswith('.workflowFieldUpdate'):
        return "WorkflowFieldUpdate"
    elif filename.endswith('.workflowTask'):
        return "WorkflowTask"
    elif filename.endswith('.workflowSend'):
        return "WorkflowSend"
    elif filename.endswith('.workflowOutboundMessage'):
        return "WorkflowOutboundMessage"
    elif filename.endswith('.workflowKnowledgePublish'):
        return "WorkflowKnowledgePublish"
    
    # UI and Layout
    elif filename.endswith('.layout'):
        return "Layout"
    elif filename.endswith('.flexipage'):
        return "FlexiPage"
    elif filename.endswith('.tab'):
        return "CustomTab"
    elif filename.endswith('.app'):
        return "CustomApplication"
    elif filename.endswith('.weblink'):
        return "CustomWebLink"
    elif filename.endswith('.quickAction'):
        return "QuickAction"
    
    # Validation and Rules
    elif filename.endswith('.validationRule'):
        return "ValidationRule"
    elif filename.endswith('.sharingRules'):
        return "SharingRules"
    elif filename.endswith('.sharingSet'):
        return "SharingSet"
    
    # Security and Permissions
    elif filename.endswith('.permissionset'):
        return "PermissionSet"
    elif filename.endswith('.profile'):
        return "Profile"
    elif filename.endswith('.role'):
        return "Role"
    elif filename.endswith('.group'):
        return "Group"
    elif filename.endswith('.queue'):
        return "Queue"
    elif filename.endswith('.customPermission'):
        return "CustomPermission"
    
    # Custom Metadata and Labels
    elif filename.endswith('.customMetadata'):
        return "CustomMetadata"
    elif filename.endswith('.labels'):
        return "CustomLabel"
    
    # Sites and Communities
    elif filename.endswith('.site'):
        return "CustomSite"
    elif filename.endswith('.network'):
        return "Network"
    elif filename.endswith('.networkBranding'):
        return "NetworkBranding"
    elif filename.endswith('.networkMemberGroup'):
        return "NetworkMemberGroup"
    elif filename.endswith('.networkPageOverride'):
        return "NetworkPageOverride"
    elif filename.endswith('.networkTabSet'):
        return "NetworkTabSet"
    
    # Reports and Analytics
    elif filename.endswith('.report'):
        return "Report"
    elif filename.endswith('.reportType'):
        return "ReportType"
    elif filename.endswith('.dashboard'):
        return "Dashboard"
    elif filename.endswith('.listView'):
        return "ListView"
    
    # Einstein Analytics (Wave)
    elif filename.endswith('.waveApplication'):
        return "WaveApplication"
    elif filename.endswith('.waveDashboard'):
        return "WaveDashboard"
    elif filename.endswith('.waveDataflow'):
        return "WaveDataflow"
    elif filename.endswith('.waveDataset'):
        return "WaveDataset"
    elif filename.endswith('.waveLens'):
        return "WaveLens"
    elif filename.endswith('.waveRecipe'):
        return "WaveRecipe"
    elif filename.endswith('.waveSpoke'):
        return "WaveSpoke"
    elif filename.endswith('.waveXmd'):
        return "WaveXmd"
    
    # Global Value Sets
    elif filename.endswith('.globalValueSet'):
        return "GlobalValueSet"
    elif filename.endswith('.globalValueSetTranslation'):
        return "GlobalValueSetTranslation"
    elif filename.endswith('.standardValueSet'):
        return "StandardValueSet"
    elif filename.endswith('.standardValueSetTranslation'):
        return "StandardValueSetTranslation"
    
    # Home Page Components
    elif filename.endswith('.homePageComponent'):
        return "HomePageComponent"
    elif filename.endswith('.homePageLayout'):
        return "HomePageLayout"
    
    # Named Credentials and Integrations
    elif filename.endswith('.namedCredential'):
        return "NamedCredential"
    elif filename.endswith('.samlSsoConfig'):
        return "SamlSsoConfig"
    
    # Documents and Resources
    elif filename.endswith('.document'):
        return "Document"
    elif filename.endswith('.resource'):
        return "StaticResource"
    elif filename.endswith('.email'):
        return "EmailTemplate"
    
    # Territory Management
    elif filename.endswith('.territory'):
        return "Territory"
    elif filename.endswith('.territory2'):
        return "Territory2"
    elif filename.endswith('.territory2Model'):
        return "Territory2Model"
    elif filename.endswith('.territory2Rule'):
        return "Territory2Rule"
    elif filename.endswith('.territory2Type'):
        return "Territory2Type"
    
    # Platform Events
    elif filename.endswith('.platformEventChannel'):
        return "PlatformEventChannel"
    elif filename.endswith('.platformEventChannelMember'):
        return "PlatformEventChannelMember"
    
    # Service and Support
    elif filename.endswith('.serviceChannel'):
        return "ServiceChannel"
    elif filename.endswith('.servicePresenceStatus'):
        return "ServicePresenceStatus"
    elif filename.endswith('.skill'):
        return "Skill"
    
    # Queue Routing
    elif filename.endswith('.queueRoutingConfig'):
        return "QueueRoutingConfig"
    
    # Path Assistant
    elif filename.endswith('.pathAssistant'):
        return "PathAssistant"
    
    # Permission Set Groups
    elif filename.endswith('.permissionSetGroup'):
        return "PermissionSetGroup"
    
    # Post Templates
    elif filename.endswith('.postTemplate'):
        return "PostTemplate"
    
    # Profile Settings
    elif filename.endswith('.profilePasswordPolicy'):
        return "ProfilePasswordPolicy"
    elif filename.endswith('.profileSessionSetting'):
        return "ProfileSessionSetting"
    
    # Topics
    elif filename.endswith('.topicsForObjects'):
        return "TopicsForObjects"
    
    # User Criteria and Searches
    elif filename.endswith('.userCriteria'):
        return "UserCriteria"
    elif filename.endswith('.userProfileSearch'):
        return "UserProfileSearch"
    
    # Custom Object Translations
    elif filename.endswith('.customObjectTranslation'):
        return "CustomObjectTranslation"
    elif filename.endswith('.customPageWebLink'):
        return "CustomPageWebLink"
    elif filename.endswith('.customTabTranslation'):
        return "CustomTabTranslation"
    
    # Installed Packages
    elif filename.endswith('.installedPackage'):
        return "InstalledPackage"
    
    # Synonym Dictionary
    elif filename.endswith('.synonymDictionary'):
        return "SynonymDictionary"
    
    # Site Dot Com
    elif filename.endswith('.siteDotCom'):
        return "SiteDotCom"
    
    else:
        return "Unknown"

def analyze_extracted_metadata(extract_dir):
    """Analyze the extracted metadata and return statistics"""
    metadata_types = {
        'classes': {'count': 0, 'icon': '⚡', 'description': 'Custom business logic and controllers'},
        'triggers': {'count': 0, 'icon': '🔄', 'description': 'Event-driven code execution'},
        'objects': {'count': 0, 'icon': '📦', 'description': 'Custom data structures and fields'},
        'flows': {'count': 0, 'icon': '🔀', 'description': 'Business process automation'},
        'layouts': {'count': 0, 'icon': '📋', 'description': 'Page and record layouts'}
    }
    
    total_files = 0
    
    for root, dirs, files in os.walk(extract_dir):
        total_files += len(files)
        
        # Count by directory
        folder_name = os.path.basename(root).lower()
        if 'classes' in folder_name:
            metadata_types['classes']['count'] += len([f for f in files if f.endswith('.cls')])
        elif 'triggers' in folder_name:
            metadata_types['triggers']['count'] += len([f for f in files if f.endswith('.trigger')])
        elif 'objects' in folder_name:
            metadata_types['objects']['count'] += len([f for f in files if f.endswith('.object')])
        elif 'flows' in folder_name:
            metadata_types['flows']['count'] += len([f for f in files if f.endswith('.flow')])
        elif 'layouts' in folder_name:
            metadata_types['layouts']['count'] += len([f for f in files if f.endswith('.layout')])
    
    return {
        'totalFiles': total_files,
        'outputPath': extract_dir,
        'types': [
            {
                'type': 'Apex Classes',
                'count': metadata_types['classes']['count'],
                'icon': metadata_types['classes']['icon'],
                'description': metadata_types['classes']['description']
            },
            {
                'type': 'Apex Triggers', 
                'count': metadata_types['triggers']['count'],
                'icon': metadata_types['triggers']['icon'],
                'description': metadata_types['triggers']['description']
            },
            {
                'type': 'Custom Objects',
                'count': metadata_types['objects']['count'], 
                'icon': metadata_types['objects']['icon'],
                'description': metadata_types['objects']['description']
            },
            {
                'type': 'Flows',
                'count': metadata_types['flows']['count'],
                'icon': metadata_types['flows']['icon'], 
                'description': metadata_types['flows']['description']
            },
            {
                'type': 'Layouts',
                'count': metadata_types['layouts']['count'],
                'icon': metadata_types['layouts']['icon'],
                'description': metadata_types['layouts']['description']
            }
        ]
    }

def generate_metadata_summary(filename, content):
    """Generate AI summary for metadata using Together AI API"""
    
    try:
        # Together AI API configuration
        api_key = "tgp_v1_0qJtM3IFwIU9vDaSYfNQ3E62KAhRs5AqniMH2jfU69c"
        
        # Create prompt based on file type
        prompt = create_metadata_prompt(filename, content)
        
        # Call the Together AI API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 400
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get("choices", [{}])[0].get("text", "").strip()
            return summary if summary else "Unable to generate summary for this file."
        else:
            return "Error generating AI summary. Please try again later."
        
    except Exception as e:
        return "Error generating summary due to an exception."

def create_metadata_prompt(filename, content):
    """Create an appropriate prompt based on the metadata file type"""
    
    file_type = get_file_type_from_path(filename)
    
    if file_type == "ApexClass":
        return f"""<s>[INST] You are an expert Salesforce developer. Analyze this Apex class and provide a concise summary.

File: {filename}

Here is the Apex class code:
{content[:2000]}

Please provide a summary that includes:
1. What this class does (main purpose)
2. Key methods and their functionality
3. Any design patterns or integrations
4. Business value or use case

Keep the summary concise but informative (150-250 words).
[/INST]</s>

"""
    
    elif file_type == "ApexTrigger":
        return f"""<s>[INST] You are an expert Salesforce developer. Analyze this Apex trigger and provide a concise summary.

File: {filename}

Here is the trigger code:
{content[:2000]}

Please provide a summary that includes:
1. What object this trigger operates on
2. Which trigger events it handles (before/after insert/update/delete)
3. What business logic it implements
4. Any integrations or external calls
5. Potential impact on data operations

Keep the summary concise but informative (150-250 words).
[/INST]</s>

"""
    
    elif file_type == "CustomObject":
        return f"""<s>[INST] You are an expert Salesforce admin. Analyze this custom object definition and provide a concise summary.

File: {filename}

Here is the custom object XML:
{content[:2000]}

Please provide a summary that includes:
1. What business entity this object represents
2. Key custom fields and their purposes
3. Relationships to other objects
4. Any special configurations (validation rules, workflows, etc.)
5. Business use case and value

Keep the summary concise but informative (150-250 words).
[/INST]</s>

"""
    else:
        return f"""<s>[INST] You are an expert Salesforce developer/admin. Analyze this Salesforce metadata file and provide a concise summary.

File: {filename}
File Type: {file_type}

Here is the metadata content:
{content[:2000]}

Please provide a summary that includes:
1. What this metadata component does
2. Its role in the Salesforce org
3. Key configurations or settings
4. Business value or use case
5. How it might interact with other components

Keep the summary concise but informative (150-250 words).
[/INST]</s>

"""

def analyze_apex_class_dependencies(file_path, filename, component_map):
    """Analyze Apex class for dependencies"""
    dependencies = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        source_name = filename.replace('.cls', '')
        
        # SOQL queries
        soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
        for match in re.finditer(soql_pattern, content):
            obj_name = match.group(1)
            if '_' in obj_name and not obj_name.endswith('__c'):
                obj_name = f"{obj_name}__c"
            
            # Find the component ID for this object
            target_component_id = find_component_id_by_name(obj_name, component_map)
            if target_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'soql_query',
                    'description': f'{source_name} queries {obj_name}'
                })
        
        # DML operations
        dml_pattern = r'(?i)(insert|update|delete|upsert|merge)\s+(\w+)'
        for match in re.finditer(dml_pattern, content):
            var_name = match.group(2)
            if var_name.lower() not in ['list', 'set', 'map', 'string', 'integer', 'boolean']:
                target_component_id = find_component_id_by_name(var_name, component_map)
                if target_component_id:
                    dependencies.append({
                        'to_component_id': target_component_id,
                        'type': 'dml_operation',
                        'description': f'{source_name} performs {match.group(1)} on {var_name}'
                    })
        
    except Exception as e:
        print(f"Error analyzing Apex class {filename}: {str(e)}")
    
    return dependencies

def analyze_apex_trigger_dependencies(file_path, filename, component_map):
    """Analyze Apex trigger for dependencies"""
    dependencies = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        source_name = filename.replace('.trigger', '')
        
        # Extract object the trigger is on
        object_match = re.search(r'trigger\s+\w+\s+on\s+(\w+)', content, re.IGNORECASE)
        if object_match:
            obj_name = object_match.group(1)
            target_component_id = find_component_id_by_name(obj_name, component_map)
            if target_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'trigger_on_object',
                    'description': f'{source_name} trigger operates on {obj_name}'
                })
        
    except Exception as e:
        print(f"Error analyzing trigger {filename}: {str(e)}")
    
    return dependencies

def analyze_custom_object_dependencies(file_path, filename, component_map):
    """Analyze custom object for dependencies"""
    dependencies = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        source_name = filename.replace('.object', '')
        
        # Define namespace for Salesforce metadata
        ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
        
        # Find field relationships
        for field_elem in root.findall('.//sf:fields', ns):
            field_name_elem = field_elem.find('sf:fullName', ns)
            ref_to_elem = field_elem.find('sf:referenceTo', ns)
            type_elem = field_elem.find('sf:type', ns)
            
            if field_name_elem is not None and ref_to_elem is not None:
                field_name = field_name_elem.text
                ref_to = ref_to_elem.text
                field_type = type_elem.text if type_elem is not None else None
                
                # Look for reference relationships
                if ref_to and field_type in ['Lookup', 'MasterDetail']:
                    target_component_id = component_map.get(ref_to)
                    if target_component_id and target_component_id != source_component_id:
                        dependencies.append({
                            'to_component_id': target_component_id,
                            'type': 'object_reference',
                            'description': f'{source_name} has {field_type} field referencing {ref_to}'
                        })
        
    except Exception as e:
        print(f"Error analyzing object {filename}: {str(e)}")
    
    return dependencies

def analyze_flow_dependencies(file_path, filename, component_map):
    """Analyze flow for dependencies"""
    dependencies = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        source_name = filename.replace('.flow', '')
        
        # Define namespace for Salesforce metadata
        ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
        
        # Find object references
        for obj_elem in root.findall('.//sf:object', ns):
            if obj_elem.text:
                obj_name = obj_elem.text
                target_component_id = component_map.get(obj_name)
                if target_component_id:
                    dependencies.append({
                        'to_component_id': target_component_id,
                        'type': 'flow_object_reference',
                        'description': f'{source_name} flow uses {obj_name}'
                    })
        
    except Exception as e:
        print(f"Error analyzing flow {filename}: {str(e)}")
    
    return dependencies

def analyze_layout_dependencies(file_path, filename, component_map):
    """Analyze layout for dependencies"""
    dependencies = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        source_name = filename.replace('.layout', '')
        
        # Extract object name from layout name
        object_name = source_name.split('-')[0] if '-' in source_name else None
        
        if object_name:
            target_component_id = find_component_id_by_name(object_name, component_map)
            if target_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'layout_for_object',
                    'description': f'{source_name} is a layout for {object_name}'
                })
        
    except Exception as e:
        print(f"Error analyzing layout {filename}: {str(e)}")
    
    return dependencies

def find_component_id_by_name(name, component_map):
    """Find component ID by name in the component map"""
    for filename, component_id in component_map.items():
        dev_name = filename.replace('.cls', '').replace('.trigger', '').replace('.object', '').replace('.flow', '').replace('.layout', '')
        if dev_name == name:
            return component_id
    return None

def extract_metadata_async(job_id, username, password, security_token, is_sandbox, output_dir):
    """Main async extraction workflow"""
    job = extraction_jobs[job_id]
    
    try:
        # Step 1: Login (silently, no progress message)
        session_id, server_url, error = login_to_salesforce(username, password, security_token, is_sandbox)
        
        if error:
            job['status'] = 'error'
            job['error'] = error
            return
        
        # Step 2: Extract metadata
        job['progress'].append('Preparing metadata extraction...')
        metadata_url = server_url.replace('/services/Soap/c/', '/services/Soap/m/')
        
        success = extract_metadata_corrected(job_id, session_id, metadata_url, output_dir)
        
        if not success and job['status'] != 'success':
            if job['status'] != 'error':
                job['status'] = 'error'
                job['error'] = 'Failed to extract metadata'
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = f'Extraction process failed: {str(e)}'

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = db.get_connection()
        db_status = "connected" if conn and not conn.closed else "disconnected"
        
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.now().isoformat(),
            'database': db_status
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'error',
            'error': str(e)
        }), 500

# ============================================================================
# MYLIST MANAGEMENT API ENDPOINTS
# ============================================================================

@app.route('/api/mylists', methods=['POST'])
def create_mylist():
    """Create a new MyList"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['org_id', 'user_id', 'integration_id', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create MyList in database
        list_id = db.create_mylist(
            org_id=data['org_id'],
            user_id=data['user_id'],
            integration_id=data['integration_id'],
            name=data['name'],
            description=data.get('description', ''),
            notes=data.get('notes', ''),
            created_user_id=data.get('created_user_id', data['user_id'])
        )
        
        if list_id:
            return jsonify({
                'success': True,
                'list_id': list_id,
                'message': 'MyList created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create MyList'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mylists/user/<int:user_id>/org/<int:org_id>', methods=['GET'])
def get_user_mylists(user_id, org_id):
    """Get all MyLists for a user"""
    try:
        mylists = db.get_mylists_by_user(user_id, org_id)
        
        return jsonify({
            'success': True,
            'mylists': mylists,
            'count': len(mylists)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mylists/<int:list_id>', methods=['GET'])
def get_mylist(list_id):
    """Get MyList by ID"""
    try:
        mylist = db.get_mylist(list_id)
        
        if mylist:
            return jsonify({
                'success': True,
                'mylist': mylist
            })
        else:
            return jsonify({'success': False, 'error': 'MyList not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mylists/<int:list_id>/components', methods=['GET'])
def get_mylist_components(list_id):
    """Get all components in a MyList"""
    try:
        components = db.get_list_components(list_id)
        
        # Convert components to dictionaries to ensure proper JSON serialization
        serialized_components = []
        for component in components:
            # Convert to dict and handle None values
            component_dict = {}
            for key, value in component.items():
                if value is None:
                    component_dict[key] = None
                elif isinstance(value, (datetime, date)):
                    component_dict[key] = value.isoformat()
                else:
                    component_dict[key] = value
            serialized_components.append(component_dict)
        
        return jsonify({
            'success': True,
            'components': serialized_components,
            'count': len(serialized_components)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mylists/<int:list_id>/components', methods=['POST'])
def add_component_to_mylist(list_id):
    """Add a metadata component to a MyList"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['org_id', 'component_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Add component to list
        mapping_id = db.add_component_to_list(
            org_id=data['org_id'],
            list_id=list_id,
            component_id=data['component_id'],
            notes=data.get('notes', ''),
            created_user_id=data.get('created_user_id', 243)
        )
        
        if mapping_id:
            return jsonify({
                'success': True,
                'mapping_id': mapping_id,
                'message': 'Component added to MyList successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add component to MyList'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mylists/<int:list_id>/components/<int:component_id>', methods=['DELETE'])
def remove_component_from_mylist(list_id, component_id):
    """Remove a metadata component from a MyList"""
    try:
        # Remove component from list
        db.remove_component_from_list(list_id, component_id)
        
        return jsonify({
            'success': True,
            'message': 'Component removed from MyList successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mylists/<int:list_id>/dependency-network', methods=['GET'])
def get_mylist_dependency_network(list_id):
    """Get dependency network for all components in a MyList"""
    try:
        # Get the MyList
        mylist = db.get_mylist(list_id)
        if not mylist:
            return jsonify({'success': False, 'error': 'MyList not found'}), 404
        
        # Get components in the list
        components = db.get_list_components(list_id)
        if not components:
            return jsonify({
                'success': True,
                'mylist': mylist,
                'network': {'nodes': [], 'edges': []},
                'message': 'No components in this list'
            })
        
        # Extract component IDs
        component_ids = [comp['almm_component_id'] for comp in components]
        
        # Get dependency network for these components
        network_data = db.get_dependency_network(mylist['aml_org_id'], component_ids)
        
        # Create network visualization data
        nodes = []
        edges = []
        
        # Add all components as nodes
        for comp in components:
            nodes.append({
                'id': comp['almm_component_id'],
                'label': comp['amc_dev_name'],
                'type': comp['metadata_type_name'],
                'isInList': True
            })
        
        # Add dependencies as edges - handle the network_data structure correctly
        if isinstance(network_data, dict) and 'edges' in network_data:
            for dep in network_data['edges']:
                # Find the component IDs for the dependency
                from_comp_id = None
                to_comp_id = None
                
                for comp in components:
                    if comp['amc_dev_name'] == dep.get('from'):
                        from_comp_id = comp['almm_component_id']
                    if comp['amc_dev_name'] == dep.get('to'):
                        to_comp_id = comp['almm_component_id']
                
                if from_comp_id and to_comp_id:
                    edges.append({
                        'from': from_comp_id,
                        'to': to_comp_id,
                        'type': dep.get('type', 'unknown'),
                        'description': dep.get('description', '')
                    })
        
        return jsonify({
            'success': True,
            'mylist': mylist,
            'network': {
                'nodes': nodes,
                'edges': edges
            },
            'stats': {
                'total_components': len(components),
                'total_relationships': len(edges)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def extract_metadata_to_database(job_id, session_id, metadata_url, integration_id):
    """Extract metadata directly to database without local files - COMPREHENSIVE EXTRACTION"""
    job = extraction_jobs[job_id]
    
    try:
        # Use the comprehensive metadata extraction function
        retrieve_body = get_comprehensive_metadata_retrieve_body(session_id)
        
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'retrieve'
        }
        
        job['progress'].append('Submitting retrieve request for ALL metadata types...')
        
        response = requests.post(metadata_url, data=retrieve_body, headers=headers, timeout=300)  # 5 minutes timeout for comprehensive extraction
        
        if response.status_code != 200:
            job['status'] = 'error'
            job['error'] = f"Retrieve failed: {response.status_code}"
            return False
        
        response_text = response.text
        
        # Check for faults
        if '<soapenv:Fault>' in response_text:
            fault_match = re.search(r'<faultstring>(.*?)</faultstring>', response_text)
            job['status'] = 'error'
            job['error'] = fault_match.group(1) if fault_match else "Unknown SOAP fault"
            return False
        
        # Extract async ID
        id_match = re.search(r'<id>(.*?)</id>', response_text)
        if not id_match:
            job['status'] = 'error'
            job['error'] = "No async ID found in response"
            return False
        
        async_id = id_match.group(1)
        job['progress'].append(f'Job ID: {async_id}')
        
        # Check if immediately done
        done_match = re.search(r'<done>(.*?)</done>', response_text)
        if done_match and done_match.group(1).lower() == 'true':
            job['progress'].append('Job completed immediately!')
            return process_zip_to_database(job_id, response_text, integration_id)
        
        # Poll for completion
        return poll_and_process_to_database(job_id, session_id, metadata_url, async_id, integration_id)
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = f"Retrieve exception: {str(e)}"
        return False

def poll_and_process_to_database(job_id, session_id, metadata_url, async_id, integration_id):
    """Poll for completion and process zip directly to database - INCREASED TIMEOUT FOR COMPREHENSIVE EXTRACTION"""
    job = extraction_jobs[job_id]
    
    check_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{session_id}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:checkRetrieveStatus>
         <met:asyncProcessId>{async_id}</met:asyncProcessId>
      </met:checkRetrieveStatus>
   </soapenv:Body>
</soapenv:Envelope>'''
    
    headers = {
        'Content-Type': 'text/xml; charset=UTF-8',
        'SOAPAction': 'checkRetrieveStatus'
    }
    
    # INCREASED TIMEOUT: 60 attempts × 60 seconds = 60 minutes max
    max_attempts = 60  # Increased from 15 to 60
    attempt = 0
    
    job['progress'].append('Polling for completion (comprehensive extraction - this may take 15-30 minutes)...')
    
    while attempt < max_attempts:
        attempt += 1
        job['progress'].append(f'Checking status... ({attempt}/{max_attempts}) - Comprehensive extraction in progress')
        
        try:
            response = requests.post(metadata_url, data=check_body, headers=headers, timeout=180)  # Increased timeout to 3 minutes
            
            if response.status_code != 200:
                job['status'] = 'error'
                job['error'] = f"Status check failed: {response.status_code}"
                return False
            
            response_text = response.text
            
            # Check for faults
            if '<soapenv:Fault>' in response_text:
                fault_match = re.search(r'<faultstring>(.*?)</faultstring>', response_text)
                job['status'] = 'error'
                job['error'] = fault_match.group(1) if fault_match else "Unknown SOAP fault"
                return False
            
            # Check if done
            done_match = re.search(r'<done>(.*?)</done>', response_text)
            if done_match and done_match.group(1).lower() == 'true':
                job['progress'].append('✅ Job completed! Processing immediately...')
                return process_zip_to_database(job_id, response_text, integration_id)
            
            # Wait before next check - increased from 2 to 60 seconds
            time.sleep(60)
            
        except Exception as e:
            job['progress'].append(f'Error checking status: {str(e)}')
            time.sleep(60)  # Increased from 2 to 60 seconds
    
    job['status'] = 'error'
    job['error'] = 'Job timed out (60 minutes) - Comprehensive extraction may take longer'
    return False

def process_zip_to_database(job_id, response_text, integration_id):
    """Process zip file in memory and store components directly to database"""
    job = extraction_jobs[job_id]
    
    try:
        # Verify success
        success_match = re.search(r'<success>(.*?)</success>', response_text)
        if success_match and success_match.group(1).lower() == 'false':
            job['status'] = 'error'
            job['error'] = 'Retrieve operation was not successful'
            # Look for error messages
            messages = re.findall(r'<message>(.*?)</message>', response_text)
            for msg in messages:
                job['progress'].append(f'Error message: {msg}')
            return False
        
        # Extract zip file content
        zip_match = re.search(r'<zipFile>(.*?)</zipFile>', response_text, re.DOTALL)
        if not zip_match:
            job['status'] = 'error'
            job['error'] = 'No zip file found in response'
            return False
        
        zip_b64 = zip_match.group(1).strip()
        
        job['progress'].append('Decoding and processing zip file...')
        zip_data = base64.b64decode(zip_b64)
        job['progress'].append(f'Zip file size: {len(zip_data):,} bytes')
        
        # Process zip file in memory
        job['progress'].append('Processing files in memory...')
        
        # Create extraction job in database
        db_job_id = db.create_extraction_job(
            org_id=409,
            integration_id=integration_id,
            job_status="completed",
            total_files=0,  # Will be updated after processing
            created_user_id=243
        )
        
        if not db_job_id:
            job['progress'].append('Warning: Failed to create extraction job in database')
            return False
        
        # Get metadata types for mapping
        metadata_types = db.get_metadata_types(org_id=409)
        type_mapping = {mt['amt_name']: mt['amt_id'] for mt in metadata_types}
        
        components_stored = 0
        dependencies_stored = 0
        component_map = {}  # Map component name (without extension) to component_id for dependency creation
        
        # Process zip file in memory
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_file:
            for file_info in zip_file.filelist:
                if file_info.is_dir():
                    continue
                
                filename = file_info.filename
                
                # Determine metadata type
                metadata_type = get_file_type_from_path(filename)
                type_id = type_mapping.get(metadata_type)
                
                if not type_id:
                    continue  # Skip unknown types
                
                try:
                    # Read file content from zip
                    content = zip_file.read(filename).decode('utf-8', errors='ignore')
                    
                    # Create metadata component in database WITHOUT AI summary
                    component_id = db.create_metadata_component(
                        org_id=409,
                        integration_id=integration_id,
                        extraction_job_id=db_job_id,
                        metadata_type_id=type_id,
                        label=os.path.basename(filename),
                        dev_name=os.path.basename(filename).replace('.cls', '').replace('.trigger', '').replace('.object', '').replace('.flow', '').replace('.layout', ''),
                        notes=f"Extracted from {filename}",
                        content=content,
                        ai_summary=None,  # No AI summary during extraction
                        ai_model=None,     # No AI model during extraction
                        last_modified=datetime.now(),
                        api_version="62.0",
                        created_user_id=243
                    )
                    
                    if component_id:
                        components_stored += 1
                        # Store with component name (without extension) as key
                        component_name = os.path.basename(filename).replace('.cls', '').replace('.trigger', '').replace('.object', '').replace('.flow', '').replace('.layout', '')
                        component_map[component_name] = component_id
                    
                except Exception as e:
                    job['progress'].append(f'Warning: Failed to store component {filename}: {str(e)}')
                    continue
        
        # Now analyze and store dependencies
        job['progress'].append('Analyzing dependencies between components...')
        
        # Process dependencies in memory
        for component_name, component_id in component_map.items():
            # Analyze dependencies based on file type
            dependencies = []
            
            # Determine file type from component name (we need to check what type this component is)
            component = db.get_metadata_component(component_id)
            if not component:
                continue
                
            metadata_type_id = component.get('amc_metadata_type_id')
            
            # Analyze based on metadata type
            if metadata_type_id == 1:  # Apex Class
                dependencies = analyze_apex_class_dependencies_in_memory(component_name + '.cls', component_map)
            elif metadata_type_id == 2:  # Apex Trigger
                dependencies = analyze_apex_trigger_dependencies_in_memory(component_name + '.trigger', component_map)
            elif metadata_type_id == 3:  # Custom Object
                dependencies = analyze_custom_object_dependencies_in_memory(component_name + '.object', component_map)
            elif metadata_type_id == 4:  # Flow
                dependencies = analyze_flow_dependencies_in_memory(component_name + '.flow', component_map)
            elif metadata_type_id == 5:  # Layout
                dependencies = analyze_layout_dependencies_in_memory(component_name + '.layout', component_map)
            
            # Store dependencies in database
            for dep in dependencies:
                try:
                    dependency_id = db.create_dependency(
                        org_id=409,
                        from_component_id=component_id,
                        to_component_id=dep['to_component_id'],
                        dependency_type=dep['type'],
                        description=dep['description'],
                        created_user_id=243
                    )
                    if dependency_id:
                        dependencies_stored += 1
                except Exception as e:
                    job['progress'].append(f'Warning: Failed to store dependency: {str(e)}')
                    continue
        
        # Update job with final stats
        metadata_stats = {
            "totalFiles": components_stored,
            "components_stored": components_stored,
            "dependencies_stored": dependencies_stored
        }
        
        db.update_extraction_job(
            job_id=db_job_id,
            job_status="completed",
            completed_at=datetime.now(),
            total_files=components_stored,
            job_data=metadata_stats
        )
        
        job['progress'].append(f'Successfully processed {components_stored} files!')
        job['progress'].append(f'Stored {dependencies_stored} dependencies')
        
        job['status'] = 'success'
        job['data'] = metadata_stats
        job['end_time'] = datetime.now()
        
        return True
        
    except zipfile.BadZipFile:
        job['status'] = 'error'
        job['error'] = 'Received invalid zip file'
        return False
    except Exception as e:
        job['status'] = 'error'
        job['error'] = f'Error processing zip: {str(e)}'
        return False

def analyze_apex_class_dependencies_in_memory(filename, component_map):
    """Analyze Apex class dependencies in memory"""
    dependencies = []
    
    # Get the component ID for this component name
    source_component_name = filename.replace('.cls', '')
    source_component_id = component_map.get(source_component_name)
    if not source_component_id:
        return dependencies
    
    # Get the content from the database for this component
    try:
        component = db.get_metadata_component(source_component_id)
        if not component or not component.get('amc_content'):
            return dependencies
        
        content = component['amc_content']
        source_name = source_component_name
        
        # Use the actual component ID from database, not from map
        actual_source_component_id = component['amc_id']
        
        # SOQL queries
        soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
        for match in re.finditer(soql_pattern, content):
            obj_name = match.group(1)
            if '_' in obj_name and not obj_name.endswith('__c'):
                obj_name = f"{obj_name}__c"
            
            # Find the component ID for this object
            target_component_id = component_map.get(obj_name)
            if target_component_id and target_component_id != actual_source_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'soql_query',
                    'description': f'{source_name} queries {obj_name}'
                })
        
        # DML operations
        dml_pattern = r'(?i)(insert|update|delete|upsert|merge)\s+(\w+)'
        for match in re.finditer(dml_pattern, content):
            var_name = match.group(2)
            if var_name.lower() not in ['list', 'set', 'map', 'string', 'integer', 'boolean']:
                target_component_id = component_map.get(var_name)
                if target_component_id and target_component_id != actual_source_component_id:
                    dependencies.append({
                        'to_component_id': target_component_id,
                        'type': 'dml_operation',
                        'description': f'{source_name} performs {match.group(1)} on {var_name}'
                    })
        
        # Class references
        class_pattern = r'(?i)public\s+class\s+(\w+)\s+extends\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            parent_class = match.group(2)
            target_component_id = component_map.get(parent_class)
            if target_component_id and target_component_id != actual_source_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'class_inheritance',
                    'description': f'{source_name} extends {parent_class}'
                })
        
        # Interface implementations
        interface_pattern = r'(?i)public\s+class\s+(\w+)\s+implements\s+(\w+)'
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(2)
            target_component_id = component_map.get(interface_name)
            if target_component_id and target_component_id != actual_source_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'interface_implementation',
                    'description': f'{source_name} implements {interface_name}'
                })
        
    except Exception as e:
        print(f"Error analyzing Apex class dependencies in memory for {filename}: {str(e)}")
    
    return dependencies

def analyze_apex_trigger_dependencies_in_memory(filename, component_map):
    """Analyze Apex trigger dependencies in memory"""
    dependencies = []
    
    # Get the component ID for this component name
    source_component_name = filename.replace('.trigger', '')
    source_component_id = component_map.get(source_component_name)
    if not source_component_id:
        return dependencies
    
    try:
        component = db.get_metadata_component(source_component_id)
        if not component or not component.get('amc_content'):
            return dependencies
        
        content = component['amc_content']
        source_name = source_component_name
        
        # Extract object the trigger is on
        object_match = re.search(r'trigger\s+\w+\s+on\s+(\w+)', content, re.IGNORECASE)
        if object_match:
            obj_name = object_match.group(1)
            target_component_id = component_map.get(obj_name)
            if target_component_id and target_component_id != source_component_id:
                dependencies.append({
                    'to_component_id': target_component_id,
                    'type': 'trigger_on_object',
                    'description': f'{source_name} trigger operates on {obj_name}'
                })
        
    except Exception as e:
        print(f"Error analyzing Apex trigger dependencies in memory for {filename}: {str(e)}")
    
    return dependencies

def analyze_custom_object_dependencies_in_memory(filename, component_map):
    """Analyze Custom Object dependencies in memory"""
    dependencies = []
    
    # Get the component ID for this component name
    source_component_name = filename.replace('.object', '')
    source_component_id = component_map.get(source_component_name)
    if not source_component_id:
        return dependencies
    
    try:
        component = db.get_metadata_component(source_component_id)
        if not component or not component.get('amc_content'):
            return dependencies
        
        content = component['amc_content']
        source_name = source_component_name
        
        # Parse XML content for field relationships
        try:
            root = ET.fromstring(content)
            
            # Define namespace for Salesforce metadata
            ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
            
            # Find field relationships
            for field_elem in root.findall('.//sf:fields', ns):
                field_name_elem = field_elem.find('sf:fullName', ns)
                ref_to_elem = field_elem.find('sf:referenceTo', ns)
                type_elem = field_elem.find('sf:type', ns)
                
                if field_name_elem is not None and ref_to_elem is not None:
                    field_name = field_name_elem.text
                    ref_to = ref_to_elem.text
                    field_type = type_elem.text if type_elem is not None else None
                    
                    # Look for reference relationships
                    if ref_to and field_type in ['Lookup', 'MasterDetail']:
                        target_component_id = component_map.get(ref_to)
                        if target_component_id and target_component_id != source_component_id:
                            dependencies.append({
                                'to_component_id': target_component_id,
                                'type': 'object_reference',
                                'description': f'{source_name} has {field_type} field referencing {ref_to}'
                            })
            
        except ET.ParseError as e:
            print(f"Error parsing XML for {filename}: {str(e)}")
        
    except Exception as e:
        print(f"Error analyzing Custom Object dependencies in memory for {filename}: {str(e)}")
    
    return dependencies

def analyze_flow_dependencies_in_memory(filename, component_map):
    """Analyze Flow dependencies in memory"""
    dependencies = []
    
    # Get the component ID for this component name
    source_component_name = filename.replace('.flow', '')
    source_component_id = component_map.get(source_component_name)
    if not source_component_id:
        return dependencies
    
    try:
        component = db.get_metadata_component(source_component_id)
        if not component or not component.get('amc_content'):
            return dependencies
        
        content = component['amc_content']
        source_name = source_component_name
        
        # Parse XML content for dependencies
        try:
            root = ET.fromstring(content)
            
            # Define namespace for Salesforce metadata
            ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
            
            # Find object references
            for obj_elem in root.findall('.//sf:object', ns):
                if obj_elem.text:
                    obj_name = obj_elem.text
                    target_component_id = component_map.get(obj_name)
                    if target_component_id and target_component_id != source_component_id:
                        dependencies.append({
                            'to_component_id': target_component_id,
                            'type': 'flow_object_reference',
                            'description': f'{source_name} flow references object {obj_name}'
                        })
            
            # Find Apex class references
            for apex_elem in root.findall('.//sf:apexClass', ns):
                if apex_elem.text:
                    apex_class = apex_elem.text
                    target_component_id = component_map.get(apex_class)
                    if target_component_id and target_component_id != source_component_id:
                        dependencies.append({
                            'to_component_id': target_component_id,
                            'type': 'flow_apex_reference',
                            'description': f'{source_name} flow calls Apex class {apex_class}'
                        })
            
        except ET.ParseError as e:
            print(f"Error parsing XML for {filename}: {str(e)}")
        
    except Exception as e:
        print(f"Error analyzing Flow dependencies in memory for {filename}: {str(e)}")
    
    return dependencies

def analyze_layout_dependencies_in_memory(filename, component_map):
    """Analyze Layout dependencies in memory"""
    dependencies = []
    
    # Get the component ID for this component name
    source_component_name = filename.replace('.layout', '')
    source_component_id = component_map.get(source_component_name)
    if not source_component_id:
        return dependencies
    
    try:
        component = db.get_metadata_component(source_component_id)
        if not component or not component.get('amc_content'):
            return dependencies
        
        content = component['amc_content']
        source_name = source_component_name
        
        # Parse XML content for dependencies
        try:
            root = ET.fromstring(content)
            
            # Define namespace for Salesforce metadata
            ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
            
            # Find object references
            for obj_elem in root.findall('.//sf:object', ns):
                if obj_elem.text:
                    obj_name = obj_elem.text
                    target_component_id = component_map.get(obj_name)
                    if target_component_id and target_component_id != source_component_id:
                        dependencies.append({
                            'to_component_id': target_component_id,
                            'type': 'layout_object_reference',
                            'description': f'{source_name} layout is for object {obj_name}'
                        })
            
        except ET.ParseError as e:
            print(f"Error parsing XML for {filename}: {str(e)}")
        
    except Exception as e:
        print(f"Error analyzing Layout dependencies in memory for {filename}: {str(e)}")
    
    return dependencies

@app.route('/api/mylists/<int:list_id>/generate-summaries', methods=['POST'])
def generate_list_summaries(list_id):
    """Generate AI summaries for all components in a list"""
    try:
        # Get the list details first
        list_details = db.get_mylist(list_id)
        if not list_details:
            return jsonify({'success': False, 'error': 'List not found'}), 404
        
        # Get all components in the list
        components = db.get_list_components(list_id)
        if not components:
            return jsonify({'success': False, 'error': 'No components found in list'}), 404
        
        print(f"Generating summaries for list '{list_details['aml_name']}' with {len(components)} components")
        
        # Generate summaries for each component that doesn't have one
        summaries_generated = 0
        for component in components:
            if not component.get('amc_ai_summary'):
                try:
                    # Generate summary for this component
                    summary_response = generate_component_summary_logic(component['amc_id'])
                    if summary_response.get('success'):
                        summaries_generated += 1
                        print(f"Generated summary for component {component['amc_dev_name']}")
                    else:
                        print(f"Failed to generate summary for component {component['amc_dev_name']}: {summary_response.get('error')}")
                except Exception as e:
                    print(f"Error generating summary for component {component['amc_dev_name']}: {str(e)}")
        
        # Get updated components with summaries
        updated_components = db.get_list_components(list_id)
        
        # Create a combined summary
        combined_summary = f"# {list_details['aml_name']}\n\n"
        combined_summary += f"**List Description:** {list_details.get('aml_description', 'No description available')}\n\n"
        combined_summary += f"**Total Components:** {len(updated_components)}\n\n"
        combined_summary += "## Component Summaries\n\n"
        
        for component in updated_components:
            component_name = component.get('amc_dev_name', component.get('amc_label', 'Unknown'))
            component_type = component.get('metadata_type_name', 'Unknown Type')
            summary = component.get('amc_ai_summary', 'No summary available')
            
            combined_summary += f"### {component_name} ({component_type})\n"
            combined_summary += f"{summary}\n\n"
        
        return jsonify({
            'success': True,
            'list_name': list_details['aml_name'],
            'list_description': list_details.get('aml_description', ''),
            'total_components': len(updated_components),
            'summaries_generated': summaries_generated,
            'combined_summary': combined_summary,
            'components': updated_components
        })
        
    except Exception as e:
        print(f"Error generating list summaries: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_component_summary_logic(component_id):
    """Helper function to generate summary for a single component"""
    try:
        # Get component details
        component = db.get_metadata_component(component_id)
        if not component:
            return {'success': False, 'error': 'Component not found'}
        
        # Get component content
        content = component.get('amc_content', '')
        if not content:
            return {'success': False, 'error': 'No content available for summary generation'}
        
        # Generate AI summary
        filename = component.get('amc_dev_name', component.get('amc_label', 'Unknown'))
        summary = generate_metadata_summary(filename, content)
        
        # Update component with new summary
        success = db.update_metadata_component(
            component_id=component_id,
            ai_summary=summary,
            ai_model='gpt-3.5-turbo'
        )
        
        if success:
            return {'success': True, 'summary': summary}
        else:
            return {'success': False, 'error': 'Failed to update component with summary'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/api/metadata-component/<int:component_id>/update-notes', methods=['PUT'])
def update_metadata_component_notes(component_id):
    """Update notes for a metadata component"""
    try:
        data = request.json
        
        if not data or 'notes' not in data:
            return jsonify({'success': False, 'error': 'Notes field is required'}), 400
        
        notes = data['notes']
        user_id = data.get('user_id', 243)  # Default user ID
        
        # Update the component notes
        success = db.update_metadata_component_notes(
            component_id=component_id,
            notes=notes,
            last_updated_user_id=user_id
        )
        
        if success:
            # Get the updated component to return current data
            component = db.get_metadata_component(component_id)
            return jsonify({
                'success': True,
                'message': 'Notes updated successfully',
                'component': component
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update notes'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search-metadata', methods=['GET'])
def search_metadata():
    """Search metadata components"""
    try:
        org_id = request.args.get('org_id', 409)  # Default org_id
        search_term = request.args.get('search_term')
        metadata_type_id = request.args.get('metadata_type_id')
        
        if metadata_type_id:
            metadata_type_id = int(metadata_type_id)
        
        components = db.search_metadata_components(
            org_id=int(org_id),
            search_term=search_term,
            metadata_type_id=metadata_type_id
        )
        
        return jsonify({
            'success': True,
            'components': components,
            'count': len(components)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Salesforce Metadata Extractor Backend with Database Integration...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 API endpoints:")
    print("   POST /api/integrations - Create integration")
    print("   GET  /api/integrations/<id> - Get integration")
    print("   GET  /api/integrations/org/<org_id> - Get integrations by org")
    print("   GET  /api/integrations/user/<user_id> - Get user integrations")
    print("   PUT  /api/integrations/<id> - Update integration")
    print("   DELETE /api/integrations/<id> - Delete integration")
    print("   POST /api/store-integration - Store integration with credentials")
    print("   POST /api/login-with-integration/<id> - Login with stored integration")
    print("   GET  /api/dashboard/user/<user_id>/org/<org_id> - Get user dashboard")
    print("   GET  /api/dashboard/integration/<id> - Get integration dashboard")
    print("   POST /api/dashboard/extract/<id> - Extract metadata for dashboard")
    print("   GET  /api/dashboard/job-status/<job_id> - Get dashboard job status")
    print("   POST /api/metadata-types - Create metadata type")
    print("   GET  /api/metadata-types/org/<org_id> - Get metadata types")
    print("   POST /api/extraction-jobs - Create extraction job")
    print("   GET  /api/extraction-jobs/<id> - Get extraction job")
    print("   GET  /api/extraction-jobs/integration/<id> - Get jobs by integration")
    print("   PUT  /api/extraction-jobs/<id> - Update extraction job")
    print("   GET  /api/metadata-components/<job_id> - Get components by job")
    print("   GET  /api/metadata-component/<component_id> - Get specific component")
    print("   GET  /api/metadata-from-integration/<integration_id> - Get metadata from integration")
    print("   GET  /api/search-metadata - Search metadata components")
    print("   POST /api/extract-metadata-with-login - Start extraction with login")
    print("   POST /api/extract-metadata - Start extraction")
    print("   GET  /api/job-status/<id> - Check job status")
    print("   GET  /api/metadata-files/<id>/<type> - List files")
    print("   POST /api/login-test - Test login credentials")
    print("   GET  /api/health - Health check")
    print("   POST /api/metadata-component/<id>/generate-summary - Generate AI summary")
    print("   GET  /api/metadata-component/<id>/details - Get component details")
    print("   GET  /api/metadata-component/<id>/dependencies - Get component dependencies")
    print("   GET  /api/metadata-component/<id>/content - Get component content")
    print("   GET  /api/metadata-component/<id>/dependency-network - Get dependency network")
    print("   POST /api/mylists - Create MyList")
    print("   GET  /api/mylists/user/<user_id>/org/<org_id> - Get user MyLists")
    print("   GET  /api/mylists/<id> - Get MyList by ID")
    print("   GET  /api/mylists/<id>/components - Get MyList components")
    print("   POST /api/mylists/<id>/components - Add component to MyList")
    print("   DELETE /api/mylists/<id>/components/<component_id> - Remove component from MyList")
    print("   GET  /api/mylists/<id>/dependency-network - Get MyList dependency network")
    print("   POST /api/mylists/<id>/generate-summaries - Generate AI summaries for all components in a list")
    print("\n✨ Ready to work with database and extract metadata!")
    
    app.run(debug=False, host='0.0.0.0', port=5000) 