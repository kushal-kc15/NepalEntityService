"""Base LLM entity scraper."""

from abc import ABC, abstractmethod
from typing import List, Optional

from nes.core.models import Entity


class LLMEntityScraper(ABC):
    """Abstract base class for LLM-based entity extraction from unstructured text."""

    @abstractmethod
    def extract_entities(
        self, text: str, entity_types: Optional[List[str]] = None
    ) -> List[Entity]:
        """Extract entities from unstructured text using LLM.

        Args:
            text: Unstructured text to extract entities from
            entity_types: Optional list of entity types to focus on (e.g., ["Person", "Organization"])

        Returns:
            List of extracted Entity objects
        """
        pass

    @abstractmethod
    def extract_single_entity(self, text: str, entity_type: str) -> Optional[Entity]:
        """Extract a single entity of specified type from text.

        Args:
            text: Unstructured text containing entity information
            entity_type: Type of entity to extract (e.g., "Person", "Organization")

        Returns:
            Single Entity object or None if extraction fails
        """
        pass
