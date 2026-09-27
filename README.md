# PocketSmart AI

PocketSmart AI is a FastAPI application that creates budget-aware plans for:

- Home interiors
- Parties and events
- Occasion jewelry

It supports Gemini-based structured recommendations, optional outfit-image
analysis, SQLite persistence, session authentication, JWT API authentication,
saved history, and deterministic fallback recommendations.

## Important data behavior

Marketplace links are search links. Prices and recommendations are estimates.
The application does not scrape or claim live marketplace inventory.

For verified prices and availability, integrate approved vendor or affiliate APIs.

## Requirements

- Python 3.11 or newer
- A Gemini API key for AI output
- No external database is needed for local development

## Setup

Create and activate a virtual environment:

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
