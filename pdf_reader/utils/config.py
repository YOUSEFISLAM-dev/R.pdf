"""
Configuration Utility Module

This module handles application configuration settings.
"""

import os
import json


class AppConfig:
    """
    Class for managing application configuration.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str): Optional path to config file
        """
        # Set default config file location
        if config_file is None:
            # Store in user's home directory
            home_dir = os.path.expanduser('~')
            self.config_file = os.path.join(home_dir, '.pdf_reader_config.json')
        else:
            self.config_file = config_file
        
        # Default configuration values
        self.defaults = {
            'theme': 'light',
            'zoom_level': 1.0,
            'recent_files_limit': 10,
            'startup_directory': '',
            'default_view': 'continuous',
            'show_thumbnails': True,
        }
        
        # Load configuration
        self.config = self.load()
    
    def load(self):
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration settings
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Return defaults if file doesn't exist
                return dict(self.defaults)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return dict(self.defaults)
    
    def save(self):
        """
        Save current configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Value for the key or default
        """
        if default is None and key in self.defaults:
            default = self.defaults[key]
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key
            value: Value to set
            
        Returns:
            bool: True if key was set, False otherwise
        """
        try:
            self.config[key] = value
            return True
        except Exception as e:
            print(f"Error setting configuration: {e}")
            return False
    
    def reset(self):
        """
        Reset configuration to defaults.
        
        Returns:
            bool: True if successful
        """
        self.config = dict(self.defaults)
        return self.save()
