# Vertex AI chat

![License](https://img.shields.io/github/license/leliw/vertex-ai-chat)
[![CI](https://github.com/leliw/vertex-ai-chat/actions/workflows/main.yml/badge.svg)](https://github.com/leliw/vertex-ai-chat/actions/workflows/main.yml)
![coverage badge](./backend/coverage.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-blue)
![Angular](https://img.shields.io/badge/Angular-18-brightgreen)

Chat application for general purposes usig `VertexAI` and `gemini-1.*` models.

## Changelog

For a detailed history of changes, please refer to the [CHANGELOG.md](CHANGELOG.md) file.

## Preparing environment

### Backend

```bash
cd backend
uv init . --python 3.12 --bare
uv venv --prompt vertex-ai-chat
source .venv/bin/activate
uv sync --dev
```

Create `backend/.env` file.

```.env
JWT_SECRET_KEY=
GOOGLE_APPLICATION_CREDENTIALS=
```

```bash
gcloud alpha firestore indexes composite create --project=vertex-ai-chat-dev --collection-group=KnowledgeBase --query-scope=COLLECTION --field-config=vector-config='{"dimension":"256","flat": "{}"}',field-path=embedding
```

## Testing

### Testing backend (python)

```bash
cd backend
pytest --cov=. tests/ --cov-report html
```

Report is gnerated as html here: `backend/htmlcov/index.html`.

## Running

The application is available at: [https://chat.hanse-intelli-tech.pl/](https://chat.hanse-intelli-tech.pl/)

### Running in develpment evironment

```bash
source ./run_dev.sh
```

To quit: press `Q` + `Enter`.
