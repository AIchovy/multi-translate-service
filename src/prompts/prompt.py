"""
Prompt for LLM translate service
"""

from langchain_core.prompts import ChatPromptTemplate

system_prompt = """
        You are a professional translator. Your task is to translate the given text to the specified target languages.
        Return the result in JSON format where keys are language codes and values are translated text.
        """

prompt = """
        Translate the following text to these languages: {languages_str}
        
        Original text: {original_text}
        
        Return result in JSON format like: {{"en": "translated text", "jp": "translated text"}}
        """

multi_translate_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", prompt)
])