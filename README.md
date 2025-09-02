# Dynecron_Pueba Backend

This is the backend service for the application, built with FastAPI.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. **Create Docker Network** (if not already created):
   ```bash
   docker network create dynecron_network
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory with the required environment variables.

3. **Build and Run**
   ```bash
   docker-compose up --build
   ```
   The API will be available at `http://localhost:8000`

## API Documentation

Once running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Locally (without Docker)

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Environment Variables

Create a `.env` file with the following variables:

```
HF_TOKEN=your_hf_token
```


