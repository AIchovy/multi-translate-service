"""
File decoding service
"""

import struct
from typing import Optional
from fastapi import HTTPException

from src.models.translation_model import TranslationTask
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileDecodingService:
    """File decoding service"""

    def __init__(self, file_path: str = "stories.bin"):
        self.file_path = file_path
        try:
            with open(file_path, "rb") as f:
                self.num_records, self.index_length, self.data_offset = struct.unpack(
                    "<IIQ", f.read(16)
                )
            logger.info(
                f"initialized StoryReader: num_records={self.num_records}, data_offset={self.data_offset}")
        except Exception as e:
            logger.error(f"failed to initialize StoryReader: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"failed to initialize FileDecodingService: {str(e)}")

    def get_text(self, language: str, text_id: str, source: Optional[str] = None) -> str:
        """
        Get text content by language, text_id and source
        """
        try:
            # Build query key
            key = (language, text_id, source) if source else (
                language, text_id)

            # Read index area
            with open(self.file_path, "rb") as f:
                # Skip metadata header
                f.seek(16)  
                low, high = 0, self.num_records
                while low < high:
                    mid = (low + high) // 2
                    # Each index record is 41 bytes
                    f.seek(16 + mid * 41)  
                    lang = f.read(8).decode("utf-8").rstrip("\x00")
                    tid = f.read(16).decode("utf-8").rstrip("\x00")
                    src = f.read(5).decode("utf-8").rstrip("\x00")
                    offset, length = struct.unpack("<QI", f.read(12))

                    if (lang, tid) < key[:2]:
                        low = mid + 1
                    elif (lang, tid) > key[:2]:
                        high = mid
                    else:
                        if source and src != source:
                            logger.error(f"source mismatch: expected {source}, actual {src}")
                            raise HTTPException(
                                status_code=404, detail=f"source mismatch: expected {source}, actual {src}")
                        break
                else:
                    logger.error(f"not found: language {language}, text id {text_id}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"not found: language {language}, text id {text_id}"
                    )

            # Read data area
            with open(self.file_path, "rb") as f:
                f.seek(self.data_offset + offset)
                content = f.read(length).decode("utf-8")
                logger.info(
                    f"query success: {language}, {text_id}, {source}, content: {content}")
                return content

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"query failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"query failed: {str(e)}")
