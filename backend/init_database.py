#!/usr/bin/env python3
"""
Database initialization script for Salesforce Audit Agent
Sets up default metadata types and tests database connectivity
"""

from database import get_db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with default metadata types"""
    
    db = get_db_manager()
    
    try:
        # Test database connection
        logger.info("Testing database connection...")
        conn = db.get_connection()
        logger.info("✅ Database connection successful!")
        
        # Default metadata types for Salesforce - COMPREHENSIVE LIST
        default_metadata_types = [
            {
                'name': 'ApexClass',
                'display_name': 'Apex Classes',
                'description': 'Custom business logic and controllers written in Apex',
                'icon': '⚡',
                'file_extension': '.cls'
            },
            {
                'name': 'ApexTrigger',
                'display_name': 'Apex Triggers',
                'description': 'Event-driven code execution for data operations',
                'icon': '🔄',
                'file_extension': '.trigger'
            },
            {
                'name': 'ApexPage',
                'display_name': 'Visualforce Pages',
                'description': 'Custom user interface pages and components',
                'icon': '📄',
                'file_extension': '.page'
            },
            {
                'name': 'ApexComponent',
                'display_name': 'Visualforce Components',
                'description': 'Reusable UI components for Visualforce pages',
                'icon': '🧩',
                'file_extension': '.component'
            },
            {
                'name': 'CustomObject',
                'display_name': 'Custom Objects',
                'description': 'Custom data structures and fields for business entities',
                'icon': '📦',
                'file_extension': '.object'
            },
            {
                'name': 'CustomField',
                'display_name': 'Custom Fields',
                'description': 'Custom field definitions for objects',
                'icon': '🏷️',
                'file_extension': '.field'
            },
            {
                'name': 'Flow',
                'display_name': 'Flows',
                'description': 'Business process automation and workflow rules',
                'icon': '🔀',
                'file_extension': '.flow'
            },
            {
                'name': 'Layout',
                'display_name': 'Layouts',
                'description': 'Page and record layouts for user interface',
                'icon': '📋',
                'file_extension': '.layout'
            },
            {
                'name': 'ValidationRule',
                'display_name': 'Validation Rules',
                'description': 'Data validation rules for fields and records',
                'icon': '✅',
                'file_extension': '.validationRule'
            },
            {
                'name': 'WorkflowRule',
                'display_name': 'Workflow Rules',
                'description': 'Automated business processes and field updates',
                'icon': '⚙️',
                'file_extension': '.workflow'
            },
            {
                'name': 'PermissionSet',
                'display_name': 'Permission Sets',
                'description': 'User access and permission configurations',
                'icon': '🔐',
                'file_extension': '.permissionset'
            },
            {
                'name': 'Profile',
                'display_name': 'Profiles',
                'description': 'User profile configurations and permissions',
                'icon': '👤',
                'file_extension': '.profile'
            },
            {
                'name': 'Role',
                'display_name': 'Roles',
                'description': 'User role hierarchy and access control',
                'icon': '👑',
                'file_extension': '.role'
            },
            {
                'name': 'Group',
                'display_name': 'Groups',
                'description': 'User groups for sharing and collaboration',
                'icon': '👥',
                'file_extension': '.group'
            },
            {
                'name': 'Queue',
                'display_name': 'Queues',
                'description': 'Work queues for case and lead management',
                'icon': '📥',
                'file_extension': '.queue'
            },
            {
                'name': 'CustomTab',
                'display_name': 'Custom Tabs',
                'description': 'Custom navigation tabs for applications',
                'icon': '📑',
                'file_extension': '.tab'
            },
            {
                'name': 'CustomApplication',
                'display_name': 'Custom Applications',
                'description': 'Custom application definitions and configurations',
                'icon': '📱',
                'file_extension': '.app'
            },
            {
                'name': 'CustomPermission',
                'display_name': 'Custom Permissions',
                'description': 'Custom permission definitions for access control',
                'icon': '🔑',
                'file_extension': '.customPermission'
            },
            {
                'name': 'CustomMetadata',
                'display_name': 'Custom Metadata',
                'description': 'Custom metadata type records and configurations',
                'icon': '🗂️',
                'file_extension': '.customMetadata'
            },
            {
                'name': 'CustomLabel',
                'display_name': 'Custom Labels',
                'description': 'Custom label definitions for multi-language support',
                'icon': '🏷️',
                'file_extension': '.labels'
            },
            {
                'name': 'CustomSite',
                'display_name': 'Custom Sites',
                'description': 'Custom Salesforce sites and communities',
                'icon': '🌐',
                'file_extension': '.site'
            },
            {
                'name': 'CustomWebLink',
                'display_name': 'Custom Web Links',
                'description': 'Custom web link buttons and actions',
                'icon': '🔗',
                'file_extension': '.weblink'
            },
            {
                'name': 'Dashboard',
                'display_name': 'Dashboards',
                'description': 'Analytics dashboards and reports',
                'icon': '📊',
                'file_extension': '.dashboard'
            },
            {
                'name': 'Document',
                'display_name': 'Documents',
                'description': 'Document storage and file management',
                'icon': '📄',
                'file_extension': '.document'
            },
            {
                'name': 'EmailTemplate',
                'display_name': 'Email Templates',
                'description': 'Email template definitions and content',
                'icon': '📧',
                'file_extension': '.email'
            },
            {
                'name': 'FlexiPage',
                'display_name': 'FlexiPages',
                'description': 'Lightning page layouts and components',
                'icon': '📱',
                'file_extension': '.flexipage'
            },
            {
                'name': 'GlobalValueSet',
                'display_name': 'Global Value Sets',
                'description': 'Global picklist value definitions',
                'icon': '📋',
                'file_extension': '.globalValueSet'
            },
            {
                'name': 'ListView',
                'display_name': 'List Views',
                'description': 'Custom list view definitions for objects',
                'icon': '📋',
                'file_extension': '.listView'
            },
            {
                'name': 'NamedCredential',
                'display_name': 'Named Credentials',
                'description': 'External system authentication credentials',
                'icon': '🔐',
                'file_extension': '.namedCredential'
            },
            {
                'name': 'Network',
                'display_name': 'Networks',
                'description': 'Salesforce community and network configurations',
                'icon': '🌐',
                'file_extension': '.network'
            },
            {
                'name': 'QuickAction',
                'display_name': 'Quick Actions',
                'description': 'Custom quick action buttons and processes',
                'icon': '⚡',
                'file_extension': '.quickAction'
            },
            {
                'name': 'Report',
                'display_name': 'Reports',
                'description': 'Analytics report definitions and configurations',
                'icon': '📈',
                'file_extension': '.report'
            },
            {
                'name': 'ReportType',
                'display_name': 'Report Types',
                'description': 'Report type definitions and field configurations',
                'icon': '📊',
                'file_extension': '.reportType'
            },
            {
                'name': 'StaticResource',
                'display_name': 'Static Resources',
                'description': 'Static files and assets for applications',
                'icon': '📁',
                'file_extension': '.resource'
            },
            {
                'name': 'SharingRules',
                'display_name': 'Sharing Rules',
                'description': 'Data sharing and access control rules',
                'icon': '🤝',
                'file_extension': '.sharingRules'
            },
            {
                'name': 'WorkflowAlert',
                'display_name': 'Workflow Alerts',
                'description': 'Workflow email alert configurations',
                'icon': '📢',
                'file_extension': '.workflowAlert'
            },
            {
                'name': 'WorkflowFieldUpdate',
                'display_name': 'Workflow Field Updates',
                'description': 'Automated field update configurations',
                'icon': '🔄',
                'file_extension': '.workflowFieldUpdate'
            },
            {
                'name': 'WorkflowTask',
                'display_name': 'Workflow Tasks',
                'description': 'Automated task creation configurations',
                'icon': '📝',
                'file_extension': '.workflowTask'
            },
            {
                'name': 'WorkflowSend',
                'display_name': 'Workflow Sends',
                'description': 'Workflow outbound message configurations',
                'icon': '📤',
                'file_extension': '.workflowSend'
            },
            {
                'name': 'WorkflowOutboundMessage',
                'display_name': 'Workflow Outbound Messages',
                'description': 'Workflow outbound message configurations',
                'icon': '📤',
                'file_extension': '.workflowOutboundMessage'
            },
            {
                'name': 'WorkflowKnowledgePublish',
                'display_name': 'Workflow Knowledge Publish',
                'description': 'Knowledge article publishing workflows',
                'icon': '📚',
                'file_extension': '.workflowKnowledgePublish'
            },
            {
                'name': 'WaveApplication',
                'display_name': 'Wave Applications',
                'description': 'Einstein Analytics application configurations',
                'icon': '📊',
                'file_extension': '.waveApplication'
            },
            {
                'name': 'WaveDashboard',
                'display_name': 'Wave Dashboards',
                'description': 'Einstein Analytics dashboard configurations',
                'icon': '📈',
                'file_extension': '.waveDashboard'
            },
            {
                'name': 'WaveDataflow',
                'display_name': 'Wave Dataflows',
                'description': 'Einstein Analytics data transformation flows',
                'icon': '🔄',
                'file_extension': '.waveDataflow'
            },
            {
                'name': 'WaveDataset',
                'display_name': 'Wave Datasets',
                'description': 'Einstein Analytics dataset configurations',
                'icon': '📊',
                'file_extension': '.waveDataset'
            },
            {
                'name': 'WaveLens',
                'display_name': 'Wave Lenses',
                'description': 'Einstein Analytics lens configurations',
                'icon': '🔍',
                'file_extension': '.waveLens'
            },
            {
                'name': 'WaveRecipe',
                'display_name': 'Wave Recipes',
                'description': 'Einstein Analytics data preparation recipes',
                'icon': '📋',
                'file_extension': '.waveRecipe'
            },
            {
                'name': 'WaveSpoke',
                'display_name': 'Wave Spokes',
                'description': 'Einstein Analytics spoke configurations',
                'icon': '🔗',
                'file_extension': '.waveSpoke'
            },
            {
                'name': 'WaveXmd',
                'display_name': 'Wave XMD',
                'description': 'Einstein Analytics extended metadata',
                'icon': '📄',
                'file_extension': '.waveXmd'
            }
        ]
        
        # Check if metadata types already exist
        existing_types = db.get_metadata_types(org_id=409)  # Using org_id from test_db.py
        
        if existing_types:
            logger.info(f"Found {len(existing_types)} existing metadata types")
            return
        
        # Create default metadata types
        logger.info("Creating default metadata types...")
        created_count = 0
        
        for metadata_type in default_metadata_types:
            try:
                type_id = db.create_metadata_type(
                    org_id=409,  # Using org_id from test_db.py
                    name=metadata_type['name'],
                    display_name=metadata_type['display_name'],
                    description=metadata_type['description'],
                    icon=metadata_type['icon'],
                    file_extension=metadata_type['file_extension'],
                    created_user_id=243  # Using user_id from test_db.py
                )
                
                if type_id:
                    created_count += 1
                    logger.info(f"✅ Created metadata type: {metadata_type['name']}")
                else:
                    logger.error(f"❌ Failed to create metadata type: {metadata_type['name']}")
                    
            except Exception as e:
                logger.error(f"❌ Error creating metadata type {metadata_type['name']}: {e}")
        
        logger.info(f"🎉 Database initialization complete! Created {created_count} metadata types.")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        db.close_connection()

def test_database_operations():
    """Test various database operations"""
    
    db = get_db_manager()
    
    try:
        logger.info("Testing database operations...")
        
        # Test integration creation
        integration_id = db.create_integration(
            org_id=409,
            name="Test Integration",
            instance_url="https://test-instance.com",
            org_type="demo-org",
            token="test-token",
            ext_app_id=1001,
            created_user_id=243
        )
        logger.info(f"✅ Created test integration with ID: {integration_id}")
        
        # Test extraction job creation
        job_id = db.create_extraction_job(
            org_id=409,
            integration_id=integration_id,
            job_status="running",
            total_files=0,
            created_user_id=243
        )
        logger.info(f"✅ Created test extraction job with ID: {job_id}")
        
        # Test metadata component creation
        component_id = db.create_metadata_component(
            org_id=409,
            integration_id=integration_id,
            extraction_job_id=job_id,
            metadata_type_id=1,  # Assuming ApexClass type exists
            label="TestClass",
            dev_name="TestClass",
            notes="Test component",
            content="public class TestClass { }",
            ai_summary="Test Apex class for demonstration",
            ai_model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            last_modified=None,
            api_version="62.0",
            created_user_id=243
        )
        logger.info(f"✅ Created test metadata component with ID: {component_id}")
        
        # Test retrieval operations
        integration = db.get_integration(integration_id)
        logger.info(f"✅ Retrieved integration: {integration['i_name']}")
        
        job = db.get_extraction_job(job_id)
        logger.info(f"✅ Retrieved extraction job: {job['aej_job_status']}")
        
        component = db.get_metadata_component(component_id)
        logger.info(f"✅ Retrieved metadata component: {component['amc_label']}")
        
        logger.info("🎉 All database operations test successful!")
        
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        raise
    finally:
        db.close_connection()

if __name__ == "__main__":
    print("🚀 Initializing Salesforce Audit Agent Database...")
    
    try:
        # Initialize database with default metadata types
        init_database()
        
        # Test database operations
        test_database_operations()
        
        print("✅ Database initialization and testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        exit(1) 