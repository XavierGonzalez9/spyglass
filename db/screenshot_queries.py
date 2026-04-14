"""Database query utilities for screenshot operations."""

from typing import Optional, List, Dict
import logging
from db.database import getDB


def insertIntoScreenshotTable(eventID: int, imagePath: str) -> bool:
    """
    Insert screenshot record into the encrypted database.
    
    Args:
        eventID: Event ID to associate with screenshot
        imagePath: Path to the screenshot file
        
    Returns:
        True if successful, False otherwise
    """
    db = getDB()
    if not db or not db.connection:
        logging.error("Database connection not available for screenshot insertion")
        return False
    
    try:
        cursor = db.connection.cursor()
        cursor.execute(
            """INSERT INTO screenshot (eventID, imagePath, capturedAt) 
               VALUES (?, ?, datetime('now'))""",
            (eventID, imagePath)
        )
        db.connection.commit()
        cursor.close()
        logging.info(f"Screenshot inserted into database: {imagePath}")
        return True
    except Exception as e:
        logging.error(f"Error inserting screenshot into database: {e}", exc_info=True)
        return False


def getScreenshots(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Get recent screenshots for a user from the database.
    
    Args:
        user_id: User ID
        limit: Maximum number of screenshots to return
        
    Returns:
        List of screenshot records
    """
    db = getDB()
    if not db or not db.connection:
        logging.error("Database connection not available for screenshot retrieval")
        return []
    
    try:
        cursor = db.connection.cursor()
        cursor.execute(
            """SELECT s.screenshotID, s.imagePath, s.capturedAt, a.action
               FROM screenshot s
               JOIN activity_log a ON s.eventID = a.eventID
               WHERE a.userID = ?
               ORDER BY s.capturedAt DESC
               LIMIT ?""",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        cursor.close()
        
        screenshots = []
        for row in rows:
            screenshots.append({
                'screenshotID': row[0],
                'imagePath': row[1],
                'capturedAt': row[2],
                'action': row[3]
            })
        
        logging.info(f"Retrieved {len(screenshots)} screenshots for user {user_id}")
        return screenshots
    except Exception as e:
        logging.error(f"Error retrieving screenshots from database: {e}", exc_info=True)
        return []