"""Azure AI Search vector store implementation."""

from __future__ import annotations

import base64
import json
import logging

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from src.services.vector_store.base import (
    SearchResult,
    VectorRecord,
    VectorStore,
)

LOGGER = logging.getLogger(__name__)


def _encode_key(key: str) -> str:
    """Encode a chunk_id to a valid Azure Search key."""
    return base64.urlsafe_b64encode(key.encode()).decode().rstrip("=")


def _decode_key(encoded: str) -> str:
    """Decode an Azure Search key back to chunk_id."""
    padding = 4 - len(encoded) % 4
    if padding != 4:
        encoded += "=" * padding
    return base64.urlsafe_b64decode(encoded.encode()).decode()


class AzureSearchVectorStore(VectorStore):
    """VectorStore backed by Azure AI Search."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        index_name: str,
        vector_size: int = 768,
    ) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._index_name = index_name
        self._vector_size = vector_size
        self._credential = AzureKeyCredential(api_key)

    def _search_client(self) -> SearchClient:
        return SearchClient(
            endpoint=self._endpoint,
            index_name=self._index_name,
            credential=self._credential,
        )

    def _index_client(self) -> SearchIndexClient:
        return SearchIndexClient(
            endpoint=self._endpoint,
            credential=self._credential,
        )

    def initialize(self, vector_size: int = 768) -> None:
        """Create the index if it does not exist."""
        self._vector_size = vector_size
        client = self._index_client()
        existing = [i.name for i in client.list_indexes()]
        if self._index_name in existing:
            LOGGER.info(
                "[AzureSearch] index '%s' already exists",
                self._index_name,
            )
            return

        fields = [
            SimpleField(
                name="chunk_id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SimpleField(
                name="source_id",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="source_type",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
            ),
            SimpleField(
                name="metadata_json",
                type=SearchFieldDataType.String,
                filterable=False,
            ),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single
                ),
                searchable=True,
                vector_search_dimensions=vector_size,
                vector_search_profile_name="hnsw-profile",
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="hnsw-config")
            ],
            profiles=[
                VectorSearchProfile(
                    name="hnsw-profile",
                    algorithm_configuration_name="hnsw-config",
                )
            ],
        )

        index = SearchIndex(
            name=self._index_name,
            fields=fields,
            vector_search=vector_search,
        )
        client.create_index(index)
        LOGGER.info(
            "[AzureSearch] created index '%s'", self._index_name
        )

    def upsert(self, records: list[VectorRecord]) -> None:
        """Upload or update documents in the index."""
        if not records:
            return
        documents = [
            {
                "chunk_id": _encode_key(r.chunk_id),
                "source_id": r.source_id,
                "source_type": r.source_type,
                "content": r.content,
                "metadata_json": json.dumps(r.metadata),
                "embedding": r.embedding,
            }
            for r in records
        ]
        client = self._search_client()
        client.merge_or_upload_documents(documents)
        LOGGER.info(
            "[AzureSearch] upserted %d documents", len(documents)
        )

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Vector similarity search."""
        client = self._search_client()
        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=top_k,
            fields="embedding",
        )
        results = client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["chunk_id", "content", "metadata_json"],
            top=top_k,
        )
        output = []
        for r in results:
            metadata = json.loads(r.get("metadata_json") or "{}")
            output.append(
                SearchResult(
                    chunk_id=_decode_key(r["chunk_id"]),
                    content=r["content"],
                    metadata=metadata,
                    score=r["@search.score"],
                )
            )
        return output

    def get_by_url(self, url_substring: str) -> list[SearchResult]:
        """Return all chunks whose source_id contains url_substring.

        metadata_json is stored but not searchable or filterable in the
        Azure AI Search index, so we cannot use it in search_fields or a
        $filter expression.  source_id is filterable and holds the URL
        path (minus the https:// prefix), so a Python substring check on
        source_id is both correct and cheap for this index size.
        """
        client = self._search_client()
        results = client.search(
            search_text="*",
            select=["chunk_id", "content", "metadata_json", "source_id"],
            top=1000,
        )
        output = []
        for r in results:
            source_id = r.get("source_id") or ""
            if url_substring in source_id:
                metadata = json.loads(r.get("metadata_json") or "{}")
                output.append(
                    SearchResult(
                        chunk_id=_decode_key(r["chunk_id"]),
                        content=r["content"],
                        metadata=metadata,
                        score=1.0,
                    )
                )
        return output

    def delete(self, namespace: str) -> None:
        """Delete all documents with matching source_id."""
        client = self._search_client()
        results = client.search(
            search_text="*",
            filter=f"source_id eq '{namespace}'",
            select=["chunk_id"],
            top=1000,
        )
        keys = [{"chunk_id": r["chunk_id"]} for r in results]
        if keys:
            client.delete_documents(keys)
            LOGGER.info(
                "[AzureSearch] deleted %d docs for source_id=%s",
                len(keys),
                namespace,
            )

    def clear(self) -> int:
        """Delete all documents in the index."""
        client = self._search_client()
        results = client.search(
            search_text="*",
            select=["chunk_id"],
            top=1000,
        )
        keys = [{"chunk_id": r["chunk_id"]} for r in results]
        if keys:
            client.delete_documents(keys)
        LOGGER.info(
            "[AzureSearch] cleared %d documents", len(keys)
        )
        return len(keys)
