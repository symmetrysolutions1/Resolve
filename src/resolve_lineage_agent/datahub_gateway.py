"""DataHub SDK adapter. Imports are lazy so the offline demo stays lightweight."""

from __future__ import annotations

from typing import Any


class DataHubGateway:
    def __init__(self, server: str, token: str | None = None) -> None:
        from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig

        self._graph = DataHubGraph(DataHubGraphConfig(server=server, token=token))

    def read_context(self, urn: str) -> dict[str, Any]:
        from datahub.metadata.schema_classes import (
            DatasetPropertiesClass,
            OwnershipClass,
            SchemaMetadataClass,
            UpstreamLineageClass,
        )

        properties = self._graph.get_aspect(urn, DatasetPropertiesClass)
        schema = self._graph.get_aspect(urn, SchemaMetadataClass)
        ownership = self._graph.get_aspect(urn, OwnershipClass)
        lineage = self._graph.get_aspect(urn, UpstreamLineageClass)

        return {
            "urn": urn,
            "name": getattr(properties, "name", None),
            "custom_properties": dict(getattr(properties, "customProperties", {}) or {}),
            "schema_fields": [field.fieldPath for field in getattr(schema, "fields", []) or []],
            "owners": [str(owner.owner) for owner in getattr(ownership, "owners", []) or []],
            "upstreams": [str(item.dataset) for item in getattr(lineage, "upstreams", []) or []],
        }

    def write_resolution(self, urn: str, receipt: dict[str, Any]) -> None:
        from datahub.specific.dataset import DatasetPatchBuilder

        builder = DatasetPatchBuilder(urn)
        builder.add_custom_property("resolve.last_status", receipt["status"])
        builder.add_custom_property("resolve.last_manifest_sha256", receipt["receipt_sha256"])
        builder.add_custom_property("resolve.last_checked_at", receipt["checked_at"])
        builder.add_custom_property("resolve.finding_count", str(len(receipt["findings"])))
        for proposal in builder.build():
            self._graph.emit(proposal)

