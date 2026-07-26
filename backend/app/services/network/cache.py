"""Cache engine for the NetworkX Graph models."""

from __future__ import annotations

from typing import Any

# Cache for the fully compiled NetworkX Graph
_compiled_graph: Any = None


def get_cached_graph() -> Any | None:
    """Retrieve the cached compiled NetworkX Graph."""
    return _compiled_graph


def set_cached_graph(graph: Any) -> None:
    """Cache the compiled NetworkX Graph."""
    global _compiled_graph
    _compiled_graph = graph


def clear_network_cache() -> None:
    """Clear cached NetworkX Graph."""
    global _compiled_graph
    _compiled_graph = None
