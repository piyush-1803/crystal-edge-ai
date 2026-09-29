import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List


@dataclass
class NodeConfig:
    """
    Crystal Node Configuration.
    Defines identity, network binding, local storage location, and peer list for a node.
    """
    node_id: str = "node-a"
    node_name: str = "Crystal Node A"
    host: str = "127.0.0.1"
    port: int = 8001
    data_directory: str = "./data/node_a"
    peers: List[Dict[str, Any]] = field(default_factory=list)
    llm_server_url: Optional[str] = "http://127.0.0.1:8080"
    llm_binary_path: Optional[str] = None
    llm_model_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NodeConfig":
        return cls(
            node_id=str(data.get("node_id", "node-a")),
            node_name=str(data.get("node_name", "Crystal Node A")),
            host=str(data.get("host", "127.0.0.1")),
            port=int(data.get("port", 8001)),
            data_directory=str(data.get("data_directory", "./data/node_a")),
            peers=list(data.get("peers", [])),
            llm_server_url=data.get("llm_server_url", "http://127.0.0.1:8080"),
            llm_binary_path=data.get("llm_binary_path"),
            llm_model_path=data.get("llm_model_path"),
        )

    @classmethod
    def from_file(cls, filepath: str) -> "NodeConfig":
        """Load configuration from a JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "NodeConfig":
        """
        Loads configuration prioritizing explicit file path, environment variable, 
        or default settings.
        """
        path = config_path or os.getenv("CRYSTAL_CONFIG_PATH")
        if path and os.path.exists(path):
            config = cls.from_file(path)
        else:
            config = cls()

        # Environment variable overrides
        if os.getenv("CRYSTAL_NODE_ID"):
            config.node_id = os.getenv("CRYSTAL_NODE_ID")
        if os.getenv("CRYSTAL_NODE_NAME"):
            config.node_name = os.getenv("CRYSTAL_NODE_NAME")
        if os.getenv("CRYSTAL_HOST"):
            config.host = os.getenv("CRYSTAL_HOST")
        if os.getenv("CRYSTAL_PORT"):
            config.port = int(os.getenv("CRYSTAL_PORT"))
        if os.getenv("CRYSTAL_DATA_DIR"):
            config.data_directory = os.getenv("CRYSTAL_DATA_DIR")
        if os.getenv("CRYSTAL_LLM_URL"):
            config.llm_server_url = os.getenv("CRYSTAL_LLM_URL")
        if os.getenv("CRYSTAL_LLAMA_BIN"):
            config.llm_binary_path = os.getenv("CRYSTAL_LLAMA_BIN")
        if os.getenv("CRYSTAL_MODEL_PATH"):
            config.llm_model_path = os.getenv("CRYSTAL_MODEL_PATH")

        return config
