import json
import logging

logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> dict:
    """
    Load JSON file and return the data as a dictionary.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Loaded JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            result = json.load(file)
            logger.info(f"Loaded JSON file from {file_path}")
            return result
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        raise
