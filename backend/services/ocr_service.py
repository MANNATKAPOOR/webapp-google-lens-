import easyocr
import numpy as np
from backend.core.logging import logger
from backend.models.schemas import OCRResult

class OCRService:
    def __init__(self):
        logger.info("Initializing EasyOCR...")
        # Initialize EasyOCR for English text (verbose=False prevents Windows cp1252 crash)
        self.reader = easyocr.Reader(['en'], verbose=False)
        logger.info("EasyOCR initialized successfully.")

    def extract_text(self, image_array: np.ndarray) -> OCRResult:
        """
        Extract text from an image array using EasyOCR.
        Returns extracted text and overall confidence.
        """
        try:
            logger.info("Starting OCR extraction with EasyOCR...")
            # easyocr reads text from a numpy array
            results = self.reader.readtext(image_array)
            
            extracted_text = []
            total_confidence = 0.0
            count = 0
            
            # results is a list of tuples: (bbox, text, prob)
            for (bbox, text, prob) in results:
                extracted_text.append(text)
                total_confidence += prob
                count += 1
            
            final_text = "\n".join(extracted_text) if extracted_text else "No text detected."
            
            # Calculate average confidence (0-100 scale)
            avg_confidence = (total_confidence / count * 100) if count > 0 else 0.0
            
            logger.info(f"OCR extraction complete. Detected {count} lines.")
            return OCRResult(
                text=final_text,
                confidence=round(avg_confidence, 2)
            )
            
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            return OCRResult(text="OCR not available (System Error)", confidence=0.0)

# Create a singleton instance to be used across requests
ocr_service_instance = None

def get_ocr_service() -> OCRService:
    global ocr_service_instance
    if ocr_service_instance is None:
        ocr_service_instance = OCRService()
    return ocr_service_instance
