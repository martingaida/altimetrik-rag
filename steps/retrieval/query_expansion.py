from langchain_openai import ChatOpenAI
from loguru import logger

from shared.domain.queries import LLMQuery
from settings import settings

from steps.base import RAGStep
from steps.prompt_templates import QueryExpansionTemplateECT


class QueryExpansion(RAGStep):
    def generate(self, query: LLMQuery, expand_to_n: int) -> list[LLMQuery]:
        assert expand_to_n > 0, f"'expand_to_n' should be greater than 0. Got {expand_to_n}."

        if self._mock:
            return [query for _ in range(expand_to_n)]

        query_expansion_template = QueryExpansionTemplateECT()
        prompt = query_expansion_template.create_template(expand_to_n - 1)
        model = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0)

        chain = prompt | model

        response = chain.invoke({"question": query})
        result = response.content

        queries_content = result.strip().split(query_expansion_template.separator)

        queries = [query]
        queries += [
            query.replace_content(stripped_content)
            for content in queries_content
            if (stripped_content := content.strip())
        ]

        return queries


if __name__ == "__main__":
    query = LLMQuery.from_str("Write an article about the best types of advanced RAG methods.")
    query_expander = QueryExpansion()
    expanded_queries = query_expander.generate(query, expand_to_n=3)
    for expanded_query in expanded_queries:
        logger.info(expanded_query.content)
