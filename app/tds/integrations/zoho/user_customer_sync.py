"""
User and Customer-Salesperson Sync Service
===========================================

Handles syncing users from Zoho Books and mapping customer ownership relationships.

Key Features:
- Sync users from Zoho Books API
- Map Zoho user IDs to TSH ERP user IDs
- Assign customers to salespersons based on Zoho owner_id
- Handle user role mapping (Zoho roles → TSH ERP roles)

Author: TSH ERP Team
Date: November 16, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.models.customer import Customer
from app.models.role import Role
from .client import UnifiedZohoClient, ZohoAPI
from .processors.users import UserProcessor
from .processors.customers import CustomerProcessor

logger = logging.getLogger(__name__)


class UserCustomerSyncService:
    """
    Service for syncing users and customer-salesperson relationships from Zoho
    خدمة مزامنة المستخدمين وعلاقات العملاء-مندوبي المبيعات من Zoho
    """

    def __init__(self, db: Session, zoho_client: UnifiedZohoClient):
        """
        Initialize sync service

        Args:
            db: Database session
            zoho_client: Unified Zoho API client
        """
        self.db = db
        self.zoho = zoho_client
        self.user_processor = UserProcessor()
        self.customer_processor = CustomerProcessor()

    async def sync_users_from_zoho(
        self,
        full_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Sync users from Zoho Books to TSH ERP

        Args:
            full_sync: If True, sync all users. If False, only sync updated users.

        Returns:
            dict: Sync results with counts and errors
        """
        logger.info("Starting user sync from Zoho Books")

        result = {
            "total_fetched": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": [],
            "started_at": datetime.utcnow(),
        }

        try:
            # Fetch users from Zoho Books
            logger.info("Fetching users from Zoho Books API")
            zoho_users = await self.zoho.get_all(
                api_type=ZohoAPI.BOOKS,
                endpoint="users",
                params={}
            )

            result["total_fetched"] = len(zoho_users)
            logger.info(f"Fetched {len(zoho_users)} users from Zoho Books")

            # Process each user
            for zoho_user in zoho_users:
                try:
                    # Validate user data
                    if not self.user_processor.validate(zoho_user):
                        logger.warning(f"Invalid user data: {zoho_user.get('user_id')}")
                        result["skipped"] += 1
                        continue

                    # Transform user data
                    transformed_data = self.user_processor.transform(zoho_user)
                    zoho_user_id = transformed_data['zoho_user_id']

                    # Check if user exists (by zoho_user_id or email)
                    existing_user = self.db.query(User).filter(
                        (User.zoho_user_id == zoho_user_id) |
                        (User.email == transformed_data['email'])
                    ).first()

                    if existing_user:
                        # Update existing user
                        if not full_sync and existing_user.zoho_last_sync:
                            # Check if update is needed
                            if not self.user_processor.needs_update(
                                existing_user.__dict__,
                                zoho_user
                            ):
                                result["skipped"] += 1
                                continue

                        # Update user fields
                        existing_user.name = transformed_data['name']
                        existing_user.phone = transformed_data.get('phone') or transformed_data.get('mobile')
                        existing_user.zoho_user_id = zoho_user_id
                        existing_user.zoho_last_sync = datetime.utcnow()

                        # Update is_active based on Zoho status
                        existing_user.is_active = transformed_data['is_active']

                        self.db.commit()
                        result["updated"] += 1
                        logger.info(f"Updated user: {existing_user.email}")

                    else:
                        # Create new user (with default password - user must reset)
                        from app.utils.security import get_password_hash

                        # Map Zoho role to TSH ERP role
                        role_name = self.user_processor.map_to_erp_role(
                            transformed_data.get('role_name', 'employee')
                        )

                        # Get or create role
                        role = self.db.query(Role).filter(Role.name == role_name).first()
                        if not role:
                            # Create default employee role if not exists
                            role = self.db.query(Role).filter(Role.name == 'employee').first()

                        new_user = User(
                            name=transformed_data['name'],
                            email=transformed_data['email'],
                            phone=transformed_data.get('phone') or transformed_data.get('mobile'),
                            password=get_password_hash("ChangeMe123!"),  # Default password
                            role_id=role.id if role else None,
                            is_active=transformed_data['is_active'],
                            is_salesperson=role_name == 'salesperson' if role_name else False,
                            zoho_user_id=zoho_user_id,
                            zoho_last_sync=datetime.utcnow(),
                        )

                        self.db.add(new_user)
                        self.db.commit()
                        result["created"] += 1
                        logger.info(f"Created new user: {new_user.email}")

                except Exception as e:
                    logger.error(f"Error processing user {zoho_user.get('user_id')}: {str(e)}")
                    result["errors"].append({
                        "zoho_user_id": zoho_user.get('user_id'),
                        "error": str(e)
                    })
                    self.db.rollback()

        except Exception as e:
            logger.error(f"Error during user sync: {str(e)}")
            result["errors"].append({"general_error": str(e)})

        result["completed_at"] = datetime.utcnow()
        logger.info(f"User sync completed: {result}")

        return result

    def map_owner_to_salesperson(
        self,
        zoho_owner_id: Optional[str]
    ) -> Optional[int]:
        """
        Map Zoho owner_id to TSH ERP salesperson_id

        Args:
            zoho_owner_id: Zoho user ID (owner of the contact)

        Returns:
            int: TSH ERP user ID (salesperson_id) or None if not found
        """
        if not zoho_owner_id:
            return None

        # Find user by zoho_user_id
        user = self.db.query(User).filter(
            User.zoho_user_id == zoho_owner_id
        ).first()

        if user:
            return user.id
        else:
            logger.warning(f"No TSH ERP user found for Zoho owner_id: {zoho_owner_id}")
            return None

    async def update_customer_salesperson_assignments(
        self,
        resync_all: bool = False
    ) -> Dict[str, Any]:
        """
        Update salesperson assignments for customers based on Zoho owner_id

        Args:
            resync_all: If True, update all customers. If False, only update customers with zoho_owner_id but no salesperson_id.

        Returns:
            dict: Update results with counts
        """
        logger.info("Updating customer salesperson assignments")

        result = {
            "total_checked": 0,
            "updated": 0,
            "skipped": 0,
            "errors": [],
            "started_at": datetime.utcnow(),
        }

        try:
            # Query customers that need salesperson assignment
            if resync_all:
                customers = self.db.query(Customer).filter(
                    Customer.zoho_owner_id.isnot(None)
                ).all()
            else:
                customers = self.db.query(Customer).filter(
                    and_(
                        Customer.zoho_owner_id.isnot(None),
                        Customer.salesperson_id.is_(None)
                    )
                ).all()

            result["total_checked"] = len(customers)
            logger.info(f"Found {len(customers)} customers to process")

            for customer in customers:
                try:
                    # Map Zoho owner_id to local salesperson_id
                    salesperson_id = self.map_owner_to_salesperson(customer.zoho_owner_id)

                    if salesperson_id:
                        customer.salesperson_id = salesperson_id
                        customer.zoho_last_sync = datetime.utcnow()
                        result["updated"] += 1
                        logger.info(f"Assigned salesperson {salesperson_id} to customer {customer.name}")
                    else:
                        result["skipped"] += 1
                        logger.warning(f"Could not map owner for customer {customer.name}")

                except Exception as e:
                    logger.error(f"Error updating customer {customer.id}: {str(e)}")
                    result["errors"].append({
                        "customer_id": customer.id,
                        "error": str(e)
                    })

            self.db.commit()

        except Exception as e:
            logger.error(f"Error during customer salesperson update: {str(e)}")
            result["errors"].append({"general_error": str(e)})
            self.db.rollback()

        result["completed_at"] = datetime.utcnow()
        logger.info(f"Customer salesperson update completed: {result}")

        return result

    async def get_user_mapping(self) -> Dict[str, int]:
        """
        Get a mapping of Zoho user IDs to TSH ERP user IDs

        Returns:
            dict: Mapping of {zoho_user_id: tsh_user_id}
        """
        users = self.db.query(User).filter(
            User.zoho_user_id.isnot(None)
        ).all()

        return {
            user.zoho_user_id: user.id
            for user in users
        }

    async def full_sync_pipeline(self) -> Dict[str, Any]:
        """
        Complete sync pipeline: users → customer salesperson assignments

        Returns:
            dict: Combined results from all sync operations
        """
        logger.info("Starting full user-customer sync pipeline")

        pipeline_result = {
            "user_sync": {},
            "customer_assignment_update": {},
            "started_at": datetime.utcnow(),
        }

        # Step 1: Sync users from Zoho
        logger.info("Step 1: Syncing users from Zoho Books")
        pipeline_result["user_sync"] = await self.sync_users_from_zoho(full_sync=True)

        # Step 2: Update customer salesperson assignments
        logger.info("Step 2: Updating customer salesperson assignments")
        pipeline_result["customer_assignment_update"] = await self.update_customer_salesperson_assignments(
            resync_all=True
        )

        pipeline_result["completed_at"] = datetime.utcnow()
        logger.info(f"Full sync pipeline completed: {pipeline_result}")

        return pipeline_result
