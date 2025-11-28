"""Playwright-based web scraper for JavaScript-rendered pages."""
import logging
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


@tool
def scrape_page(url: str) -> str:
    """
    Fetch and render a webpage using Playwright.
    
    This handles JavaScript-rendered pages by loading them in a headless browser.
    
    IMPORTANT: Only use this for HTML pages. For direct file downloads
    (URLs ending in .pdf, .csv, .zip, etc.), use download_file instead.
    
    Args:
        url: The webpage URL to scrape
        
    Returns:
        The fully rendered HTML content
    """
    logger.info(f"Scraping page: {url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Load page and wait for network to be idle
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Get rendered HTML
            content = page.content()
            
            browser.close()
            
            logger.info(f"✓ Scraped {len(content)} chars from {url}")
            return content
            
    except PlaywrightTimeout:
        logger.error(f"Timeout loading {url}")
        return f"Error: Page load timeout for {url}"
    
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return f"Error scraping page: {str(e)}"
