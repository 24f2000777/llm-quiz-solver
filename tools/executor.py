"""Python code execution tool."""
import logging
import subprocess
from pathlib import Path
from langchain_core.tools import tool
from config import TEMP_DIR

logger = logging.getLogger(__name__)


@tool
def run_code(code: str) -> dict:
    """
    Execute Python code and return the output.
    
    The code is written to a temporary file and executed in isolation.
    Working directory is set to TEMP_DIR so downloaded files are accessible.
    
    Args:
        code: Python source code to execute
        
    Returns:
        Dictionary with stdout, stderr, and return_code
    """
    logger.info("Executing Python code")
    
    try:
        # Write code to temp file
        script_path = TEMP_DIR / "runner.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        # Execute with subprocess (timeout in communicate, not Popen)
        proc = subprocess.Popen(
            ["python3", "runner.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(TEMP_DIR)
        )
        
        # Timeout is applied here in communicate()
        try:
            stdout, stderr = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return {
                "stdout": stdout,
                "stderr": "Execution timeout after 120 seconds",
                "return_code": -1
            }
        
        result = {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": proc.returncode
        }
        
        if proc.returncode == 0:
            logger.info(f"✓ Code executed successfully")
            logger.info(f"Output: {stdout[:200]}")
        else:
            logger.warning(f"Code execution failed with code {proc.returncode}")
            logger.error(f"STDERR: {stderr}")
            logger.error(f"STDOUT: {stdout}")
        
        return result
        
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }
