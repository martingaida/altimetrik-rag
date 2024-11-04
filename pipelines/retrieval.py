from loguru import logger
from zenml import pipeline
from shared.domain.queries import LLMQuery
from shared.preprocessing.operations.tagging import tag_chunk
from steps.retrieval.query_expansion import QueryExpansion
from steps.retrieval.self_query import SelfQuery
from steps.retrieval.reranking import Reranker
from infrastructure.db.qdrant import connection
from shared.domain.documents import VectorSearchResult
from typing import List

def retrieval_pipeline(query: str, top_k: int = 3) -> List[VectorSearchResult]:
    """
    Execute the RAG retrieval pipeline
    """
    logger.info(f"Retrieving context for query: {query}")
    
    try:
        # Convert string to LLMQuery
        if isinstance(query, str):
            query = LLMQuery.from_str(query)

        # Tag query
        query_tags = tag_chunk(query.content)
        logger.info(f"Query tags: {query_tags}")
        filter_condition = None
        
        # Expand query
        # Generate expanded queries
        query_expander = QueryExpansion()
        expanded_queries = query_expander.generate(query, expand_to_n=3)
        logger.info(f"Generated {len(expanded_queries)} expanded queries")
       
        # Generate self queries
        self_query = SelfQuery()
        self_query = self_query.generate(query)
        logger.info(f"Generated self query: {self_query}")
        
        # Extract terms from self queries and add to query tags
        tags = self_query.split(',')
        query_tags.extend([tag.strip() for tag in tags if tag.strip() and not tag.startswith("none")])
        logger.info(f"Query tags after self query: {query_tags}")

        # Create filter condition if we have tags
        if len(query_tags) > 0:
            filter_condition = {
                "must": [
                    {
                        "key": "tags",
                        "match": { "any": query_tags }
                    }
                ]
            }

        # Combine expanded and self queries
        if isinstance(self_query, LLMQuery):
            expanded_queries.extend(self_query)
        logger.info(f"Total queries after combining: {len(expanded_queries)}")
        
        # Search using all queries
        all_results = []
        seen = set()
        
        for idx, expanded_query in enumerate(expanded_queries):
            logger.debug(f"Searching with query {idx + 1}: {expanded_query.content}")
            
            results = connection.search(
                query_text=expanded_query.content,
                limit=10,
                filter_condition=filter_condition
            )

            if len(results) == 0:
                logger.warning(f"Filter condition returned no results. Trying without filter condition.")
                results = connection.search(
                    query_text=expanded_query.content,
                    limit=10,
                    filter_condition=None
                )
            
            # Convert results and remove duplicates
            if len(results) > 0:    
                for result in results:
                    chunk = VectorSearchResult(
                        text=result.get("content", ""),
                        metadata=result.get("metadata", {}),
                        score=result.get("score")
                    )
                    if chunk.text not in seen:
                        seen.add(chunk.text)
                        all_results.append(chunk)
                    
            logger.info(f"Found {len(results)} results for query {idx + 1}")
        
        if len(all_results) == 0:
            logger.warning("No results found from vector search")
            return []
            
        # Rerank combined results
        reranker = Reranker()
        reranked_results = reranker.generate(query, all_results, keep_top_k=top_k)
        
        logger.info(f"Retrieved and reranked {len(reranked_results)} final results")
        return reranked_results
        
    except Exception as e:
        logger.error(f"Error in retrieval pipeline: {str(e)}")
        return []
