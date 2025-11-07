"""
Base Repository Interface

Defines the contract for all repository implementations.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any

T = TypeVar('T')  # Entity type
ID = TypeVar('ID')  # ID type


class IBaseRepository(ABC, Generic[T, ID]):
    """
    Base repository interface for data access operations.

    This interface defines common CRUD operations that all repositories
    must implement. It follows the Repository Pattern to abstract
    data access logic from business logic.
    """

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """
        Get an entity by its ID.

        Args:
            id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[T]:
        """
        Get all entities with optional pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filters

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Create a new entity.

        Args:
            entity: Entity to create

        Returns:
            Created entity with generated ID
        """
        pass

    @abstractmethod
    async def update(self, id: ID, entity: T) -> Optional[T]:
        """
        Update an existing entity.

        Args:
            id: Entity ID
            entity: Updated entity data

        Returns:
            Updated entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """
        Delete an entity.

        Args:
            id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, id: ID) -> bool:
        """
        Check if an entity exists.

        Args:
            id: Entity ID

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def count(self, **filters) -> int:
        """
        Count entities with optional filtering.

        Args:
            **filters: Optional filters

        Returns:
            Number of entities
        """
        pass

    @abstractmethod
    async def find_one(self, **filters) -> Optional[T]:
        """
        Find a single entity by filters.

        Args:
            **filters: Search filters

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[T]:
        """
        Find multiple entities by filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Search filters

        Returns:
            List of entities matching filters
        """
        pass
