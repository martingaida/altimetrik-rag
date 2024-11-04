from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer, util
from settings import settings
from shared.domain.queries import LLMQuery, VectorQuery
from shared.domain.documents import VectorSearchResult
from steps.base import RAGStep


class Reranker(RAGStep):
    def __init__(self, mock: bool = False) -> None:
        super().__init__(mock=mock)
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def generate(self, query: LLMQuery | VectorQuery, chunks: list[VectorSearchResult], keep_top_k: int) -> list[VectorSearchResult]:
        """Rerank chunks based on cosine similarity using the same embedding model"""
        if self._mock or not chunks:
            return chunks[:keep_top_k] if chunks else []

        try:
            # Get query embedding
            query_embedding = self._model.encode(query.content, convert_to_tensor=True)
            
            # Get chunk embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            chunk_embeddings = self._model.encode(chunk_texts, convert_to_tensor=True)
            
            # Calculate cosine similarities
            cos_scores = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
            cos_scores = cos_scores.cpu().numpy()

            # Sort chunks by similarity
            chunk_score_pairs = list(zip(cos_scores, chunks))
            chunk_score_pairs.sort(key=lambda x: x[0], reverse=True)

            # Take top k chunks
            reranked_documents = chunk_score_pairs[:keep_top_k]
            reranked_documents = [doc for _, doc in reranked_documents]
            
            logger.info(f"Reranked {len(chunks)} chunks to top {keep_top_k}")
            return reranked_documents
            
        except Exception as e:
            logger.error(f"Error during reranking: {str(e)}")
            return chunks[:keep_top_k] if chunks else []
