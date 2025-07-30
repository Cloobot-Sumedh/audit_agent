import psycopg2
import os

def check_users():
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
        
        # Check users
        print("Checking users...")
        cursor.execute("SELECT user_id, u_name FROM ids_users ORDER BY user_id")
        users = cursor.fetchall()
        
        print("Available users:")
        for user in users:
            print(f"  User ID: {user[0]}, Username: {user[1]}")
        
        # Check organizations
        print("Checking organizations...")
        cursor.execute("SELECT org_id, o_name FROM ids_organisation ORDER BY org_id")
        orgs = cursor.fetchall()
        
        print("\nAvailable organizations:")
        for org in orgs:
            print(f"  Org ID: {org[0]}, Name: {org[1]}")
        
        # Check integrations
        print("Checking integrations...")
        cursor.execute("SELECT i_id, i_name FROM ids_integration ORDER BY i_id")
        integrations = cursor.fetchall()
        
        print("\nAvailable integrations:")
        for integration in integrations:
            print(f"  Integration ID: {integration[0]}, Name: {integration[1]}")
        
        cursor.close()
        conn.close()
        print("Database connection closed")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users() 
