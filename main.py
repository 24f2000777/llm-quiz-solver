"""FastAPI server for receiving quiz tasks."""
import asyncio
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import SECRET, AGENT_TIMEOUT
from agent import run_agent

logger = logging.getLogger(__name__)
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the app."""
    logger.info("🚀 Quiz Solver API starting up...")
    yield
    logger.info("👋 Quiz Solver API shutting down...")


app = FastAPI(
    title="LLM Quiz Solver",
    description="Autonomous agent for solving data science quizzes",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    uptime = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "uptime_seconds": uptime
    }


async def run_agent_with_timeout(url: str):
    """Run agent with timeout protection."""
    try:
        logger.info(f"Starting agent for URL: {url}")
        await asyncio.wait_for(
            asyncio.to_thread(run_agent, url),
            timeout=AGENT_TIMEOUT
        )
        logger.info(f"✅ Agent completed successfully for {url}")
    except asyncio.TimeoutError:
        logger.error(f"❌ Agent timeout ({AGENT_TIMEOUT}s) exceeded for {url}")
    except Exception as e:
        logger.error(f"❌ Agent error: {e}", exc_info=True)


@app.post("/solve")
async def solve_quiz(request: Request, background_tasks: BackgroundTasks):
    """
    Receive quiz task and start solving in background.
    
    Expected payload:
    {
        "email": "student@example.com",
        "secret": "your_secret",
        "url": "https://quiz-url.com/quiz-123"
    }
    """
    # Parse JSON
    try:
        data = await request.json()
    except Exception as e:
        logger.warning(f"Invalid JSON received: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Validate payload
    url = data.get("url")
    secret = data.get("secret")
    
    if not url or not secret:
        logger.warning("Missing url or secret in payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Verify secret
    if secret != SECRET:
        logger.warning(f"Invalid secret received from {data.get('email', 'unknown')}")
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Start background task
    logger.info(f"✓ Secret verified, queuing quiz: {url}")
    background_tasks.add_task(run_agent_with_timeout, url)
    
    return JSONResponse(status_code=200, content={"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://0.0.0.0:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
