## API Usage

### Ingest Campaign
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