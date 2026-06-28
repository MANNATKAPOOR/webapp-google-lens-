from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse
from backend.models.schemas import AnalyzeResponse
from backend.services.image_processor import ImageProcessor
from backend.services.ocr_service import get_ocr_service
from backend.services.huggingface_service import get_huggingface_service
from backend.core.logging import logger
from backend.core.config import settings
import time
import asyncio
import uuid
import io
import json
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict

router = APIRouter()
thread_pool = ThreadPoolExecutor(max_workers=4)

# In-memory result cache (LRU-style, max 100 entries)
_result_cache: OrderedDict[str, dict] = OrderedDict()
MAX_CACHE_SIZE = 100


def _cache_result(analysis_id: str, data: dict):
    """Store an analysis result in the cache."""
    if len(_result_cache) >= MAX_CACHE_SIZE:
        _result_cache.popitem(last=False)  # Remove oldest
    _result_cache[analysis_id] = data


def _get_cached_result(analysis_id: str) -> dict | None:
    """Retrieve a cached analysis result."""
    return _result_cache.get(analysis_id)


@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an uploaded image.
    Performs OCR extraction and AI image understanding in parallel.
    Returns a unique ID that can be used to download results.
    """
    start_time = time.time()

    # 1. Validation
    # Allow application/octet-stream as well, since some browsers/clients send that instead of image/*
    if file.content_type and not (file.content_type.startswith("image/") or file.content_type == "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        image_bytes = await file.read()

        # Check size (convert to MB)
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > settings.max_image_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"Image size exceeds limit of {settings.max_image_size_mb}MB"
            )

        logger.info(f"Received image for analysis: {file.filename} ({size_mb:.2f} MB)")

        # 2. Process image for OCR and Gemini (in thread pool)
        loop = asyncio.get_event_loop()
        processed_ocr_array = await loop.run_in_executor(
            thread_pool, ImageProcessor.process_for_ocr, image_bytes
        )

        processed_ai_bytes = await loop.run_in_executor(
            thread_pool, ImageProcessor.process_for_ai, image_bytes
        )

        # 3. Run OCR and Hugging Face analysis concurrently
        ocr_service = get_ocr_service()
        hf_service = get_huggingface_service()

        def run_ocr():
            return ocr_service.extract_text(processed_ocr_array)

        def run_hf():
            return hf_service.analyze_image(processed_ai_bytes, file.content_type)

        ocr_task = loop.run_in_executor(thread_pool, run_ocr)
        hf_task = loop.run_in_executor(thread_pool, run_hf)

        ocr_result, ai_result = await asyncio.gather(ocr_task, hf_task)

        # 4. Construct Response
        end_time = time.time()
        processing_time_sec = round(end_time - start_time, 2)
        analysis_id = str(uuid.uuid4())[:8]

        logger.info(f"Analysis complete in {processing_time_sec}s (id={analysis_id})")

        response = AnalyzeResponse(
            id=analysis_id,
            text=ocr_result.text,
            confidence=ocr_result.confidence,
            description=ai_result.description,
            objects=ai_result.objects,
            brands=ai_result.brands,
            dominant_colors=ai_result.dominant_colors,
            language=ai_result.language,
            processing_time=f"{processing_time_sec} sec"
        )

        # Cache the result for downloads
        _cache_result(analysis_id, response.model_dump())

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the image: {str(e)}")


@router.get("/download/txt/{analysis_id}", tags=["Downloads"])
async def download_txt(analysis_id: str):
    """Download OCR results as a plain text file."""
    result = _get_cached_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found or expired.")

    content = f"""AI Vision OCR - Analysis Results
{'=' * 40}

EXTRACTED TEXT:
{result['text']}

AI DESCRIPTION:
{result['description']}

DETECTED OBJECTS:
{', '.join(result['objects'])}

BRANDS/LOGOS:
{', '.join(result.get('brands', []))}

DOMINANT COLORS:
{', '.join(result.get('dominant_colors', []))}

LANGUAGE: {result['language']}
CONFIDENCE: {result['confidence']}%
PROCESSING TIME: {result['processing_time']}
"""
    return PlainTextResponse(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=ocr_result_{analysis_id}.txt"}
    )


@router.get("/download/json/{analysis_id}", tags=["Downloads"])
async def download_json(analysis_id: str):
    """Download analysis results as a JSON file."""
    result = _get_cached_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found or expired.")

    json_content = json.dumps(result, indent=2, ensure_ascii=False)
    return PlainTextResponse(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=ocr_result_{analysis_id}.json"}
    )


@router.get("/download/pdf/{analysis_id}", tags=["Downloads"])
async def download_pdf(analysis_id: str):
    """Download analysis results as a PDF file."""
    result = _get_cached_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found or expired.")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1 * inch, bottomMargin=1 * inch)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=20, textColor=HexColor('#3b82f6'), spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'CustomHeading', parent=styles['Heading2'],
            fontSize=14, textColor=HexColor('#1e293b'), spaceAfter=8, spaceBefore=16
        )
        body_style = ParagraphStyle(
            'CustomBody', parent=styles['Normal'],
            fontSize=11, leading=16, spaceAfter=8
        )

        story = []
        story.append(Paragraph("AI Vision OCR - Analysis Results", title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Extracted Text", heading_style))
        # Escape HTML in text
        safe_text = result['text'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
        story.append(Paragraph(safe_text, body_style))

        story.append(Paragraph("AI Description", heading_style))
        safe_desc = result['description'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(safe_desc, body_style))

        story.append(Paragraph("Detected Objects", heading_style))
        story.append(Paragraph(', '.join(result['objects']), body_style))

        if result.get('brands'):
            story.append(Paragraph("Brands / Logos", heading_style))
            story.append(Paragraph(', '.join(result['brands']), body_style))

        if result.get('dominant_colors'):
            story.append(Paragraph("Dominant Colors", heading_style))
            story.append(Paragraph(', '.join(result['dominant_colors']), body_style))

        story.append(Paragraph("Details", heading_style))
        story.append(Paragraph(f"Language: {result['language']}", body_style))
        story.append(Paragraph(f"Confidence: {result['confidence']}%", body_style))
        story.append(Paragraph(f"Processing Time: {result['processing_time']}", body_style))

        doc.build(story)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=ocr_result_{analysis_id}.pdf"}
        )
    except ImportError:
        raise HTTPException(status_code=501, detail="PDF generation requires 'reportlab'. Install with: pip install reportlab")
