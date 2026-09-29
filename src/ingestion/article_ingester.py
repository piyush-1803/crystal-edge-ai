import os
import argparse
from pathlib import Path
from typing import List, Optional

from src.config import NodeConfig
from src.node import create_app
from src.services.network_knowledge_service import NetworkKnowledgeService
from src.storage.network_knowledge import NetworkKnowledgeRecord


class ArticleIngester:
    """
    Ingests text article files from a local directory into a node's Network Knowledge Service.
    """

    def __init__(self, service: NetworkKnowledgeService, source_node_id: str = "node-a"):
        self.service = service
        self.source_node_id = source_node_id

    def ingest_directory(self, directory_path: str) -> List[NetworkKnowledgeRecord]:
        """
        Scans directory for .txt files, reads content, and ingests them as shareable network knowledge.
        Prevents duplicate insertion if article is already ingested.
        """
        dir_path = Path(directory_path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileNotFoundError(f"Articles directory not found: {directory_path}")

        ingested_records = []
        txt_files = sorted(dir_path.glob("*.txt"))

        # Fetch existing shareable records for duplicate check
        existing_records = self.service.list_shareable_knowledge()
        existing_contents = {rec.content.strip() for rec in existing_records}

        for file_path in txt_files:
            article_title = file_path.stem
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()

            if not raw_text.startswith("Title:"):
                formatted_content = f"Title: {article_title}\n\n{raw_text}"
            else:
                formatted_content = raw_text

            # Duplicate check: compare content or title header against existing records
            is_duplicate = formatted_content in existing_contents or any(
                f"Title: {article_title}" in rec.content for rec in existing_records
            )

            if is_duplicate:
                print(f"Skipping duplicate article: '{article_title}'")
                continue

            record = self.service.add_knowledge(
                content=formatted_content,
                is_shareable=True,
                source_node_id=self.source_node_id,
            )
            ingested_records.append(record)
            existing_contents.add(formatted_content)
            print(f"Successfully ingested article: '{article_title}' (ID: {record.id})")

        return ingested_records


def ingest_node_articles(config_path: str, articles_dir: str) -> List[NetworkKnowledgeRecord]:
    """
    Helper function to load node application, locate Network Knowledge Service, and run ingestion.
    """
    config = NodeConfig.load(config_path=config_path)
    app = create_app(config)
    service: NetworkKnowledgeService = app.state.network_knowledge_service

    ingester = ArticleIngester(service=service, source_node_id=config.node_id)
    return ingester.ingest_directory(articles_dir)


def main():
    parser = argparse.ArgumentParser(description="Ingest text articles into Crystal Network Knowledge")
    parser.add_argument(
        "--config",
        type=str,
        default="config/node_a.json",
        help="Path to node JSON configuration file",
    )
    parser.add_argument(
        "--articles-dir",
        type=str,
        default="data/node_a/shareable/articles",
        help="Path to directory containing .txt articles",
    )
    args = parser.parse_args()

    records = ingest_node_articles(config_path=args.config, articles_dir=args.articles_dir)
    print(f"\nIngestion Complete: {len(records)} new article(s) ingested into Network Knowledge.")


if __name__ == "__main__":
    main()
