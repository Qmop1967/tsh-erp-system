"""
User Processor
==============

Processes and transforms Zoho user data.

معالج المستخدمين - تحويل والتحقق من بيانات المستخدمين

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class UserProcessor:
    """
    Zoho User data processor
    معالج بيانات مستخدمي Zoho

    Validates, transforms, and prepares Zoho user data for local storage.
    """

    @staticmethod
    def validate(user_data: Dict[str, Any]) -> bool:
        """
        Validate user data

        Args:
            user_data: Zoho user data

        Returns:
            bool: True if valid
        """
        required_fields = ['user_id', 'name', 'email']

        for field in required_fields:
            if field not in user_data or not user_data[field]:
                logger.warning(f"User missing required field: {field}")
                return False

        return True

    @staticmethod
    def transform(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho user data to local format

        Args:
            user_data: Zoho user data

        Returns:
            dict: Transformed user data
        """
        transformed = {
            # IDs
            'zoho_user_id': user_data.get('user_id'),

            # Basic information
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'phone': user_data.get('phone'),
            'mobile': user_data.get('mobile'),

            # Role and permissions
            'role_id': user_data.get('role_id'),
            'role_name': user_data.get('role_name'),
            'user_role': user_data.get('user_role'),

            # Status
            'status': user_data.get('status', 'active'),
            'is_active': user_data.get('status') == 'active',
            'is_current_user': user_data.get('is_current_user', False),

            # Additional info
            'photo_url': user_data.get('photo_url'),
            'language_code': user_data.get('language_code'),
            'timezone': user_data.get('time_zone'),
            'date_format': user_data.get('date_format'),
            'time_format': user_data.get('time_format'),

            # Metadata
            'created_time': user_data.get('created_time'),
            'last_modified_time': user_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': user_data
        }

        return transformed

    @staticmethod
    def needs_update(
        existing_user: Dict[str, Any],
        new_user_data: Dict[str, Any]
    ) -> bool:
        """
        Check if user needs to be updated

        Args:
            existing_user: Existing user data in database
            new_user_data: New user data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_user.get('last_modified_time')
        new_modified = new_user_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified

    @staticmethod
    def map_to_erp_role(zoho_role: str) -> str:
        """
        Map Zoho role to TSH ERP role

        Args:
            zoho_role: Zoho role name

        Returns:
            str: TSH ERP role name
        """
        role_mapping = {
            'admin': 'admin',
            'administrator': 'admin',
            'manager': 'manager',
            'staff': 'employee',
            'salesperson': 'salesperson',
            'warehouse': 'inventory_manager',
            'accountant': 'accountant',
        }

        return role_mapping.get(zoho_role.lower(), 'employee')
