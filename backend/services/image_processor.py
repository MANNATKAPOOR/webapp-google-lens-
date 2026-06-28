import cv2
import numpy as np
from PIL import Image, ImageEnhance, ExifTags
import io


class ImageProcessor:
    @staticmethod
    def _fix_orientation(image: Image.Image) -> Image.Image:
        """Auto-rotate image based on EXIF orientation data."""
        try:
            exif = image._getexif()
            if exif is not None:
                orientation_key = None
                for key, val in ExifTags.TAGS.items():
                    if val == 'Orientation':
                        orientation_key = key
                        break
                
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        return image

    @staticmethod
    def process_for_ocr(image_bytes: bytes) -> np.ndarray:
        """
        Process the uploaded image for optimal OCR extraction.
        Steps:
        1. Auto-rotate from EXIF
        2. Convert to RGB
        3. Denoise
        4. Enhance contrast
        5. Enhance sharpness
        6. Adjust brightness
        """
        # Open with Pillow for EXIF handling
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # Auto-rotate from EXIF
        pil_img = ImageProcessor._fix_orientation(pil_img)
        
        # Convert to RGB if needed
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        
        # Convert to numpy for OpenCV processing
        img_array = np.array(pil_img)
        
        # Denoise using fastNlMeansDenoisingColored
        denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 6, 6, 7, 21)
        
        # Convert back to PIL for enhancement
        pil_img = Image.fromarray(denoised)
        
        # Enhance Contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.5)
        
        # Enhance Sharpness
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(2.0)
        
        # Adjust Brightness slightly
        enhancer = ImageEnhance.Brightness(pil_img)
        pil_img = enhancer.enhance(1.1)
        
        # Convert back to numpy array (RGB)
        enhanced_img = np.array(pil_img)

        return enhanced_img

    @staticmethod
    def process_for_ai(image_bytes: bytes) -> bytes:
        """
        Process image for AI analysis (compression). 
        Auto-rotate and compress if larger than 4MB.
        """
        # Auto-rotate
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img = ImageProcessor._fix_orientation(pil_img)
        
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        
        # Convert to numpy for OpenCV
        img_array = np.array(pil_img)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Compress if larger than 4MB
        if len(image_bytes) > 4 * 1024 * 1024:
            height, width = img_bgr.shape[:2]
            max_dim = 1600
            if max(height, width) > max_dim:
                scale = max_dim / max(height, width)
                img_bgr = cv2.resize(img_bgr, (int(width * scale), int(height * scale)))

            # Encode back to JPEG
            _, buffer = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return buffer.tobytes()

        # Re-encode to ensure correct orientation is baked in
        _, buffer = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return buffer.tobytes()
