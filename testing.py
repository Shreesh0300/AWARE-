import sqlite3

def search_aware_db():
    print("🔍 A.W.A.R.E. Database Search Terminal")
    print("Type 'quit' to close the program.\n")
    
    # 1. Connect to the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    while True:
        # 2. Get the search term from you
        query = input("Enter a medical term to search: ")
        
        if query.lower() == 'quit':
            break
            
        print(f"\nScanning 16 million characters for '{query}'...")
        
        # 3. Search the table (LIMIT 3 so it doesn't flood your screen)
        cursor.execute("SELECT text_chunk FROM medical_data WHERE text_chunk LIKE ? LIMIT 3", ('%' + query + '%',))
        results = cursor.fetchall()
        
        # 4. Display the results
        if not results:
            print("❌ No matches found. Try another term.\n")
        else:
            for i, row in enumerate(results):
                print(f"\n--- CHUNK {i+1} ---")
                print(row[0])
            print("-" * 40 + "\n")
                    
    # 5. Clean up when you quit
    conn.close()
    print("Search terminal closed.")

if __name__ == "__main__":
    search_aware_db()