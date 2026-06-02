# Student Support Chatbot

An intelligent agentic AI chatbot designed to provide 24/7 support for student enquiries, reducing pressure on administrative staff.

## Features

- **FAQ Assistance**: Answers questions about hostel allocation, campus rules, and moral/conduct policies
- **Multi-language Support**: English and Yoruba language capabilities
- **Ethical Guidelines**: Respects and surfaces MU's Islamic ethics and Ahmadiyya community guidelines
- **Ticketing/Escalation**: Automatically escalates unresolved issues to appropriate departments
- **Streaming Responses**: Real-time AI responses for better user experience

## Technology Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Model**: Ollama (configurable for production: ChatGPT, Gemini, or cloud alternatives)
- **Dependency Injection**: Dependency Injector
- **Environment Management**: Python-dotenv

## Project Structure

```
student-support-chatbot/
├── agentic/
│   ├── api/v1/                  # API endpoints
│   ├── application/             # Application interfaces and use cases
│   ├── domain/                  # Domain models and entities
│   └── infrastructure/          # Infrastructure implementations
│       ├── ai_client.py         # Ollama AI integration
│       ├── database.py          # Database configuration
│       ├── dependency.py        # Dependency injection container
│       ├── repository/          # Data access implementations
│       ├── service/             # Business logic implementations
│       └── tools.py             # Available AI tools
├── alembic/                     # Database migrations
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── main.py                      # Application entry point
```

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables** in `.env` file:
   ```env
   # Database
   DATABASE_URL="postgresql+asyncpg://postgres:your_password@localhost:5432/StudentSupportAI"

   # AI
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:3b
   ```
4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```
5. **Start the application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- `POST /chats` - Create a new chat session
- `GET /chats/sessions` - List all chat sessions
- `POST /chats/{session_id}/message` - Send a message and get streaming response

## Future Enhancements

- Integration with actual FAQ databases for hostel allocation, campus rules, etc.
- Yoruba translation service implementation
- Department-specific escalation mechanisms
- Authentication and authorization for administrative access
- Analytics and reporting features
- Production deployment with ChatGPT/Gemini/cloud AI models

## Ethical Considerations

This chatbot is designed to:
- Promote Islamic ethical principles of justice, compassion, and honesty
- Uphold Ahmadiyya values of peace, tolerance, and service to humanity
- Provide accurate information while acknowledging limitations
- Escalate complex issues to human administrators when needed
- Maintain respectful and inclusive communication at all times