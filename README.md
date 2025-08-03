## API Usage

### Ingest Email
```bash
curl -X POST https://genv-backend-mvp.vercel.app/ingest_email \
  -H "Content-Type: application/json" \
  -d '{
        "client_id": "abc123",
        "email_id": "email789",
        "subject": "New message from John",
        "thread_id": "thread456",
        "category": "inquiry",
        "body_excerpt": "Hi, I would like to ask about...",
        "name": "John Doe",
        "email_address": "john@example.com"
      }'
```

```bash
curl -X POST http://127.0.0.1:8000/ingest_email \
  -H "Content-Type: application/json" \
  -d '{
        "client_id": "abc123",
        "email_id": "email789",
        "subject": "New message from John",
        "thread_id": "thread456",
        "category": "inquiry",
        "body_excerpt": "Hi, I would like to ask about...",
        "name": "John Doe",
        "email_address": "john@example.com"
      }'
```

### Get All Emails

```bash       
curl -X GET "https://genv-backend-mvp.vercel.app/emails" -H "accept: application/json" 
```

```bash
curl -X GET "http://localhost:8000/emails" -H "accept: application/json"
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the latest emails?",
    "verbose": true
  }'
```

```bash
curl -X POST https://genv-backend-mvp.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the latest emails?",
    "verbose": true
  }'
```

### Health Check

```bash
curl -X GET "http://localhost:8000/health" -H "accept: application/json"
```

```bash
curl -X GET "https://genv-backend-mvp.vercel.app/health" -H "accept: application/json"
```

### Execute Cypher Query

```bash
curl -X POST http://localhost:8000/cypher \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (e:Email) RETURN e LIMIT 5"
  }'
```

```bash
curl -X POST https://genv-backend-mvp.vercel.app/cypher \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (e:Email) RETURN e LIMIT 5"
  }'
```

### Get Database Schema

```bash
curl -X GET "http://localhost:8000/schema" -H "accept: application/json"
```

```bash
curl -X GET "https://genv-backend-mvp.vercel.app/schema" -H "accept: application/json"
```

### Get Database Statistics

```bash
curl -X GET "http://localhost:8000/stats" -H "accept: application/json"
```

```bash
curl -X GET "https://genv-backend-mvp.vercel.app/stats" -H "accept: application/json"
```

### Update Node Properties

```bash
curl -X POST http://localhost:8000/update-node \
  -H "Content-Type: application/json" \
  -d '{
    "match_properties": {"email_id": "email789"},
    "set_properties": {"status": "processed", "priority": "high"}
  }'
```

```bash
curl -X POST https://genv-backend-mvp.vercel.app/update-node \
  -H "Content-Type: application/json" \
  -d '{
    "match_properties": {"email_id": "email789"},
    "set_properties": {"status": "processed", "priority": "high"}
  }'
```
