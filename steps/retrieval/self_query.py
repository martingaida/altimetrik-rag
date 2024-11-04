from langchain_openai import ChatOpenAI
from loguru import logger
from shared.domain.queries import LLMQuery
from settings import settings
from steps.base import RAGStep
from steps.prompt_templates import SelfQueryTemplateECT


class SelfQuery(RAGStep):
    def generate(self, query: LLMQuery) -> LLMQuery:
        """Extract metadata from query using LLM"""
        if self._mock:
            return query

        try:
            # Create prompt and model
            prompt = SelfQueryTemplateECT().create_template()
            model = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0
            )

            # Get metadata from LLM
            chain = prompt | model
            response = chain.invoke({"question": query.content})
            metadata = response.content.strip("\n ")
            
            # Add metadata to query
            query.metadata = {"extracted_terms": metadata}
            logger.info(f"Extracted metadata: {metadata}")
            
            return query
            
        except Exception as e:
            logger.error(f"Error in self-query: {e}")
            return query


if __name__ == "__main__":
    query = LLMQuery.from_str("I am Paul Iusztin. Write an article about the best types of advanced RAG methods.")
    self_query = SelfQuery()
    query = self_query.generate(query)
    logger.info(f"Extracted metadata: {query.metadata}")
