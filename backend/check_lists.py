import psycopg2

def check_lists():
    try:
        print("Connecting to database...")
        # Connect to database using the same config as database.py
        DB_CONFIG = {
            'dbname': '',
            'user': '',
            'password': '',
            'host': '',
            'port': 5432
        }
        
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected to database successfully")
        
        cursor = conn.cursor()
        
        # Check existing lists
        print("Checking existing lists...")
        cursor.execute("SELECT aml_id, aml_name, aml_user_id, aml_org_id FROM ids_audit_mylist ORDER BY aml_id")
        lists = cursor.fetchall()
        
        print("Available lists:")
        for list_item in lists:
            print(f"  List ID: {list_item[0]}, Name: {list_item[1]}, User ID: {list_item[2]}, Org ID: {list_item[3]}")
        
        # Check list components
        print("\nChecking list components...")
        cursor.execute("SELECT almm_list_id, almm_component_id FROM ids_audit_list_metadata_mappings ORDER BY almm_list_id")
        mappings = cursor.fetchall()
        
        print("List component mappings:")
        for mapping in mappings:
            print(f"  List ID: {mapping[0]}, Component ID: {mapping[1]}")
        
        cursor.close()
        conn.close()
        print("Database connection closed")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_lists() 
