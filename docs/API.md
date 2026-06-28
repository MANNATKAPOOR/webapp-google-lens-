# API Documentation

The backend exposes a REST API via FastAPI.

Base URL: `http://localhost:8000` (Local) or `https://your-backend-url.onrender.com` (Production)

## Endpoints

### 1. Analyze Image
`POST /analyze`

Analyzes an uploaded image, performing OCR and AI understanding concurrently.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file, max 10MB)

**Response (200 OK):**
```json
{
  "id": "a1b2c3d4",
  "text": "Detected text from the image...",
  "description": "A detailed AI description of the scene...",
  "objects": ["Object 1", "Object 2", "QR Code"],
  "brands": ["Brand A", "Product B"],
  "dominant_colors": ["Red", "White"],
  "language": "English",
  "confidence": 95.5,
  "processing_time": "2.1 sec"
}
```

### 2. Download Results
Download cached analysis results in various formats. Requires the `id` from the `/analyze` response.

`GET /download/txt/{id}`
Returns: `text/plain` file

`GET /download/json/{id}`
Returns: `application/json` file

`GET /download/pdf/{id}`
Returns: `application/pdf` file

### 3. System Status

`GET /health`
Returns:
```json
{
  "status": "ok",
  "environment": "production"
}
```

`GET /version`
Returns:
```json
{
  "name": "AI Vision OCR Platform",
  "version": "1.0.0"
}
```

## Interactive Docs
When running locally, interactive Swagger UI documentation is available at `/docs` and ReDoc at `/redoc`.
