"""
Recent Files Management Module

This module handles tracking and managing recently opened files.
"""

import os
import json


class RecentFiles:
    """
    Class for managing a list of recently opened files.
    """
    
    def __init__(self, max_files=10, storage_file=None):
        """
        Initialize the recent files manager.
        
        Args:
            max_files (int): Maximum number of files to track
            storage_file (str): Optional path to storage file
        """
        self.max_files = max_files
        
        # Set default storage file location
        if storage_file is None:
            # Store in user's home directory
            home_dir = os.path.expanduser('~')
            self.storage_file = os.path.join(home_dir, '.pdf_reader_recent.json')
        else:
            self.storage_file = storage_file
        
        # Load recent files
        self.files = self.load()
    
    def load(self):
        """
        Load the list of recent files from storage.
        
        Returns:
            list: List of file paths
        """
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    files = json.load(f)
                    
                    # Filter out files that no longer exist
                    return [f for f in files if os.path.exists(f)]
            else:
                return []
        except Exception as e:
            print(f"Error loading recent files: {e}")
            return []
    
    def save(self):
        """
        Save the current list of recent files to storage.
        
        Returns:
            bool: True if successful
        """
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.files, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving recent files: {e}")
            return False
    
    def add(self, file_path):
        """
        Add a file to the recent files list.
        
        Args:
            file_path (str): Path to the file to add
            
        Returns:
            bool: True if the file was added or moved to top
        """
        # Normalize path
        file_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False
        
        # Remove if already in the list (will be re-added at top)
        if file_path in self.files:
            self.files.remove(file_path)
        
        # Add to the beginning of the list
        self.files.insert(0, file_path)
        
        # Trim list to max size
        self.files = self.files[:self.max_files]
        
        # Save changes
        self.save()
        return True
    
    def remove(self, file_path):
        """
        Remove a file from the recent files list.
        
        Args:
            file_path (str): Path to the file to remove
            
        Returns:
            bool: True if the file was removed
        """
        # Normalize path
        file_path = os.path.abspath(file_path)
        
        # Remove if in the list
        if file_path in self.files:
            self.files.remove(file_path)
            self.save()
            return True
        return False
    
    def clear(self):
        """
        Clear the recent files list.
        
        Returns:
            bool: True if successful
        """
        self.files = []
        return self.save()
    
    def get_list(self):
        """
        Get the list of recent files.
        
        Returns:
            list: List of file paths
        """
        return self.files
