import io
from PIL import Image
from transformers import pipeline
from backend.core.logging import logger
from backend.models.schemas import AIDescription

class HuggingFaceService:
    def __init__(self):
        logger.info("Initializing Local AI Models (this will download models on first run)...")
        # Initialize the vision models locally on CPU
        # We use the base BLIP model which is ~900MB and runs reasonably fast on CPU
        try:
            self.blip_pipeline = pipeline("image-text-to-text", model="Salesforce/blip-image-captioning-base")
            self.vit_pipeline = pipeline("image-classification", model="google/vit-base-patch16-224")
            logger.info("Local AI Models initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize local AI models: {e}")
            self.blip_pipeline = None
            self.vit_pipeline = None

    def analyze_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> AIDescription:
        """
        Analyze image using local Hugging Face transformers models.
        """
        logger.info("Starting local AI image understanding...")
        
        description = "No description available."
        objects = []
        
        if not self.blip_pipeline or not self.vit_pipeline:
            return AIDescription(
                description="AI Models failed to load locally.",
                objects=["Error"],
                brands=[],
                dominant_colors=[],
                language="English"
            )
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # 1. Get object tags using local ViT FIRST so we can include them in the description
            logger.info("Running ViT image classification...")
            vit_result = self.vit_pipeline(image)
            if vit_result and isinstance(vit_result, list):
                # ViT returns a list of dictionaries with 'label' and 'score'
                for item in vit_result[:5]:
                    if item.get("score", 0) > 0.05:
                        label = item.get("label", "").split(",")[0].strip()
                        if label:
                            objects.append(label)
                            
            if not objects:
                objects = ["Unknown Objects"]

            # 2. Get image caption (description) using local BLIP with longer generation params
            logger.info("Running BLIP image captioning...")
            blip_result = self.blip_pipeline(
                image,
                text="A picture of",
                max_new_tokens=100,
                min_new_tokens=10,
                do_sample=True,
                top_p=0.9
            )
            
            if blip_result and isinstance(blip_result, list) and len(blip_result) > 0:
                caption = blip_result[0].get("generated_text", "")
                if caption:
                    caption = caption[0].upper() + caption[1:]
                    
                    # Construct a more detailed explanation
                    explanation = f"{caption}. "
                    
                    if len(objects) > 0 and objects[0] != "Unknown Objects":
                        explanation += f"Based on the visual data, this image prominently features: {', '.join(objects)}. "
                        
                    description = explanation.strip()
                
        except Exception as e:
            logger.error(f"Error during local AI analysis: {e}")
            description = f"Local Analysis failed: {str(e)}"
            objects = ["Error"]

        return AIDescription(
            description=description,
            objects=objects,
            brands=[],
            dominant_colors=[],
            language="English"
        )

# Create a singleton instance
huggingface_service_instance = None

def get_huggingface_service() -> HuggingFaceService:
    global huggingface_service_instance
    if huggingface_service_instance is None:
        huggingface_service_instance = HuggingFaceService()
    return huggingface_service_instance
