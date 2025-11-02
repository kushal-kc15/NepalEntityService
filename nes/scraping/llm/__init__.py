"""LLM-based entity scraping module."""

from .base import LLMEntityScraper
from .google_cloud import GoogleCloudEntityScraper

__all__ = ["LLMEntityScraper", "GoogleCloudEntityScraper"]
