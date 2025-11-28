"""File downloader tool."""
import logging
from pathlib import Path
import requests
from langchain_core.tools import tool
from config import TEMP_DIR

logger = logging.getLogger(__name__)


@tool
def download_file(url: str, filename: str) -> str:
    """
    Download a file from a URL and save it to the temp directory.
    
    Args:
        url: Direct URL to the file
        filename: Name to save the file as
        
    Returns:
        The full path to the saved file
    """
    logger.info(f"Downloading {filename} from {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        filepath = TEMP_DIR / filename
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"✓ Downloaded to {filepath}")
        return filename
        
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return f"Error downloading file: {str(e)}"
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: {str(e)}"
