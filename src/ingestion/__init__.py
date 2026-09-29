"""
Ingestion Package for Crystal Node Knowledge.
Provides utilities to ingest article files into Network Knowledge storage.
"""

from src.ingestion.article_ingester import ArticleIngester, ingest_node_articles

__all__ = ["ArticleIngester", "ingest_node_articles"]
