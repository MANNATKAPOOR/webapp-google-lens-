# Offline AI Vision OCR Platform (Google Lens Alternative)

A production-ready Google Lens-style AI Vision OCR web application. This project extracts text from images and generates detailed AI image descriptions **100% offline** on your local machine using the Hugging Face `transformers` library, requiring absolutely NO API keys or cloud connections.

## Features
- **100% Offline AI Image Understanding**: Generates detailed descriptive captions and detects objects using local Hugging Face pipelines (`Salesforce/blip-image-captioning-base` and `google/vit-base-patch16-224`).
- **Offline OCR Text Extraction**: Extracts text from documents using the `EasyOCR` library.
- **Modern Web Interface**: Responsive HTML/CSS glassmorphism UI with drag-and-drop support.
- **Downloadable Results**: Export analysis as TXT, JSON, or PDF.

## Local Setup

### Prerequisites
- Python 3.9 - 3.13
- Internet connection (ONLY for the very first run to download the ~1.5GB AI models)
- No API keys required!

### Setup Instructions

1. **Install Dependencies**
```bash
# We recommend using a virtual environment
cd backend
python -m venv venv

# Activate the virtual environment:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

2. **Run the Backend Server**
```bash
# Make sure you are in the root folder, and your venv is activated
python -m uvicorn backend.main:app --reload
```

3. **Access the Web App**
Open your web browser and navigate to:
`http://localhost:8000`

### Note on First Run
The very first time you click "Analyze", the backend will automatically download the required AI models from Hugging Face (~1.5GB total). Your browser might take a few minutes to process the first image. All subsequent images will process much faster and completely offline!

## License
MIT
