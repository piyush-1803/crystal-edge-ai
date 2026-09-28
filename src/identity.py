from dataclasses import dataclass, asdict
from typing import Dict, Any
from src.config import NodeConfig


@dataclass(frozen=True)
class NodeIdentity:
    """
    Immutable Crystal Node Identity representation.
    Provides node identification attributes for health checks and network interaction.
    """
    node_id: str
    node_name: str
    host: str
    port: int

    @classmethod
    def from_config(cls, config: NodeConfig) -> "NodeIdentity":
        return cls(
            node_id=config.node_id,
            node_name=config.node_name,
            host=config.host,
            port=config.port,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
