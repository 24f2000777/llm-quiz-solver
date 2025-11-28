"""Python package installer tool."""
import logging
import subprocess
from typing import List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def install_package(packages: List[str]) -> str:
    """
    Install Python packages using pip.
    
    Allows the agent to dynamically install packages needed for quiz tasks.
    
    Args:
        packages: List of package names to install
        
    Returns:
        Success or error message
    """
    logger.info(f"Installing packages: {', '.join(packages)}")
    
    try:
        result = subprocess.run(
            ["pip", "install", "--quiet"] + packages,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Installed: {', '.join(packages)}")
            return f"Successfully installed: {', '.join(packages)}"
        else:
            logger.error(f"Installation failed: {result.stderr}")
            return f"Installation failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        logger.error("Installation timeout")
        return "Error: Installation timeout (120s)"
    
    except Exception as e:
        logger.error(f"Installation error: {e}")
        return f"Error: {str(e)}"
