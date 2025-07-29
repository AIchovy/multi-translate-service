"""
Text similarity calculation service
"""

import difflib
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SimilarityService:
    """Service for calculating text similarity using SequenceMatcher"""
    
    @staticmethod
    def calculate_similarity(original_text: str, stt_text: str) -> float:
        """
        Calculate similarity between two texts using difflib.SequenceMatcher, because the differences between the STT text and original text are usually at the character or phrase level.
        
        Args:
            original_text: Original text
            stt_text: STT text
            
        Returns:
            float: Similarity score between 0 and 1 (1 means identical)
        """
        if not original_text or not stt_text:
            logger.warning("One or both texts are empty")
            return 0.0
            
        # Normalize texts (convert to lowercase and strip whitespace
        text1_normalized = original_text.lower().strip()
        text2_normalized = stt_text.lower().strip()
        # Remove punctuation
        text1_normalized = re.sub(r'[^\w\s]|[\n]', '', text1_normalized)
        text2_normalized = re.sub(r'[^\w\s]|[\n]', '', text2_normalized)
        
        logger.info(f"text1_normalized: {text1_normalized}")
        logger.info(f"text2_normalized: {text2_normalized}")

        if text1_normalized == text2_normalized:
            return 1.0
            
        try:
            return difflib.SequenceMatcher(None, text1_normalized, text2_normalized).ratio()
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0