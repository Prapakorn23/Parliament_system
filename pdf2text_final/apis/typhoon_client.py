import os
import sys
import requests
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class TyphoonSummarizerClient:
    """Client for Typhoon Summarizer FastAPI service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def is_ready(self) -> bool:
        """Check if the Typhoon API service is ready."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200 and response.json().get("model_ready", False)
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information from the API."""
        try:
            response = self.session.get(f"{self.base_url}/model-info", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def summarize(
        self,
        text: str,
        target_length: int = 1000,
        do_sample: bool = False,
        lang: str = "auto",
        # Backward compatibility parameters (deprecated)
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> str:
        """
        Summarize text using Typhoon API with dynamic token allocation.
        
        Args:
            text: Input text to summarize
            target_length: Target character length for summary (500-1500 recommended, default 1000)
            do_sample: Whether to use sampling (default False for consistent results)
            lang: Language code ('auto', 'th', 'en')
            max_length: DEPRECATED - Use target_length instead
            min_length: DEPRECATED - Use target_length instead
            
        Returns:
            Summary text
        """
        if not text or len(text.strip()) < 50:
            return text.strip()

        # Handle backward compatibility
        if max_length is not None or min_length is not None:
            print("Warning: max_length and min_length are deprecated. Use target_length instead.")
            if max_length is not None:
                # Convert old max_length (tokens) to approximate character length
                target_length = max_length * 3  # Rough conversion

        try:
            payload = {
                "text": text,
                "target_length": target_length,
                "do_sample": do_sample,
                "lang": lang
            }

            response = self.session.post(
                f"{self.base_url}/summarize",
                json=payload,
                timeout=60  # Increased timeout for long texts with second-pass
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("summary", "")
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_detail = response.json().get("detail", "")
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                raise RuntimeError(error_msg)

        except requests.exceptions.Timeout:
            raise RuntimeError("API request timed out")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot connect to Typhoon API service")
        except Exception as e:
            raise RuntimeError(f"Summarization failed: {e}")

    def summarize_long_text(
        self,
        text: str,
        target_length: int = 1000,
        lang: str = "auto",
        # Deprecated parameters for backward compatibility
        max_chunk_size: Optional[int] = None,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> str:
        """
        Summarize long text using the new API with automatic chunking and second-pass.
        
        NOTE: The API now handles chunking automatically, so this method simply
        calls the regular summarize() method. The old chunking logic is deprecated.
        
        Args:
            text: Input text to summarize
            target_length: Target character length for summary (500-1500 recommended)
            lang: Language code ('auto', 'th', 'en')
            max_chunk_size: DEPRECATED - API handles chunking automatically
            max_length: DEPRECATED - Use target_length instead
            min_length: DEPRECATED - Use target_length instead
            
        Returns:
            Summary text
        """
        # Handle backward compatibility
        if max_length is not None:
            print("Warning: max_length is deprecated. Use target_length instead.")
            target_length = max_length * 3
        
        if max_chunk_size is not None:
            print("Warning: max_chunk_size is deprecated. API handles chunking automatically.")
        
        # The new API handles everything automatically
        try:
            return self.summarize(text, target_length=target_length, lang=lang)
        except Exception as e:
            print(f"Summarization failed: {e}")
            # Fallback to basic text processing
            return _basic_text_processing(text, target_length)


def _contains_thai(text: str) -> bool:
    """Check if text contains Thai characters."""
    return any("\u0E00" <= ch <= "\u0E7F" for ch in text)


def _basic_text_processing(text: str, target_length: int) -> str:
    """Basic text processing fallback when all other methods fail."""
    try:
        # Simple extractive summarization
        import re
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        
        if not sentences:
            return text[:target_length] + "..." if len(text) > target_length else text
        
        # Take first, middle, and last sentences
        if len(sentences) > 10:
            key_sentences = sentences[:3] + sentences[len(sentences)//2:len(sentences)//2+2] + sentences[-2:]
        elif len(sentences) > 5:
            key_sentences = sentences[:2] + sentences[-2:]
        else:
            key_sentences = sentences
        
        summary = ". ".join(key_sentences) + "."
        
        # Ensure length constraints
        if len(summary) > target_length:
            summary = summary[:target_length] + "..."
        
        return summary
        
    except Exception as e:
        print(f"Basic text processing failed: {e}")
        # Ultimate fallback
        return text[:target_length] + "..." if len(text) > target_length else text


# Global client instance
typhoon_client = TyphoonSummarizerClient()