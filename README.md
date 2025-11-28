# LLM Quiz Solver 🤖

Autonomous agent that solves multi-step data science quizzes using LangGraph and Google Gemini.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✅ **Autonomous multi-step solving** - Chains through multiple quiz pages  
✅ **JavaScript rendering** - Uses Playwright for dynamic pages  
✅ **Code execution** - Runs Python for data analysis  
✅ **Smart retry logic** - Handles wrong answers within time limits  
✅ **Timeout protection** - 10-minute max per quiz chain  
✅ **Proper logging** - Track every step  
✅ **Docker ready** - Deploy to HuggingFace Spaces or anywhere  

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repo
git clone <your-repo-url>
cd llm-quiz-solver

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
# - EMAIL: Your email from Google Form
# - SECRET: Your secret string from Google Form  
# - GOOGLE_API_KEY: Get from https://aistudio.google.com/app/apikey
```

### 3. Run Server

```bash
python main.py
```

Server starts at `http://0.0.0.0:7860`

### 4. Test It

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected response: `{"status": "ok"}`

Check logs to see the agent solving the quiz!

## How It Works

```
POST /solve → Validate Secret → Background Task
                                      ↓
                              LangGraph Agent
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
              Agent Node                          Tool Node
           (LLM Reasoning)                    (Execute Tools)
                    ↓                                   ↓
            ┌───────┴────────┐                 ┌────────┴────────┐
            │ Load quiz page │                 │ scrape_page     │
            │ Parse task     │                 │ download_file   │
            │ Plan solution  │                 │ run_code        │
            │ Check response │                 │ send_post       │
            └───────┬────────┘                 │ install_package │
                    │                          └────────┬────────┘
                    └──────────────┬───────────────────┘
                                   ↓
                          Loop until END signal
```

## Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `scrape_page` | Render JS pages with Playwright | Fetch quiz instructions |
| `download_file` | Download files to temp directory | Get CSV/PDF data files |
| `run_code` | Execute Python code (120s timeout) | Analyze data, compute answer |
| `send_post` | Submit answers via HTTP POST | Post to quiz endpoint |
| `install_package` | Install Python packages on-the-fly | Add pandas, beautifulsoup4 |

## Configuration

Edit `config.py` to adjust:

- `RECURSION_LIMIT`: Max steps in quiz chain (default: 200)
- `AGENT_TIMEOUT`: Max time per quiz chain (default: 600s)
- `LLM_RATE_LIMIT`: Gemini requests/minute (default: 9/60)

## Docker Deployment

### Build & Run Locally

```bash
docker build -t quiz-solver .
docker run -p 7860:7860 \
  -e EMAIL="your@email.com" \
  -e SECRET="your_secret" \
  -e GOOGLE_API_KEY="your_api_key" \
  quiz-solver
```

### Deploy to HuggingFace Spaces

1. Create new Space with Docker SDK
2. Push this repo to the Space
3. Add secrets in Space settings:
   - `EMAIL`
   - `SECRET`
   - `GOOGLE_API_KEY`
4. Space auto-builds and deploys

## API Reference

### `POST /solve`

Receive quiz task and start solving.

**Request:**
```json
{
  "email": "your@email.com",
  "secret": "your_secret",
  "url": "https://quiz-url.com/quiz-123"
}
```

**Response:**
- `200`: Secret verified, agent started
- `400`: Invalid JSON
- `403`: Invalid secret

### `GET /healthz`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "uptime_seconds": 3600
}
```

## Project Structure

```
llm-quiz-solver/
├── main.py              # FastAPI server
├── agent.py             # LangGraph orchestrator
├── config.py            # Centralized configuration
├── tools/
│   ├── scraper.py       # Playwright scraper
│   ├── downloader.py    # File downloader
│   ├── executor.py      # Code runner
│   ├── requester.py     # HTTP POST
│   └── installer.py     # Package installer
├── Dockerfile           # Container setup
├── pyproject.toml       # Dependencies
└── README.md
```

## Troubleshooting

**Agent times out:**
- Increase `AGENT_TIMEOUT` in `config.py`
- Check Gemini API rate limits

**Code execution fails:**
- Check if required packages are installed
- Use `install_package` tool to add dependencies

**Playwright errors:**
- Run `playwright install chromium`
- Ensure system dependencies are installed (see Dockerfile)

**Wrong answers:**
- Check logs for parsing errors
- Verify quiz page HTML structure
- Test code execution locally

## License

MIT License - see [LICENSE](LICENSE) file

## Author

Built for TDS (Tools in Data Science) course project
