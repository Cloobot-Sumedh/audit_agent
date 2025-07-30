

-- Salesforce Audit Agent Database Schema - Following IDS Naming Conventions
-- ============================================================================

-- 1. Integration table - Main integration configurations
CREATE TABLE ids_integration (
    i_id                      SERIAL PRIMARY KEY,
    i_org_id                  BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    i_name                    TEXT,
    i_instance_url            TEXT,
    i_org_type                TEXT,
    i_token                   TEXT,
    i_ext_app_id              INTEGER,
    i_created_user_id         BIGINT,
    i_created_timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    i_last_updated_user_id    BIGINT,
    i_last_updated_timestamp  TIMESTAMP,
    i_status                  INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_i_org_id
        FOREIGN KEY (i_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_i_created_user_id
        FOREIGN KEY (i_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_i_last_updated_user_id
        FOREIGN KEY (i_last_updated_user_id)
        REFERENCES ids_users(user_id)
);

-- 2. Audit Metadata Type table - Defines metadata types
CREATE TABLE ids_audit_metadata_type (
    amt_id                    SERIAL PRIMARY KEY,
    amt_org_id                BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    amt_name                  TEXT UNIQUE,
    amt_display_name          TEXT,
    amt_description           TEXT,
    amt_icon                  TEXT,
    amt_file_extension        TEXT,
    amt_created_user_id       BIGINT,
    amt_created_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amt_last_updated_user_id  BIGINT,
    amt_last_updated_timestamp TIMESTAMP,
    amt_status                INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_amt_org_id
        FOREIGN KEY (amt_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_amt_created_user_id
        FOREIGN KEY (amt_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_amt_last_updated_user_id
        FOREIGN KEY (amt_last_updated_user_id)
        REFERENCES ids_users(user_id)
);

-- 3. Audit Extraction Job table - Tracks extraction jobs
CREATE TABLE ids_audit_extraction_job (
    aej_id                    SERIAL PRIMARY KEY,
    aej_org_id                BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    aej_integration_id        BIGINT NOT NULL,
    aej_job_status            TEXT,
    aej_started_at            TIMESTAMP,
    aej_completed_at          TIMESTAMP,
    aej_total_files           INTEGER DEFAULT 0,
    aej_log                   TEXT,
    aej_job_data              JSONB,
    aej_created_user_id       BIGINT,
    aej_created_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    aej_last_updated_user_id  BIGINT,
    aej_last_updated_timestamp TIMESTAMP,
    aej_status                INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_aej_org_id
        FOREIGN KEY (aej_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_aej_integration_id
        FOREIGN KEY (aej_integration_id)
        REFERENCES ids_integration(i_id),

    CONSTRAINT fk_aej_created_user_id
        FOREIGN KEY (aej_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_aej_last_updated_user_id
        FOREIGN KEY (aej_last_updated_user_id)
        REFERENCES ids_users(user_id)
);

-- 4. Audit Metadata Component table - Stores metadata components
CREATE TABLE ids_audit_metadata_component (
    amc_id                    SERIAL PRIMARY KEY,
    amc_org_id                BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    amc_integration_id        BIGINT NOT NULL,
    amc_extraction_job_id     BIGINT,
    amc_metadata_type_id      BIGINT NOT NULL,
    amc_label                 TEXT,
    amc_dev_name              TEXT,
    amc_notes                 TEXT,
    amc_content               TEXT,
    amc_ai_summary            TEXT,
    amc_ai_model              TEXT,
    amc_last_modified         TIMESTAMP,
    amc_api_version           TEXT,
    amc_created_user_id       BIGINT,
    amc_created_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amc_last_updated_user_id  BIGINT,
    amc_last_updated_timestamp TIMESTAMP,
    amc_status                INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_amc_org_id
        FOREIGN KEY (amc_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_amc_integration_id
        FOREIGN KEY (amc_integration_id)
        REFERENCES ids_integration(i_id),

    CONSTRAINT fk_amc_extraction_job_id
        FOREIGN KEY (amc_extraction_job_id)
        REFERENCES ids_audit_extraction_job(aej_id),

    CONSTRAINT fk_amc_metadata_type_id
        FOREIGN KEY (amc_metadata_type_id)
        REFERENCES ids_audit_metadata_type(amt_id),

    CONSTRAINT fk_amc_created_user_id
        FOREIGN KEY (amc_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_amc_last_updated_user_id
        FOREIGN KEY (amc_last_updated_user_id)
        REFERENCES ids_users(user_id)
);

-- 5. Audit Metadata Dependency table - Tracks dependencies between components
CREATE TABLE ids_audit_metadata_dependency (
    amd_id                    SERIAL PRIMARY KEY,
    amd_org_id                BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    amd_from_component_id     BIGINT NOT NULL,
    amd_to_component_id       BIGINT NOT NULL,
    amd_dependency_type       TEXT,
    amd_description           TEXT,
    amd_created_user_id       BIGINT,
    amd_created_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amd_last_updated_user_id  BIGINT,
    amd_last_updated_timestamp TIMESTAMP,
    amd_status                INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_amd_org_id
        FOREIGN KEY (amd_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_amd_from_component_id
        FOREIGN KEY (amd_from_component_id)
        REFERENCES ids_audit_metadata_component(amc_id),

    CONSTRAINT fk_amd_to_component_id
        FOREIGN KEY (amd_to_component_id)
        REFERENCES ids_audit_metadata_component(amc_id),

    CONSTRAINT fk_amd_created_user_id
        FOREIGN KEY (amd_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_amd_last_updated_user_id
        FOREIGN KEY (amd_last_updated_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT uk_amd_dependency_relationship
        UNIQUE(amd_from_component_id, amd_to_component_id, amd_dependency_type),

    CONSTRAINT chk_amd_no_self_dependency
        CHECK (amd_from_component_id != amd_to_component_id)
);

-- 6. Audit MyList table - User-defined lists or favorites
CREATE TABLE ids_audit_mylist (
    aml_id                    SERIAL PRIMARY KEY,
    aml_org_id                BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    aml_user_id               BIGINT NOT NULL,
    aml_integration_id        BIGINT NOT NULL,
    aml_name                  TEXT,
    aml_description           TEXT,
    aml_notes                 TEXT,
    aml_created_user_id       BIGINT,
    aml_created_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    aml_last_updated_user_id  BIGINT,
    aml_last_updated_timestamp TIMESTAMP,
    aml_status                INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_aml_org_id
        FOREIGN KEY (aml_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_aml_user_id
        FOREIGN KEY (aml_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_aml_integration_id
        FOREIGN KEY (aml_integration_id)
        REFERENCES ids_integration(i_id),

    CONSTRAINT fk_aml_created_user_id
        FOREIGN KEY (aml_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_aml_last_updated_user_id
        FOREIGN KEY (aml_last_updated_user_id)
        REFERENCES ids_users(user_id)
);

-- 7. Audit List Metadata Mappings table - Maps metadata components to lists
CREATE TABLE ids_audit_list_metadata_mappings (
    almm_id                   SERIAL PRIMARY KEY,
    almm_org_id               BIGINT NOT NULL, -- Reference to ids_organisation.org_id
    almm_list_id              BIGINT NOT NULL,
    almm_component_id         BIGINT NOT NULL,
    almm_notes                TEXT,
    almm_created_user_id      BIGINT,
    almm_created_timestamp    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    almm_last_updated_user_id BIGINT,
    almm_last_updated_timestamp TIMESTAMP,
    almm_status               INTEGER DEFAULT 1, -- 1=active, -1=archived

    CONSTRAINT fk_almm_org_id
        FOREIGN KEY (almm_org_id)
        REFERENCES ids_organisation(org_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_almm_list_id
        FOREIGN KEY (almm_list_id)
        REFERENCES ids_audit_mylist(aml_id),

    CONSTRAINT fk_almm_component_id
        FOREIGN KEY (almm_component_id)
        REFERENCES ids_audit_metadata_component(amc_id),

    CONSTRAINT fk_almm_created_user_id
        FOREIGN KEY (almm_created_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT fk_almm_last_updated_user_id
        FOREIGN KEY (almm_last_updated_user_id)
        REFERENCES ids_users(user_id),

    CONSTRAINT uk_almm_list_component_mapping
        UNIQUE(almm_list_id, almm_component_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Integration table indexes
CREATE INDEX idx_i_org_id ON ids_integration(i_org_id);
CREATE INDEX idx_i_status ON ids_integration(i_status);
CREATE INDEX idx_i_created_timestamp ON ids_integration(i_created_timestamp);

-- Metadata type indexes
CREATE INDEX idx_amt_org_id ON ids_audit_metadata_type(amt_org_id);
CREATE INDEX idx_amt_status ON ids_audit_metadata_type(amt_status);

-- Extraction job indexes
CREATE INDEX idx_aej_org_id ON ids_audit_extraction_job(aej_org_id);
CREATE INDEX idx_aej_integration_id ON ids_audit_extraction_job(aej_integration_id);
CREATE INDEX idx_aej_job_status ON ids_audit_extraction_job(aej_job_status);
CREATE INDEX idx_aej_started_at ON ids_audit_extraction_job(aej_started_at);
CREATE INDEX idx_aej_status ON ids_audit_extraction_job(aej_status);

-- Metadata component indexes
CREATE INDEX idx_amc_org_id ON ids_audit_metadata_component(amc_org_id);
CREATE INDEX idx_amc_integration_id ON ids_audit_metadata_component(amc_integration_id);
CREATE INDEX idx_amc_metadata_type_id ON ids_audit_metadata_component(amc_metadata_type_id);
CREATE INDEX idx_amc_extraction_job_id ON ids_audit_metadata_component(amc_extraction_job_id);
CREATE INDEX idx_amc_dev_name ON ids_audit_metadata_component(amc_dev_name);
CREATE INDEX idx_amc_status ON ids_audit_metadata_component(amc_status);

-- Metadata dependency indexes
CREATE INDEX idx_amd_org_id ON ids_audit_metadata_dependency(amd_org_id);
CREATE INDEX idx_amd_from_component_id ON ids_audit_metadata_dependency(amd_from_component_id);
CREATE INDEX idx_amd_to_component_id ON ids_audit_metadata_dependency(amd_to_component_id);
CREATE INDEX idx_amd_status ON ids_audit_metadata_dependency(amd_status);

-- MyList indexes
CREATE INDEX idx_aml_org_id ON ids_audit_mylist(aml_org_id);
CREATE INDEX idx_aml_user_id ON ids_audit_mylist(aml_user_id);
CREATE INDEX idx_aml_integration_id ON ids_audit_mylist(aml_integration_id);
CREATE INDEX idx_aml_status ON ids_audit_mylist(aml_status);

-- List mappings indexes
CREATE INDEX idx_almm_org_id ON ids_audit_list_metadata_mappings(almm_org_id);
CREATE INDEX idx_almm_list_id ON ids_audit_list_metadata_mappings(almm_list_id);
CREATE INDEX idx_almm_component_id ON ids_audit_list_metadata_mappings(almm_component_id);
CREATE INDEX idx_almm_status ON ids_audit_list_metadata_mappings(almm_status);

-- ============================================================================
-- POSTGRESQL COMPATIBILITY & UPDATED FOREIGN KEY SUMMARY
-- ============================================================================
-- 
-- 
-- ORGANIZATION-LEVEL CASCADE BEHAVIOR:
-- - DELETE from ids_organisation will CASCADE DELETE all related audit data
-- - This provides clean organization-level data management
-- 
-- FOREIGN KEY RELATIONSHIPS (28 total):
-- 
-- CASCADE DELETE (org_id only - 7 relationships):
-- 1. ids_integration.i_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 2. ids_audit_metadata_type.amt_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 3. ids_audit_extraction_job.aej_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 4. ids_audit_metadata_component.amc_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 5. ids_audit_metadata_dependency.amd_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 6. ids_audit_mylist.aml_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 7. ids_audit_list_metadata_mappings.almm_org_id → ids_organisation.org_id ON DELETE CASCADE
-- 
-- STANDARD REFERENCES (no cascade - 21 relationships):
-- 8. ids_integration.i_created_user_id → ids_users.user_id
-- 9. ids_integration.i_last_updated_user_id → ids_users.user_id
-- 10. ids_audit_metadata_type.amt_created_user_id → ids_users.user_id
-- 11. ids_audit_metadata_type.amt_last_updated_user_id → ids_users.user_id
-- 12. ids_audit_extraction_job.aej_integration_id → ids_integration.i_id
-- 13. ids_audit_extraction_job.aej_created_user_id → ids_users.user_id
-- 14. ids_audit_extraction_job.aej_last_updated_user_id → ids_users.user_id
-- 15. ids_audit_metadata_component.amc_integration_id → ids_integration.i_id
-- 16. ids_audit_metadata_component.amc_extraction_job_id → ids_audit_extraction_job.aej_id
-- 17. ids_audit_metadata_component.amc_metadata_type_id → ids_audit_metadata_type.amt_id
-- 18. ids_audit_metadata_component.amc_created_user_id → ids_users.user_id
-- 19. ids_audit_metadata_component.amc_last_updated_user_id → ids_users.user_id
-- 20. ids_audit_metadata_dependency.amd_from_component_id → ids_audit_metadata_component.amc_id
-- 21. ids_audit_metadata_dependency.amd_to_component_id → ids_audit_metadata_component.amc_id
-- 22. ids_audit_metadata_dependency.amd_created_user_id → ids_users.user_id
-- 23. ids_audit_metadata_dependency.amd_last_updated_user_id → ids_users.user_id
-- 24. ids_audit_mylist.aml_user_id → ids_users.user_id
-- 25. ids_audit_mylist.aml_integration_id → ids_integration.i_id
-- 26. ids_audit_mylist.aml_created_user_id → ids_users.user_id
-- 27. ids_audit_mylist.aml_last_updated_user_id → ids_users.user_id
-- 28. ids_audit_list_metadata_mappings.almm_list_id → ids_audit_mylist.aml_id
-- 29. ids_audit_list_metadata_mappings.almm_component_id → ids_audit_metadata_component.amc_id
-- 30. ids_audit_list_metadata_mappings.almm_created_user_id → ids_users.user_id
-- 31. ids_audit_list_metadata_mappings.almm_last_updated_user_id → ids_users.user_id