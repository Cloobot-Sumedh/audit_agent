#!/usr/bin/env python3
"""
Flask Backend for Salesforce Metadata Extractor
Complete and Fixed Version
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
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Store active extraction jobs
extraction_jobs = {}

# Store metadata relationships and analysis
metadata_relationships = {}
metadata_objects = {}

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

def extract_metadata_corrected(job_id, session_id, metadata_url, output_dir):
    """Extract metadata using existing logic"""
    
    job = extraction_jobs[job_id]
    
    try:
        # Create the retrieve request
        retrieve_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{session_id}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:retrieve>
         <met:retrieveRequest>
            <met:apiVersion>62.0</met:apiVersion>
            <met:singlePackage>true</met:singlePackage>
            <met:unpackaged>
               <types>
                  <members>*</members>
                  <name>ApexClass</name>
               </types>
               <types>
                  <members>*</members>
                  <name>ApexTrigger</name>
               </types>
               <types>
                  <members>*</members>
                  <name>CustomObject</name>
               </types>
               <types>
                  <members>*</members>
                  <name>Flow</name>
               </types>
               <types>
                  <members>*</members>
                  <name>Layout</name>
               </types>
               <version>62.0</version>
            </met:unpackaged>
         </met:retrieveRequest>
      </met:retrieve>
   </soapenv:Body>
</soapenv:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'retrieve'
        }
        
        job['progress'].append('Submitting retrieve request...')
        
        response = requests.post(metadata_url, data=retrieve_body, headers=headers)
        
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
    """Poll for completion and download when ready"""
    
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
    
    job['progress'].append('Polling for completion...')
    
    max_attempts = 15  # 7.5 minutes max
    for i in range(max_attempts):
        time.sleep(30)  # Wait 30 seconds
        job['progress'].append(f'Checking status... ({i+1}/{max_attempts})')
        
        try:
            response = requests.post(metadata_url, data=check_body, headers=headers, timeout=120)
            
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
    job['error'] = 'Timed out waiting for completion'
    return False

def download_and_extract(job_id, response_text, output_dir):
    """Download and extract the metadata zip"""
    
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
        
        # Analyze relationships between metadata components
        job['progress'].append('Analyzing metadata relationships...')
        relationship_data = analyze_metadata_relationships(job_id, extract_dir)
        
        job['progress'].append('Successfully extracted {total_files} files!'.format(total_files=metadata_stats["totalFiles"]))
        job['progress'].append(f'Found {len(relationship_data["relationships"])} relationships between components')
        job['progress'].append(f'Output directory: {os.path.abspath(extract_dir)}')
        
        job['status'] = 'success'
        job['data'] = metadata_stats
        job['data']['relationships'] = relationship_data
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

def analyze_apex_class(file_path, filename):
    """Analyze Apex class for relationships"""
    relationships = []
    
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
            
            relationships.append({
                'from': source_name,
                'to': obj_name,
                'type': 'soql_query',
                'description': f'{source_name} queries {obj_name}'
            })
        
        # DML operations
        dml_pattern = r'(?i)(insert|update|delete|upsert|merge)\s+(\w+)'
        for match in re.finditer(dml_pattern, content):
            var_name = match.group(2)
            if var_name.lower() not in ['list', 'set', 'map', 'string', 'integer', 'boolean']:
                relationships.append({
                    'from': source_name,
                    'to': var_name,
                    'type': 'dml_operation',
                    'operation': match.group(1).lower(),
                    'description': f'{source_name} performs {match.group(1)} on {var_name}'
                })
        
    except Exception as e:
        print(f"Error analyzing Apex class {filename}: {str(e)}")
    
    return relationships

def analyze_apex_trigger(file_path, filename):
    """Analyze Apex trigger for relationships"""
    relationships = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        source_name = filename.replace('.trigger', '')
        
        # Extract object the trigger is on
        object_match = re.search(r'trigger\s+\w+\s+on\s+(\w+)', content)
        if object_match:
            obj_name = object_match.group(1)
            relationships.append({
                'from': source_name,
                'to': obj_name,
                'type': 'trigger_on_object',
                'description': f'{source_name} is a trigger on {obj_name}'
            })
        
    except Exception as e:
        print(f"Error analyzing trigger {filename}: {str(e)}")
    
    return relationships

def analyze_custom_object(file_path, filename):
    """Analyze custom object for relationships"""
    relationships = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        source_name = filename.replace('.object', '')
        
        # Find field relationships
        for field_elem in root.findall('.//fields'):
            field_name_elem = field_elem.find('fullName')
            ref_to_elem = field_elem.find('referenceTo')
            
            if field_name_elem is not None and ref_to_elem is not None:
                field_name = field_name_elem.text
                ref_to = ref_to_elem.text
                
                relationships.append({
                    'from': source_name,
                    'to': ref_to,
                    'type': 'field_reference',
                    'field': field_name,
                    'description': f'{source_name}.{field_name} references {ref_to}'
                })
        
    except Exception as e:
        print(f"Error analyzing object {filename}: {str(e)}")
    
    return relationships

def analyze_flow(file_path, filename):
    """Analyze flow for relationships"""
    relationships = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        source_name = filename.replace('.flow', '')
        
        # Find object references
        for obj_elem in root.findall('.//object'):
            if obj_elem.text:
                obj_name = obj_elem.text
                relationships.append({
                    'from': source_name,
                    'to': obj_name,
                    'type': 'flow_object_reference',
                    'description': f'{source_name} flow uses {obj_name}'
                })
        
    except Exception as e:
        print(f"Error analyzing flow {filename}: {str(e)}")
    
    return relationships

def analyze_layout(file_path, filename):
    """Analyze layout for relationships"""
    relationships = []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        source_name = filename.replace('.layout', '')
        
        # Extract object name from layout name
        object_name = source_name.split('-')[0] if '-' in source_name else None
        
        if object_name:
            relationships.append({
                'from': source_name,
                'to': object_name,
                'type': 'layout_for_object',
                'description': f'{source_name} is a layout for {object_name}'
            })
        
    except Exception as e:
        print(f"Error analyzing layout {filename}: {str(e)}")
    
    return relationships

def analyze_metadata_relationships(job_id, extract_dir):
    """Analyze relationships between metadata components"""
    
    try:
        relationships = []
        objects = {}
        
        # Parse metadata files and find relationships
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.endswith('.cls'):
                    apex_relationships = analyze_apex_class(file_path, file)
                    relationships.extend(apex_relationships)
                    objects[file] = {'type': 'ApexClass', 'path': file_path}
                    
                elif file.endswith('.trigger'):
                    trigger_relationships = analyze_apex_trigger(file_path, file)
                    relationships.extend(trigger_relationships)
                    objects[file] = {'type': 'ApexTrigger', 'path': file_path}
                    
                elif file.endswith('.object'):
                    object_relationships = analyze_custom_object(file_path, file)
                    relationships.extend(object_relationships)
                    objects[file] = {'type': 'CustomObject', 'path': file_path}
                    
                elif file.endswith('.flow'):
                    flow_relationships = analyze_flow(file_path, file)
                    relationships.extend(flow_relationships)
                    objects[file] = {'type': 'Flow', 'path': file_path}
                    
                elif file.endswith('.layout'):
                    layout_relationships = analyze_layout(file_path, file)
                    relationships.extend(layout_relationships)
                    objects[file] = {'type': 'Layout', 'path': file_path}
        
        # Store globally for later use
        metadata_relationships[job_id] = relationships
        metadata_objects[job_id] = objects
        
        return {
            'relationships': relationships,
            'objects': objects,
            'total_relationships': len(relationships),
            'total_objects': len(objects)
        }
        
    except Exception as e:
        print(f"Error analyzing relationships: {str(e)}")
        return {'relationships': [], 'objects': {}, 'total_relationships': 0, 'total_objects': 0}

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
    
    file_type = get_file_type(filename)
    
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

def get_file_type(filename):
    """Determine the metadata type from filename"""
    
    if filename.endswith('.cls'):
        return "ApexClass"
    elif filename.endswith('.trigger'):
        return "ApexTrigger"
    elif filename.endswith('.flow'):
        return "Flow"
    elif filename.endswith('.object'):
        return "CustomObject"
    elif filename.endswith('.layout'):
        return "Layout"
    else:
        return "Unknown"

def extract_metadata_async(job_id, username, password, security_token, is_sandbox, output_dir):
    """Main async extraction workflow - REMOVED login success message"""
    
    job = extraction_jobs[job_id]
    
    try:
        # Step 1: Login (silently, no progress message)
        session_id, server_url, error = login_to_salesforce(username, password, security_token, is_sandbox)
        
        if error:
            job['status'] = 'error'
            job['error'] = error
            return
        
        # REMOVED: job['progress'].append('✅ Login successful!')
        
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

# API Routes
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

@app.route('/api/login-test', methods=['POST'])
def test_login():
    """Test login credentials without starting extraction"""
    
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
        
        # Login successful
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'session_valid': True,
            'environment': 'Sandbox' if is_sandbox else 'Production'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Also update the extract-metadata endpoint to include login verification
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
    
@app.route('/api/metadata-summary/<job_id>/<path:filename>', methods=['GET'])
def get_metadata_summary(job_id, filename):
    """Generate AI summary for a metadata file"""
    
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
        
        # Find and read the file
        file_content = None
        file_path = None
        
        for root, dirs, files in os.walk(output_path):
            if filename in files:
                file_path = os.path.join(root, filename)
                
                # Security check
                try:
                    if os.path.commonpath([output_path, file_path]) != output_path:
                        return jsonify({'success': False, 'error': 'Access denied'}), 403
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid file path'}), 403
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                    break
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Error reading file: {str(e)}'}), 500
        
        if not file_content:
            return jsonify({'success': False, 'error': 'File not found or empty'}), 404
        
        # Generate summary using Together AI
        summary = generate_metadata_summary(filename, file_content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'summary': summary,
            'file_size': len(file_content)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating summary: {str(e)}'}), 500

@app.route('/api/metadata-xml/<job_id>/<path:filename>', methods=['GET'])
def get_metadata_xml(job_id, filename):
    """Get raw XML content for a metadata file"""
    
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
        
        # Find and read the file
        file_content = None
        file_path = None
        
        for root, dirs, files in os.walk(output_path):
            if filename in files:
                file_path = os.path.join(root, filename)
                
                # Security check
                try:
                    if os.path.commonpath([output_path, file_path]) != output_path:
                        return jsonify({'success': False, 'error': 'Access denied'}), 403
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid file path'}), 403
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                    break
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Error reading file: {str(e)}'}), 500
        
        if file_content is None:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Determine file type for better presentation
        file_type = get_file_type(filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': file_content,
            'file_type': file_type,
            'size': len(file_content),
            'lines': len(file_content.split('\n'))
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error reading XML content: {str(e)}'}), 500

@app.route('/api/metadata-relationships/<job_id>/<path:filename>')
def get_metadata_relationships(job_id, filename):
    """Get relationships for a specific metadata file"""
    
    if job_id not in extraction_jobs:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    job = extraction_jobs[job_id]
    if job['status'] != 'success':
        return jsonify({'success': False, 'error': 'Job not completed successfully'}), 400
    
    try:
        # Get relationships for this file
        relationships = metadata_relationships.get(job_id, [])
        objects = metadata_objects.get(job_id, {})
        
        # Clean filename for matching
        clean_filename = filename.replace('.cls', '').replace('.trigger', '').replace('.object', '').replace('.flow', '').replace('.layout', '')
        
        # Find relationships where this file is involved
        file_relationships = []
        for rel in relationships:
            if rel['from'] == clean_filename or rel['to'] == clean_filename:
                file_relationships.append(rel)
        
        # Create network data for visualization
        nodes = set()
        edges = []
        
        for rel in file_relationships:
            nodes.add(rel['from'])
            nodes.add(rel['to'])
            edges.append({
                'from': rel['from'],
                'to': rel['to'],
                'type': rel['type'],
                'description': rel.get('description', ''),
                'operation': rel.get('operation', ''),
                'field': rel.get('field', '')
            })
        
        # Convert nodes to list with metadata
        node_list = []
        for node in nodes:
            # Find the node type
            node_type = 'Unknown'
            for obj_name, obj_data in objects.items():
                if obj_name.replace('.cls', '').replace('.trigger', '').replace('.object', '').replace('.flow', '').replace('.layout', '') == node:
                    node_type = obj_data['type']
                    break
            
            node_list.append({
                'id': node,
                'label': node,
                'type': node_type,
                'isTarget': node == clean_filename
            })
        
        return jsonify({
            'success': True,
            'filename': filename,
            'relationships': file_relationships,
            'network': {
                'nodes': node_list,
                'edges': edges
            },
            'stats': {
                'total_relationships': len(file_relationships),
                'incoming': len([r for r in file_relationships if r['to'] == clean_filename]),
                'outgoing': len([r for r in file_relationships if r['from'] == clean_filename])
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error getting relationships: {str(e)}'}), 500

@app.route('/api/download-file/<job_id>/<path:filename>')
def download_metadata_file(job_id, filename):
    """Download a specific metadata file"""
    
    if job_id not in extraction_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = extraction_jobs[job_id]
    if job['status'] != 'success':
        return jsonify({'error': 'Job not completed successfully'}), 400
    
    try:
        # Get the output directory from job data
        if 'data' not in job or not job['data'] or 'outputPath' not in job['data']:
            return jsonify({'error': 'Output path not found'}), 404
        
        output_path = job['data']['outputPath']
        
        # Find the file in the directory structure
        for root, dirs, files in os.walk(output_path):
            if filename in files:
                file_path = os.path.join(root, filename)
                directory = os.path.dirname(file_path)
                
                # Security check - make sure file is within the output path
                try:
                    if os.path.commonpath([output_path, file_path]) != output_path:
                        return jsonify({'error': 'Access denied'}), 403
                except ValueError:
                    return jsonify({'error': 'Invalid file path'}), 403
                
                return send_from_directory(directory, filename, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Serve React app (for production)
@app.route('/')
def serve_react_app():
    try:
        return send_from_directory('build', 'index.html')
    except:
        return jsonify({'message': 'React build not found. Run npm run build in frontend directory.'}), 404

@app.route('/<path:path>')
def serve_react_static(path):
    try:
        if os.path.exists(os.path.join('build', path)):
            return send_from_directory('build', path)
        else:
            return send_from_directory('build', 'index.html')
    except:
        return jsonify({'message': 'React build not found.'}), 404

if __name__ == '__main__':
    print("🚀 Starting Salesforce Metadata Extractor Backend...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 API endpoints:")
    print("   POST /api/extract-metadata - Start extraction")
    print("   GET  /api/job-status/<id> - Check job status") 
    print("   GET  /api/metadata-files/<id>/<type> - List files")
    print("   GET  /api/metadata-summary/<id>/<file> - AI summary")
    print("   GET  /api/metadata-xml/<id>/<file> - XML content")
    print("   GET  /api/metadata-relationships/<id>/<file> - Relationships")
    print("   GET  /api/download-file/<id>/<file> - Download file")
    print("   GET  /api/health - Health check")
    print("\n✨ Ready to extract metadata!")
    
    # Disable auto-reload to prevent restarting when files are extracted
    app.run(debug=False, host='0.0.0.0', port=5000)