#!/usr/bin/env python3
"""
Database connection and operations module for Salesforce Audit Agent
Uses PostgreSQL with the audit agent schema
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
import json
from typing import Dict, List, Optional, Any
import logging

# Database configuration from test_db.py
DB_CONFIG = {
    'dbname': '',
    'user': '',
    'password': '',
    'host': '',
    'port': 5432
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for all audit agent operations"""
    
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """Get database connection with proper error handling"""
        try:
            if self.connection is None or self.connection.closed:
                self.connection = psycopg2.connect(**DB_CONFIG)
                self.connection.autocommit = True
            return self.connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Execute a database query with proper error handling"""
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Database query error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    # Integration Management
    def create_integration(self, org_id: int, name: str, instance_url: str, org_type: str, 
                          token: str, ext_app_id: int, created_user_id: int) -> int:
        """Create a new integration record"""
        query = """
            INSERT INTO ids_integration (
                i_org_id, i_name, i_instance_url, i_org_type, i_token, 
                i_ext_app_id, i_created_user_id, i_created_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING i_id;
        """
        result = self.execute_query(query, (org_id, name, instance_url, org_type, token, ext_app_id, created_user_id), fetch_one=True)
        return result['i_id'] if result else None
    
    def get_integration(self, integration_id: int) -> Optional[Dict]:
        """Get integration by ID"""
        query = "SELECT * FROM ids_integration WHERE i_id = %s AND i_status = 1"
        return self.execute_query(query, (integration_id,), fetch_one=True)
    
    def get_integrations_by_org(self, org_id: int) -> List[Dict]:
        """Get all integrations for an organization"""
        query = "SELECT * FROM ids_integration WHERE i_org_id = %s AND i_status = 1 ORDER BY i_created_timestamp DESC"
        return self.execute_query(query, (org_id,), fetch_all=True)
    
    def update_integration(self, integration_id: int, name: str = None, instance_url: str = None, 
                          org_type: str = None, token: str = None, ext_app_id: int = None, 
                          last_updated_user_id: int = None):
        """Update integration record"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("i_name = %s")
            params.append(name)
        
        if instance_url is not None:
            updates.append("i_instance_url = %s")
            params.append(instance_url)
        
        if org_type is not None:
            updates.append("i_org_type = %s")
            params.append(org_type)
        
        if token is not None:
            updates.append("i_token = %s")
            params.append(token)
        
        if ext_app_id is not None:
            updates.append("i_ext_app_id = %s")
            params.append(ext_app_id)
        
        if last_updated_user_id is not None:
            updates.append("i_last_updated_user_id = %s")
            params.append(last_updated_user_id)
        
        if updates:
            updates.append("i_last_updated_timestamp = CURRENT_TIMESTAMP")
            params.append(integration_id)
            
            query = f"UPDATE ids_integration SET {', '.join(updates)} WHERE i_id = %s AND i_status = 1"
            return self.execute_query(query, tuple(params))
        
        return 0
    
    def delete_integration(self, integration_id: int, last_updated_user_id: int = None):
        """Soft delete integration (set status to -1)"""
        query = """
            UPDATE ids_integration 
            SET i_status = -1, i_last_updated_timestamp = CURRENT_TIMESTAMP
        """
        params = []
        
        if last_updated_user_id:
            query += ", i_last_updated_user_id = %s"
            params.append(last_updated_user_id)
        
        query += " WHERE i_id = %s"
        params.append(integration_id)
        
        return self.execute_query(query, tuple(params))
    
    # Metadata Type Management
    def create_metadata_type(self, org_id: int, name: str, display_name: str, description: str, 
                           icon: str, file_extension: str, created_user_id: int) -> int:
        """Create a new metadata type record"""
        query = """
            INSERT INTO ids_audit_metadata_type (
                amt_org_id, amt_name, amt_display_name, amt_description, 
                amt_icon, amt_file_extension, amt_created_user_id, amt_created_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING amt_id;
        """
        result = self.execute_query(query, (org_id, name, display_name, description, icon, file_extension, created_user_id), fetch_one=True)
        return result['amt_id'] if result else None
    
    def get_metadata_types(self, org_id: int) -> List[Dict]:
        """Get all metadata types for an organization"""
        query = "SELECT * FROM ids_audit_metadata_type WHERE amt_org_id = %s AND amt_status = 1 ORDER BY amt_name"
        return self.execute_query(query, (org_id,), fetch_all=True)
    
    # Extraction Job Management
    def create_extraction_job(self, org_id: int, integration_id: int, job_status: str, 
                            total_files: int, created_user_id: int) -> int:
        """Create a new extraction job record"""
        query = """
            INSERT INTO ids_audit_extraction_job (
                aej_org_id, aej_integration_id, aej_job_status, aej_started_at,
                aej_total_files, aej_created_user_id, aej_created_timestamp
            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, CURRENT_TIMESTAMP)
            RETURNING aej_id;
        """
        result = self.execute_query(query, (org_id, integration_id, job_status, total_files, created_user_id), fetch_one=True)
        return result['aej_id'] if result else None
    
    def update_extraction_job(self, job_id: int, job_status: str, completed_at: datetime = None, 
                            total_files: int = None, log: str = None, job_data: Dict = None):
        """Update extraction job status and data"""
        updates = []
        params = []
        
        if job_status:
            updates.append("aej_job_status = %s")
            params.append(job_status)
        
        if completed_at:
            updates.append("aej_completed_at = %s")
            params.append(completed_at)
        
        if total_files is not None:
            updates.append("aej_total_files = %s")
            params.append(total_files)
        
        if log:
            updates.append("aej_log = %s")
            params.append(log)
        
        if job_data:
            updates.append("aej_job_data = %s")
            params.append(json.dumps(job_data))
        
        if updates:
            updates.append("aej_last_updated_timestamp = CURRENT_TIMESTAMP")
            params.append(job_id)
            
            query = f"UPDATE ids_audit_extraction_job SET {', '.join(updates)} WHERE aej_id = %s"
            self.execute_query(query, tuple(params))
    
    def get_extraction_job(self, job_id: int) -> Optional[Dict]:
        """Get extraction job by ID"""
        query = "SELECT * FROM ids_audit_extraction_job WHERE aej_id = %s AND aej_status = 1"
        return self.execute_query(query, (job_id,), fetch_one=True)
    
    def get_extraction_jobs_by_integration(self, integration_id: int) -> List[Dict]:
        """Get all extraction jobs for an integration"""
        query = """
            SELECT * FROM ids_audit_extraction_job 
            WHERE aej_integration_id = %s AND aej_status = 1 
            ORDER BY aej_created_timestamp DESC
        """
        return self.execute_query(query, (integration_id,), fetch_all=True)
    
    # Metadata Component Management
    def create_metadata_component(self, org_id: int, integration_id: int, extraction_job_id: int,
                                metadata_type_id: int, label: str, dev_name: str, notes: str,
                                content: str, ai_summary: str, ai_model: str, last_modified: datetime,
                                api_version: str, created_user_id: int) -> int:
        """Create a new metadata component record"""
        query = """
            INSERT INTO ids_audit_metadata_component (
                amc_org_id, amc_integration_id, amc_extraction_job_id, amc_metadata_type_id,
                amc_label, amc_dev_name, amc_notes, amc_content, amc_ai_summary, amc_ai_model,
                amc_last_modified, amc_api_version, amc_created_user_id, amc_created_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING amc_id;
        """
        result = self.execute_query(query, (
            org_id, integration_id, extraction_job_id, metadata_type_id, label, dev_name,
            notes, content, ai_summary, ai_model, last_modified, api_version, created_user_id
        ), fetch_one=True)
        return result['amc_id'] if result else None
    
    def get_metadata_components_by_job(self, job_id):
        """Get all metadata components for a specific extraction job"""
        try:
            query = """
                SELECT 
                    amc_id, amc_org_id, amc_integration_id, amc_extraction_job_id,
                    amc_metadata_type_id, amc_label, amc_dev_name, amc_notes,
                    amc_content, amc_ai_summary, amc_ai_model, amc_last_modified,
                    amc_api_version, amc_created_timestamp, amc_status,
                    amt_name as metadata_type_name
                FROM ids_audit_metadata_component amc
                LEFT JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
                WHERE amc.amc_extraction_job_id = %s AND amc.amc_status = 1
                ORDER BY amc.amc_dev_name
            """
            return self.execute_query(query, (job_id,), fetch_all=True)
        except Exception as e:
            print(f"Error getting metadata components by job: {e}")
            return []

    def get_metadata_components_by_job_and_type(self, job_id, type_id):
        """Get metadata components for a specific job and metadata type"""
        try:
            query = """
                SELECT 
                    amc_id, amc_org_id, amc_integration_id, amc_extraction_job_id,
                    amc_metadata_type_id, amc_label, amc_dev_name, amc_notes,
                    amc_content, amc_ai_summary, amc_ai_model, amc_last_modified,
                    amc_api_version, amc_created_timestamp, amc_status,
                    amt_name as metadata_type_name
                FROM ids_audit_metadata_component amc
                LEFT JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
                WHERE amc.amc_extraction_job_id = %s 
                AND amc.amc_metadata_type_id = %s 
                AND amc.amc_status = 1
                ORDER BY amc.amc_dev_name
            """
            return self.execute_query(query, (job_id, type_id), fetch_all=True)
        except Exception as e:
            print(f"Error getting metadata components by job and type: {e}")
            return []

    def search_metadata_components_by_job_and_type(self, job_id, type_id, search_term):
        """Search metadata components for a specific job and metadata type"""
        try:
            query = """
                SELECT 
                    amc_id, amc_org_id, amc_integration_id, amc_extraction_job_id,
                    amc_metadata_type_id, amc_label, amc_dev_name, amc_notes,
                    amc_content, amc_ai_summary, amc_ai_model, amc_last_modified,
                    amc_api_version, amc_created_timestamp, amc_status,
                    amt_name as metadata_type_name
                FROM ids_audit_metadata_component amc
                LEFT JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
                WHERE amc.amc_extraction_job_id = %s 
                AND amc.amc_metadata_type_id = %s 
                AND amc.amc_status = 1
                AND (
                    LOWER(amc.amc_dev_name) LIKE LOWER(%s) 
                    OR LOWER(amc.amc_label) LIKE LOWER(%s)
                    OR LOWER(amc.amc_notes) LIKE LOWER(%s)
                )
                ORDER BY amc.amc_dev_name
            """
            search_pattern = f'%{search_term}%'
            return self.execute_query(query, (job_id, type_id, search_pattern, search_pattern, search_pattern), fetch_all=True)
        except Exception as e:
            print(f"Error searching metadata components by job and type: {e}")
            return []
    
    def get_metadata_component(self, component_id: int) -> Optional[Dict]:
        """Get a specific metadata component"""
        query = """
            SELECT amc.*, amt.amt_name as metadata_type_name, amt.amt_display_name
            FROM ids_audit_metadata_component amc
            LEFT JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
            WHERE amc.amc_id = %s AND amc.amc_status = 1
        """
        return self.execute_query(query, (component_id,), fetch_one=True)
    
    def update_metadata_component(self, component_id: int, ai_summary: str = None, ai_model: str = None, last_updated_user_id: int = None) -> bool:
        """Update a metadata component (primarily for AI summary)"""
        try:
            update_fields = []
            params = []
            
            if ai_summary is not None:
                update_fields.append("amc_ai_summary = %s")
                params.append(ai_summary)
            
            if ai_model is not None:
                update_fields.append("amc_ai_model = %s")
                params.append(ai_model)
            
            if last_updated_user_id is not None:
                update_fields.append("amc_last_updated_user_id = %s")
                params.append(last_updated_user_id)
            
            if update_fields:
                update_fields.append("amc_last_updated_timestamp = CURRENT_TIMESTAMP")
                
                query = f"""
                    UPDATE ids_audit_metadata_component 
                    SET {', '.join(update_fields)}
                    WHERE amc_id = %s AND amc_status = 1
                """
                params.append(component_id)
                
                result = self.execute_query(query, tuple(params))
                return result is not None
            else:
                return False
                
        except Exception as e:
            print(f"Error updating metadata component: {e}")
            return False

    def update_metadata_component_notes(self, component_id: int, notes: str, last_updated_user_id: int = None) -> bool:
        """Update notes for a metadata component"""
        try:
            update_fields = ["amc_notes = %s"]
            params = [notes]
            
            if last_updated_user_id is not None:
                update_fields.append("amc_last_updated_user_id = %s")
                params.append(last_updated_user_id)
            
            update_fields.append("amc_last_updated_timestamp = CURRENT_TIMESTAMP")
            
            query = f"""
                UPDATE ids_audit_metadata_component 
                SET {', '.join(update_fields)}
                WHERE amc_id = %s AND amc_status = 1
            """
            params.append(component_id)
            
            result = self.execute_query(query, tuple(params))
            return result is not None
                
        except Exception as e:
            print(f"Error updating metadata component notes: {e}")
            return False
    
    def get_metadata_stats_by_job(self, extraction_job_id: int) -> Dict:
        """Get metadata statistics for a specific extraction job"""
        query = """
            SELECT 
                amt.amt_name as metadata_type,
                amt.amt_display_name,
                COUNT(amc.amc_id) as component_count
            FROM ids_audit_metadata_component amc
            LEFT JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
            WHERE amc.amc_extraction_job_id = %s AND amc.amc_status = 1
            GROUP BY amt.amt_id, amt.amt_name, amt.amt_display_name
            ORDER BY component_count DESC
        """
        stats = self.execute_query(query, (extraction_job_id,), fetch_all=True)
        
        # Get total count
        total_query = """
            SELECT COUNT(*) as total_components
            FROM ids_audit_metadata_component amc
            WHERE amc.amc_extraction_job_id = %s AND amc.amc_status = 1
        """
        total_result = self.execute_query(total_query, (extraction_job_id,), fetch_one=True)
        total_components = total_result['total_components'] if total_result else 0
        
        return {
            'total_components': total_components,
            'by_type': stats
        }
    
    def get_latest_extraction_job(self, integration_id: int) -> Optional[Dict]:
        """Get the latest extraction job for an integration"""
        query = """
            SELECT * FROM ids_audit_extraction_job 
            WHERE aej_integration_id = %s AND aej_status = 1
            ORDER BY aej_created_timestamp DESC 
            LIMIT 1
        """
        return self.execute_query(query, (integration_id,), fetch_one=True)
    
    def get_integration_with_latest_job(self, integration_id: int) -> Optional[Dict]:
        """Get integration with its latest extraction job and metadata stats"""
        # Get integration
        integration = self.get_integration(integration_id)
        if not integration:
            return None
        
        # Get latest job
        latest_job = self.get_latest_extraction_job(integration_id)
        
        # Get metadata stats if job exists
        metadata_stats = None
        if latest_job:
            metadata_stats = self.get_metadata_stats_by_job(latest_job['aej_id'])
        
        return {
            'integration': integration,
            'latest_job': latest_job,
            'metadata_stats': metadata_stats
        }
    
    def get_user_integrations_with_stats(self, user_id: int, org_id: int) -> List[Dict]:
        """Get all integrations for a user with their latest job stats"""
        integrations = self.get_integrations_by_org(org_id)
        
        result = []
        for integration in integrations:
            latest_job = self.get_latest_extraction_job(integration['i_id'])
            metadata_stats = None
            
            if latest_job:
                metadata_stats = self.get_metadata_stats_by_job(latest_job['aej_id'])
            
            result.append({
                'integration': integration,
                'latest_job': latest_job,
                'metadata_stats': metadata_stats
            })
        
        return result
    
    def search_metadata_components(self, org_id: int, search_term: str = None, 
                                 metadata_type_id: int = None) -> List[Dict]:
        """Search metadata components"""
        query = """
            SELECT amc.*, amt.amt_name as metadata_type_name, amt.amt_display_name
            FROM ids_audit_metadata_component amc
            LEFT JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
            WHERE amc.amc_org_id = %s AND amc.amc_status = 1
        """
        params = [org_id]
        
        if search_term:
            query += " AND (amc.amc_label ILIKE %s OR amc.amc_dev_name ILIKE %s OR amc.amc_content ILIKE %s)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if metadata_type_id:
            query += " AND amc.amc_metadata_type_id = %s"
            params.append(metadata_type_id)
        
        query += " ORDER BY amc.amc_created_timestamp DESC"
        return self.execute_query(query, tuple(params), fetch_all=True)
    
    def get_dashboard_data(self, integration_id: int) -> Dict:
        """Get complete dashboard data for an integration"""
        # Get integration with latest job
        integration_data = self.get_integration_with_latest_job(integration_id)
        if not integration_data:
            return None
        
        # Get metadata components if job exists
        components = []
        if integration_data['latest_job']:
            components = self.get_metadata_components_by_job(integration_data['latest_job']['aej_id'])
        
        return {
            'integration': integration_data['integration'],
            'latest_job': integration_data['latest_job'],
            'metadata_stats': integration_data['metadata_stats'],
            'metadata_components': components,
            'total_components': len(components)
        }
    
    # Dependency Management
    def create_dependency(self, org_id: int, from_component_id: int, to_component_id: int,
                         dependency_type: str, description: str, created_user_id: int) -> int:
        """Create a new dependency relationship"""
        query = """
            INSERT INTO ids_audit_metadata_dependency (
                amd_org_id, amd_from_component_id, amd_to_component_id, amd_dependency_type,
                amd_description, amd_created_user_id, amd_created_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING amd_id;
        """
        result = self.execute_query(query, (org_id, from_component_id, to_component_id, dependency_type, description, created_user_id), fetch_one=True)
        return result['amd_id'] if result else None
    
    def get_dependencies_for_component(self, component_id: int) -> List[Dict]:
        """Get all dependencies for a component"""
        query = """
            SELECT amd.*, 
                   from_comp.amc_label as from_label, from_comp.amc_dev_name as from_dev_name,
                   to_comp.amc_label as to_label, to_comp.amc_dev_name as to_dev_name
            FROM ids_audit_metadata_dependency amd
            JOIN ids_audit_metadata_component from_comp ON amd.amd_from_component_id = from_comp.amc_id
            JOIN ids_audit_metadata_component to_comp ON amd.amd_to_component_id = to_comp.amc_id
            WHERE (amd.amd_from_component_id = %s OR amd.amd_to_component_id = %s) 
            AND amd.amd_status = 1
            ORDER BY amd.amd_created_timestamp DESC
        """
        return self.execute_query(query, (component_id, component_id), fetch_all=True)
    
    # MyList Management
    def create_mylist(self, org_id: int, user_id: int, integration_id: int, name: str,
                     description: str, notes: str, created_user_id: int) -> int:
        """Create a new MyList record"""
        query = """
            INSERT INTO ids_audit_mylist (
                aml_org_id, aml_user_id, aml_integration_id, aml_name, aml_description,
                aml_notes, aml_created_user_id, aml_created_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING aml_id;
        """
        result = self.execute_query(query, (org_id, user_id, integration_id, name, description, notes, created_user_id), fetch_one=True)
        return result['aml_id'] if result else None
    
    def get_mylists_by_user(self, user_id: int, org_id: int) -> List[Dict]:
        """Get all MyLists for a user"""
        query = """
            SELECT aml.*, i.i_name as integration_name
            FROM ids_audit_mylist aml
            JOIN ids_integration i ON aml.aml_integration_id = i.i_id
            WHERE aml.aml_user_id = %s AND aml.aml_org_id = %s AND aml.aml_status = 1
            ORDER BY aml.aml_created_timestamp DESC
        """
        return self.execute_query(query, (user_id, org_id), fetch_all=True)
    
    def get_mylist(self, list_id: int) -> Optional[Dict]:
        """Get MyList by ID"""
        query = """
            SELECT aml.*, i.i_name as integration_name
            FROM ids_audit_mylist aml
            JOIN ids_integration i ON aml.aml_integration_id = i.i_id
            WHERE aml.aml_id = %s AND aml.aml_status = 1
        """
        return self.execute_query(query, (list_id,), fetch_one=True)
    
    # List Metadata Mappings
    def add_component_to_list(self, org_id: int, list_id: int, component_id: int,
                             notes: str, created_user_id: int) -> int:
        """Add a metadata component to a MyList"""
        query = """
            INSERT INTO ids_audit_list_metadata_mappings (
                almm_org_id, almm_list_id, almm_component_id, almm_notes,
                almm_created_user_id, almm_created_timestamp
            ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING almm_id;
        """
        result = self.execute_query(query, (org_id, list_id, component_id, notes, created_user_id), fetch_one=True)
        return result['almm_id'] if result else None
    
    def remove_component_from_list(self, list_id: int, component_id: int):
        """Remove a metadata component from a MyList"""
        query = """
            UPDATE ids_audit_list_metadata_mappings 
            SET almm_status = -1, almm_last_updated_timestamp = CURRENT_TIMESTAMP
            WHERE almm_list_id = %s AND almm_component_id = %s
        """
        self.execute_query(query, (list_id, component_id))
    
    def get_list_components(self, list_id: int) -> List[Dict]:
        """Get all components in a MyList"""
        query = """
            SELECT almm.*, amc.amc_id, amc.amc_label, amc.amc_dev_name, amc.amc_notes, amc.amc_content, 
                   amc.amc_ai_summary, amc.amc_ai_model, amc.amc_last_modified, amc.amc_api_version, 
                   amc.amc_created_timestamp, amt.amt_name as metadata_type_name, amt.amt_display_name, amt.amt_icon
            FROM ids_audit_list_metadata_mappings almm
            JOIN ids_audit_metadata_component amc ON almm.almm_component_id = amc.amc_id
            JOIN ids_audit_metadata_type amt ON amc.amc_metadata_type_id = amt.amt_id
            WHERE almm.almm_list_id = %s AND almm.almm_status = 1
            ORDER BY almm.almm_created_timestamp DESC
        """
        return self.execute_query(query, (list_id,), fetch_all=True)
    
    # Utility Methods
    def get_dependency_network(self, org_id: int, component_ids: List[int] = None) -> Dict:
        """Get dependency network data for visualization"""
        if component_ids:
            placeholders = ','.join(['%s'] * len(component_ids))
            query = f"""
                SELECT amd.*, 
                       from_comp.amc_label as from_label, from_comp.amc_dev_name as from_dev_name,
                       to_comp.amc_label as to_label, to_comp.amc_dev_name as to_dev_name
                FROM ids_audit_metadata_dependency amd
                JOIN ids_audit_metadata_component from_comp ON amd.amd_from_component_id = from_comp.amc_id
                JOIN ids_audit_metadata_component to_comp ON amd.amd_to_component_id = to_comp.amc_id
                WHERE amd.amd_org_id = %s 
                AND (amd.amd_from_component_id IN ({placeholders}) OR amd.amd_to_component_id IN ({placeholders}))
                AND amd.amd_status = 1
            """
            params = [org_id] + component_ids + component_ids
        else:
            query = """
                SELECT amd.*, 
                       from_comp.amc_label as from_label, from_comp.amc_dev_name as from_dev_name,
                       to_comp.amc_label as to_label, to_comp.amc_dev_name as to_dev_name
                FROM ids_audit_metadata_dependency amd
                JOIN ids_audit_metadata_component from_comp ON amd.amd_from_component_id = from_comp.amc_id
                JOIN ids_audit_metadata_component to_comp ON amd.amd_to_component_id = to_comp.amc_id
                WHERE amd.amd_org_id = %s AND amd.amd_status = 1
            """
            params = [org_id]
        
        dependencies = self.execute_query(query, tuple(params), fetch_all=True)
        
        # Build network data
        nodes = set()
        edges = []
        
        for dep in dependencies:
            nodes.add(dep['from_dev_name'])
            nodes.add(dep['to_dev_name'])
            edges.append({
                'from': dep['from_dev_name'],
                'to': dep['to_dev_name'],
                'type': dep['amd_dependency_type'],
                'description': dep['amd_description']
            })
        
        return {
            'nodes': [{'id': node, 'label': node} for node in nodes],
            'edges': edges
        }

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager 
