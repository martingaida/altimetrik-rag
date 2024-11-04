from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple
from langchain_openai import ChatOpenAI
from loguru import logger
import json
import re

from shared.domain.types import QueryIntent
from shared.domain.queries import LLMQuery
from settings import settings
from steps.base import RAGStep
from steps.prompt_templates import IntentDetectionTemplate


class IntentDetector(RAGStep):
    def __init__(self, mock: bool = False):
        super().__init__(mock=mock)
        self.model = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0
        )
        self.prompt = IntentDetectionTemplate().create_template()

    def generate(self, query: LLMQuery) -> Tuple[QueryIntent, Optional[Dict[str, Any]]]:
        """Required implementation of RAGStep's generate method"""
        return self.detect(query)

    def detect(self, query: LLMQuery) -> Tuple[QueryIntent, Optional[Dict[str, Any]]]:
        """Detect query intent and generate MongoDB query if applicable"""
        if self._mock:
            return QueryIntent.GENERAL, None

        try:
            # Create chain with prompt template
            chain = self.prompt | self.model
            
            # Get response from LLM
            response = chain.invoke({"question": query.content})
            
            # Parse LLM response
            intent_data = self._parse_intent_response(response)
            logger.info(f"Detected intent: {intent_data}")
            
            return intent_data["intent"], intent_data.get("mongo_query")
            
        except Exception as e:
            logger.error(f"Error detecting intent: {e}", exc_info=True)
            return QueryIntent.GENERAL, None


    def _parse_intent_response(self, response) -> Dict[str, Any]:
        try:
            content = response.content.strip()
            # Remove markdown code block formatting
            content = content.replace('```json', '').replace('```', '').strip()
            # Parse the JSON
            data = json.loads(content)
            # Convert intent string to enum
            intent_str = data["intent"].upper()  # Convert to uppercase for enum matching
            try:
                intent = QueryIntent[intent_str]
            except KeyError:
                logger.warning(f"Unknown intent: {intent_str}, defaulting to GENERAL")
                intent = QueryIntent.GENERAL

            return {
                "intent": intent,
                "mongo_query": data.get("mongo_query")
            }
            
        except Exception as e:
            logger.error(f"Error parsing intent response: {e}", exc_info=True)
            return {"intent": QueryIntent.GENERAL, "mongo_query": None}