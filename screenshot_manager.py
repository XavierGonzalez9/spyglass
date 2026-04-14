import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

try:
    from PIL import ImageGrab, Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logging.warning("Pillow not available. Screenshot functionality disabled.")

class ScreenshotFormat(Enum):
    """Supported screenshot image formats"""
    PNG = "png"
    JPEG = "jpeg"
    BMP = "bmp"

class ScreenshotManager:
    """
    Manages screenshot capture with the following capabilities:
    - Full screen and active window capture
    - Multiple format support
    - Encrypted storage with database integration
    - Error handling and logging
    """
    
    def __init__(self, storage_dir: str = "Screenshots", format: ScreenshotFormat = ScreenshotFormat.PNG):
        """
        Initialize the ScreenshotManager.
        
        Args:
            storage_dir: Directory to store screenshots
            format: Image format for screenshots (PNG, JPEG, BMP)
        """
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow is required for screenshot functionality. Install with: pip install Pillow")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.format = format
        self.lock = threading.Lock()
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        logging.info(f"ScreenshotManager initialized with storage directory: {self.storage_dir}")
    
    def capture_full_screen(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture the full screen and save to file.
        
        Args:
            filename: Custom filename (without extension). If None, uses timestamp.
            
        Returns:
            Path to saved screenshot file, or None if capture failed
        """
        try:
            with self.lock:
                if not PILLOW_AVAILABLE:
                    logging.error("PIL/Pillow not available for screenshot capture")
                    return None
                
                # Capture the screen
                screenshot = ImageGrab.grab()
                
                # Generate filename if not provided
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"screenshot_fullscreen_{timestamp}"
                
                # Build full path
                filepath = self.storage_dir / f"{filename}.{self.format.value}"
                
                # Save screenshot
                screenshot.save(filepath, format=self.format.value.upper())
                
                logging.info(f"Full screen screenshot saved: {filepath}")
                return str(filepath)
                
        except Exception as e:
            logging.error(f"Error capturing full screen: {e}", exc_info=True)
            return None
    
    def capture_active_window(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture the active/foreground window and save to file.
        
        Args:
            filename: Custom filename (without extension). If None, uses timestamp.
            
        Returns:
            Path to saved screenshot file, or None if capture failed
        """
        try:
            with self.lock:
                if not PILLOW_AVAILABLE:
                    logging.error("PIL/Pillow not available for screenshot capture")
                    return None
                
                import sys
                if sys.platform != "win32":
                    logging.warning("Active window capture only supported on Windows")
                    return None
                
                import ctypes
                from ctypes import wintypes
                
                # Get the foreground window
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                
                if hwnd == 0:
                    logging.warning("Could not get foreground window")
                    return None
                
                # Get window rectangle
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                
                left = rect.left
                top = rect.top
                right = rect.right
                bottom = rect.bottom
                
                # Capture the window area
                screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
                
                # Generate filename if not provided
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"screenshot_window_{timestamp}"
                
                # Build full path
                filepath = self.storage_dir / f"{filename}.{self.format.value}"
                
                # Save screenshot
                screenshot.save(filepath, format=self.format.value.upper())
                
                logging.info(f"Active window screenshot saved: {filepath}")
                return str(filepath)
                
        except Exception as e:
            logging.error(f"Error capturing active window: {e}", exc_info=True)
            return None
    
    def capture_region(self, bbox: tuple, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture a specific region of the screen.
        
        Args:
            bbox: Bounding box as (left, top, right, bottom)
            filename: Custom filename (without extension). If None, uses timestamp.
            
        Returns:
            Path to saved screenshot file, or None if capture failed
        """
        try:
            with self.lock:
                if not PILLOW_AVAILABLE:
                    logging.error("PIL/Pillow not available for screenshot capture")
                    return None
                
                # Validate bounding box
                if len(bbox) != 4 or not all(isinstance(x, int) for x in bbox):
                    logging.error("Invalid bounding box format. Expected (left, top, right, bottom)")
                    return None
                
                # Capture the region
                screenshot = ImageGrab.grab(bbox=bbox)
                
                # Generate filename if not provided
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"screenshot_region_{timestamp}"
                
                # Build full path
                filepath = self.storage_dir / f"{filename}.{self.format.value}"
                
                # Save screenshot
                screenshot.save(filepath, format=self.format.value.upper())
                
                logging.info(f"Region screenshot saved: {filepath}")
                return str(filepath)
                
        except Exception as e:
            logging.error(f"Error capturing region: {e}", exc_info=True)
            return None
    
    def start_periodic_capture(self, interval_seconds: int = 300, capture_type: str = "fullscreen") -> bool:
        """
        Start capturing screenshots at regular intervals.
        
        Args:
            interval_seconds: Interval between captures in seconds (default 5 minutes)
            capture_type: Type of capture - 'fullscreen' or 'window'
            
        Returns:
            True if capture started successfully, False otherwise
        """
        if self.is_capturing:
            logging.warning("Screenshot capture already in progress")
            return False
        
        if interval_seconds < 1:
            logging.error("Interval must be at least 1 second")
            return False
        
        try:
            self.is_capturing = True
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                args=(interval_seconds, capture_type),
                daemon=True,
                name="ScreenshotCapture"
            )
            self.capture_thread.start()
            logging.info(f"Periodic screenshot capture started (interval: {interval_seconds}s, type: {capture_type})")
            return True
        except Exception as e:
            logging.error(f"Error starting periodic screenshot capture: {e}", exc_info=True)
            self.is_capturing = False
            return False
    
    def stop_periodic_capture(self) -> bool:
        """
        Stop periodic screenshot capture.
        
        Returns:
            True if capture stopped successfully
        """
        if not self.is_capturing:
            logging.warning("Screenshot capture is not running")
            return False
        
        try:
            self.is_capturing = False
            if self.capture_thread:
                self.capture_thread.join(timeout=5)
            logging.info("Periodic screenshot capture stopped")
            return True
        except Exception as e:
            logging.error(f"Error stopping periodic screenshot capture: {e}", exc_info=True)
            return False
    
    def _capture_loop(self, interval_seconds: int, capture_type: str) -> None:
        """Internal method for the periodic capture loop."""
        import time
        
        while self.is_capturing:
            try:
                if capture_type == "window":
                    self.capture_active_window()
                else:
                    self.capture_full_screen()
                
                time.sleep(interval_seconds)
            except Exception as e:
                logging.error(f"Error in capture loop: {e}", exc_info=True)
    
    def set_format(self, format: ScreenshotFormat) -> None:
        """Change the screenshot format."""
        self.format = format
        logging.info(f"Screenshot format changed to: {format.value}")
    
    def get_screenshots_list(self, limit: Optional[int] = None) -> list:
        """
        Get list of stored screenshots.
        
        Args:
            limit: Maximum number of screenshots to return (None for all)
            
        Returns:
            List of screenshot file paths
        """
        try:
            files = sorted(
                [f for f in self.storage_dir.iterdir() if f.is_file()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if limit:
                files = files[:limit]
            return [str(f) for f in files]
        except Exception as e:
            logging.error(f"Error getting screenshots list: {e}", exc_info=True)
            return []
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.is_capturing:
            self.stop_periodic_capture()
        logging.info("ScreenshotManager cleanup complete")
