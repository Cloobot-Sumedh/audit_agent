import psycopg2

DB_NAME = "cloobotx_testing"
DB_PASS = "NQpJSoB3OHlhT3YnAr55"
DB_USER = "azureusercloobotx"
DB_HOST = "cloobotx.postgres.database.azure.com"
DB_PORT = 5432

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO ids_integration (
            i_org_id,
            i_name,
            i_instance_url,
            i_org_type,
            i_token,
            i_ext_app_id,
            i_created_user_id,
            i_last_updated_user_id,
            i_last_updated_timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING i_id;
    """

    # Replace 1 with real IDs if needed
    values = (
        409,                              # i_org_id (must exist in ids_organisation)
        'Test Integration',            # i_name
        'https://test-instance.com',   # i_instance_url
        'demo-org',                    # i_org_type
        'fake-token-abc123',           # i_token
        1001,                          # i_ext_app_id
        243,                             # i_created_user_id (must exist in ids_users)
        243                              # i_last_updated_user_id (must exist in ids_users)
    )

    cursor.execute(insert_sql, values)
    new_id = cursor.fetchone()[0]
    print(f"✅ Inserted sample row with i_id = {new_id}")

except Exception as e:
    print(f"⚠️ Insert failed: {e}")
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()
