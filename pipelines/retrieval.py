from loguru import logger
from shared.domain.queries import LLMQuery
from steps.retrieval.query_expansion import QueryExpansion
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
        
        # Expand query
        query_expander = QueryExpansion()
        expanded_queries = query_expander.generate(query, expand_to_n=3)
        logger.info(f"Generated {len(expanded_queries)} expanded queries")
        
        # Search using all queries
        all_results = []
        seen = set()
        
        for idx, expanded_query in enumerate(expanded_queries):
            logger.debug(f"Searching with query {idx + 1}: {expanded_query.content}")
            
            results = connection.search_similar(
                query_text=expanded_query.content,
                limit=10
            )
            
            # Convert results and remove duplicates
            for result in results:
                chunk = VectorSearchResult(
                    text=result.payload.get("text", ""),
                    metadata=result.payload.get("metadata", {}),
                    score=result.score
                )
                if chunk.text not in seen:
                    seen.add(chunk.text)
                    all_results.append(chunk)
                    
            logger.info(f"Found {len(results)} results for query {idx + 1}")
        
        if not all_results:
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
