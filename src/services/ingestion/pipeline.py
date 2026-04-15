"""Ingestion pipeline orchestration."""

from __future__ import annotations


class IngestionPipeline:
    """Run all enabled ingestion sources."""

    def __init__(self, sources: list) -> None:
        self._sources = sources

    def run(self) -> list[dict]:
        """Execute enabled sources in sequence."""

        results: list[dict] = []
        for source in self._sources:
            if source.is_enabled():
                result = source.ingest()
                if hasattr(result, "to_dict"):
                    results.append(result.to_dict())
                else:
                    results.append(result)
        return results
