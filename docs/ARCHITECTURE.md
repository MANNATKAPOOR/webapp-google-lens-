# System Architecture

## Overview
AI Vision OCR is a decoupled application consisting of a Flutter Web frontend and a FastAPI (Python) backend.

## Components

### 1. Frontend (Flutter Web)
- **Framework**: Flutter 3.0+
- **Key Packages**:
  - `http`: REST API communication
  - `file_picker`: Image upload handling
  - `pdf`: Client-side PDF generation (via backend generated file)
  - `flutter_animate` / `shimmer`: Loading and transition animations
- **State Management**: Stateful Widgets + asynchronous async/await calls.
- **Routing**: Built-in Navigator with `url_strategy` to remove hash fragments.

### 2. Backend (FastAPI)
- **Framework**: FastAPI + Uvicorn
- **Core Services**:
  - `ImageProcessor`: Uses OpenCV and Pillow for EXIF rotation, denoising, and contrast enhancement.
  - `OCRService`: Wraps PaddleOCR for extracting printed and handwritten text.
  - `GeminiService`: Wraps the Google Gemini 1.5 Flash API for advanced image understanding.
- **Data Flow**:
  1. Image uploaded via multipart/form-data.
  2. Image processed for OCR and Gemini in parallel using ThreadPoolExecutor.
  3. OCR and Gemini models run concurrently.
  4. Results merged and cached in LRU cache.
  5. JSON response returned to frontend.
- **Endpoints**:
  - `/analyze`: POST endpoint for image upload.
  - `/download/{format}/{id}`: GET endpoints for retrieving cached results as TXT, JSON, or PDF.
  - `/health` & `/version`: Diagnostics.

## Deployment Architecture
- **Frontend**: Hosted on Vercel CDN as static files (`index.html`, `main.dart.js`).
- **Backend**: Hosted on Render as a Docker container.
- **CORS**: Configured on backend to allow requests from the Vercel frontend domain.
