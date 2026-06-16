# Personal Issue Resolver

An AI-powered system to track problems you encounter and get AI suggestions for similar past issues using semantic search.

## Features

- **Log Issues**: Track problems you encounter with context
- **Semantic Search**: Find similar past issues using RAG (embeddings)
- **View History**: See all logged issues and their status

## Tech Stack

- **Backend**: FastAPI + ChromaDB + Ollama
- **Frontend**: Flask
- **AI**: Semantic embeddings for smart search

## How to Run

### Prerequisites
- Ollama running: `ollama serve`
- ChromaDB server running

### Start Backend
```bash
uvicorn main:app --reload
```

### Start Frontend
```bash
python app.py
```

Then visit: `http://127.0.0.1:5000`

## Usage

1. **Log an issue**: Fill the form with your problem + context
2. **Search**: Enter a problem to find similar past issues
3. **View**: See all issues and their status

## TODO

- [ ] Fix resolve duplication bug
- [ ] Database persistence
- [ ] Production deployment

## Docker
docker tag personal-issue-resolver-flask:latest thejijogeorge/personal-issue-resolver-flask:latest
docker tag personal-issue-resolver-fastapi:latest thejijogeorge/personal-issue-resolver-fastapi:latest

docker push thejijogeorge/personal-issue-resolver-flask:latest
docker push thejijogeorge/personal-issue-resolver-fastapi:latest