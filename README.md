# Vertex AI chat

Chat application for general purposes usig `VertexAI` and `gemini-1.*` models.

## Changelog

For a detailed history of changes, please refer to the [CHANGELOG.md](CHANGELOG.md) file.

## Preparing environment

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
