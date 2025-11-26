"""
Configuration loader for YAML files.
"""

import yaml
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and saves YAML configuration files."""
    
    @staticmethod
    def load_yaml(file_path: Path) -> Dict[str, Any]:
        """
        Load YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
                if data is None:
                    return {}
                return data
            except yaml.YAMLError as e:
                logger.error(f"Invalid YAML in {file_path}: {e}")
                raise
    
    @staticmethod
    def save_yaml(file_path: Path, data: Dict[str, Any]) -> None:
        """
        Save data to YAML file.
        
        Args:
            file_path: Path to save YAML file
            data: Dictionary to save
        """
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120
            )

