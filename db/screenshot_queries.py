import sqlite3


def insertIntoScreenshotTable(db_path, screenshot_data):
    """
    Inserts a screenshot record into the screenshots table of the database.
    
    Parameters:
    db_path (str): The path to the database file.
    screenshot_data (dict): A dictionary containing screenshot information.
    """
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL command to insert screenshot data
    insert_query = '''
    INSERT INTO screenshots (timestamp, filepath, description)
    VALUES (?, ?, ?)
    '''
    
    # Execute the insert command
    cursor.execute(insert_query, (screenshot_data['timestamp'], screenshot_data['filepath'], screenshot_data['description']))
    
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

