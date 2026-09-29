import os
import pytest
from pathlib import Path
from src.config import NodeConfig
from src.node import create_app
from src.storage import PrivateMemoryStore, NetworkKnowledgeStore
from src.services import PrivateMemoryService, NetworkKnowledgeService
from src.ingestion.article_ingester import ArticleIngester, ingest_node_articles


def test_single_article_ingestion(tmp_path):
    # Setup temporary storage
    db_file = str(tmp_path / "network_knowledge.sqlite")
    net_store = NetworkKnowledgeStore(db_path=db_file, node_id="node-a")
    net_service = NetworkKnowledgeService(store=net_store)

    priv_db = str(tmp_path / "private_memory.sqlite")
    priv_store = PrivateMemoryStore(db_path=priv_db)
    priv_service = PrivateMemoryService(store=priv_store)

    # Create dummy article
    articles_dir = tmp_path / "shareable_articles"
    articles_dir.mkdir()
    sample_file = articles_dir / "Test Topic.txt"
    sample_file.write_text("Title: Test Topic\nSource: Unit Test\n\nSample content text for testing.", encoding="utf-8")

    ingester = ArticleIngester(service=net_service, source_node_id="node-a")
    records = ingester.ingest_directory(str(articles_dir))

    assert len(records) == 1
    rec = records[0]
    assert rec.source_node_id == "node-a"
    assert rec.is_shareable is True
    assert "Title: Test Topic" in rec.content
    assert "Sample content text for testing." in rec.content

    # Verify Private Memory is completely unaffected
    assert len(priv_service.list_private_memory()) == 0


def test_duplicate_article_ingestion_prevention(tmp_path):
    db_file = str(tmp_path / "network_knowledge.sqlite")
    net_store = NetworkKnowledgeStore(db_path=db_file, node_id="node-a")
    net_service = NetworkKnowledgeService(store=net_store)

    articles_dir = tmp_path / "shareable_articles"
    articles_dir.mkdir()
    sample_file = articles_dir / "Duplicate Test.txt"
    sample_file.write_text("Title: Duplicate Test\n\nContent body.", encoding="utf-8")

    ingester = ArticleIngester(service=net_service, source_node_id="node-a")

    # First ingestion
    first_run = ingester.ingest_directory(str(articles_dir))
    assert len(first_run) == 1

    # Second ingestion should skip duplicate
    second_run = ingester.ingest_directory(str(articles_dir))
    assert len(second_run) == 0

    # Total stored shareable knowledge should remain 1
    assert len(net_service.list_shareable_knowledge()) == 1


def test_node_a_actual_articles_ingestion(tmp_path):
    node_a_dir = Path("data/node_a/shareable_articles")
    assert node_a_dir.exists(), "data/node_a/shareable_articles directory must exist"

    data_dir = str(tmp_path / "node_a_data")
    config = NodeConfig(node_id="node-a", node_name="Node A Test", port=8001, data_directory=data_dir)
    app = create_app(config)

    net_service: NetworkKnowledgeService = app.state.network_knowledge_service
    priv_service: PrivateMemoryService = app.state.private_memory_service

    ingester = ArticleIngester(service=net_service, source_node_id=config.node_id)
    records = ingester.ingest_directory(str(node_a_dir))

    # Verify 3 articles ingested
    assert len(records) == 3

    shareable_list = net_service.list_shareable_knowledge()
    assert len(shareable_list) == 3

    # Verify each record metadata
    titles_found = []
    for rec in shareable_list:
        assert rec.source_node_id == "node-a"
        assert rec.is_shareable is True
        if "Asteria (mythology)" in rec.content:
            titles_found.append("Asteria (mythology)")
        elif "National Institute of Technology Calicut" in rec.content:
            titles_found.append("National Institute of Technology Calicut")
        elif "Quantum computing" in rec.content:
            titles_found.append("Quantum computing")

    assert len(titles_found) == 3
    assert "Asteria (mythology)" in titles_found
    assert "National Institute of Technology Calicut" in titles_found
    assert "Quantum computing" in titles_found

    # Verify Private memory remains completely unaffected (0 records)
    assert len(priv_service.list_private_memory()) == 0
