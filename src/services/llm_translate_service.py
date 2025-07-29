"""
LLM translate service
"""

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from pydantic import BaseModel, Field

from src.utils.logger import get_logger
from src.configs.config import settings
from src.prompts.prompt import multi_translate_prompt

logger = get_logger(__name__)

class TranslationResult(BaseModel):
    """ Translation result """
    translations: dict[str, str] = Field(..., description="Dictionary where key is language code and value is translated text")

class LLMTranslateService:
    """ Translate service using LLM """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name, api_key=settings.openai_api_key, base_url=settings.openai_api_base)
        self.model_name = model_name

    def translate(self, original_text: str, target_languages: list[str]):
        """
        Translate text to multiple target languages
        
        Args:
            original_text: Text to translate
            target_languages: List of target language codes
            
        Returns:
            TranslationResult: Dictionary format with language codes as keys and translated text as values
        """
        
        languages_str = ", ".join(target_languages)

        parser = JsonOutputParser(pydantic_object=TranslationResult)

        chain = multi_translate_prompt | self.llm | parser

        result = chain.invoke({"original_text": original_text, "languages_str": languages_str})
        
        logger.info(f"Result: {result}")

        return result
