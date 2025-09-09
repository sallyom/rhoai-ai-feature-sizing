"""Lightweight local embedding implementation using sentence-transformers."""

import logging
from typing import Any, List, Optional
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class LocalEmbedding(BaseEmbedding):
    """Local embedding using sentence-transformers with minimal dependencies."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        **kwargs: Any,
    ) -> None:
        """Initialize local embedding model.
        
        Args:
            model_name: Name of the sentence-transformers model
            device: Device to run on (cpu/cuda)
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        self.device = device
        self._model: Optional[SentenceTransformer] = None
        
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model."""
        if self._model is None:
            logger.info(f"Loading local embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Local embedding model loaded successfully")
        return self._model

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a query."""
        return self.model.encode([query], convert_to_tensor=False)[0].tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a text."""
        return self.model.encode([text], convert_to_tensor=False)[0].tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return [embedding.tolist() for embedding in embeddings]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Async version of _get_query_embedding."""
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Async version of _get_text_embedding."""
        return self._get_text_embedding(text)