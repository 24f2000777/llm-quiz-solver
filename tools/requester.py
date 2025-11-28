"""HTTP POST request tool for quiz submission."""
import logging
import json
from typing import Dict, Any
import requests
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def send_post(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a POST request with JSON payload to submit quiz answers.
    
    Implements smart retry logic:
    - If answer is wrong AND time < 180s: removes next URL to force retry
    - If time >= 180s: only returns next URL to skip to next question
    
    Args:
        url: The endpoint to POST to
        payload: JSON payload to send
        
    Returns:
        Server response as dictionary
    """
    logger.info(f"Sending POST to {url}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract key fields
        correct = data.get("correct", False)
        delay = data.get("delay", 0)
        delay = delay if isinstance(delay, (int, float)) else 0
        
        # Smart retry logic
        if not correct and delay < 180:
            # Wrong answer but time left - remove URL to force retry
            if "url" in data:
                logger.info(f"Wrong answer, time left ({delay}s) - will retry")
                del data["url"]
        
        if delay >= 180:
            # Time limit exceeded - only keep URL to move on
            logger.warning(f"Time limit exceeded ({delay}s) - moving to next question")
            data = {"url": data.get("url")}
        
        logger.info(f"Response: {json.dumps(data, indent=2)}")
        return data
        
    except requests.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        try:
            error_data = e.response.json()
        except:
            error_data = {"error": e.response.text}
        return error_data
    
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}
