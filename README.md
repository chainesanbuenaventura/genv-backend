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
        "body_excerpt": """Hello,

        I recently signed a freelance contract with a tech company, and I have a few concerns about the non-compete and payment terms. I’d like to know if everything is fair and if there are any red flags.

        Can someone from your team take a look at the document and advise me on my rights?

        Thank you,

        **Sarah Dubois**""",
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
