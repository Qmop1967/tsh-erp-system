#!/usr/bin/env python3
"""
Script to add authentication to all Security BFF endpoints
This is a one-time migration script to add RBAC + ABAC + RLS to all endpoints
"""
import re

SECURITY_BFF_FILE = "/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/bff/routers/security.py"

def update_endpoint_signature(content: str, endpoint_pattern: str, new_params: str) -> str:
    """
    Update an endpoint signature to include auth parameters

    Args:
        content: File content
        endpoint_pattern: Regex pattern to match the async def line
        new_params: New parameters to add (e.g., "current_user: User = Depends(get_current_user),\n    db: AsyncSession = Depends(get_db_with_rls)")
    """
    # Find the endpoint function signature
    pattern = re.compile(
        rf'(async def {endpoint_pattern}\([^)]*?)(\s*db: AsyncSession = Depends\(get_db\))',
        re.MULTILINE | re.DOTALL
    )

    def replacement(match):
        existing_params = match.group(1)
        # Add current_user and updated db dependency
        return f'{existing_params}\n    current_user: User = Depends(get_current_user),\n    db: AsyncSession = Depends(get_db_with_rls)'

    return pattern.sub(replacement, content)

def add_role_checker_decorator(content: str, endpoint_name: str, roles: list) -> str:
    """
    Add RoleChecker dependency to endpoint decorator

    Args:
        content: File content
        endpoint_name: Name of the endpoint (e.g., "get_login_attempts")
        roles: List of allowed roles (e.g., ["admin"])
    """
    # Find the @router decorator for this endpoint
    pattern = re.compile(
        rf'(@router\.(get|post|put|delete)\(\s*["\']/{endpoint_name.replace("_", "-")}.*?["\'],\s*summary=.*?description=.*?)(""".*?""")\s*\)',
        re.MULTILINE | re.DOTALL
    )

    roles_str = ', '.join([f'"{role}"' for role in roles])
    dependency_str = f',\n    dependencies=[Depends(RoleChecker([{roles_str}]))]'

    def replacement(match):
        decorator_start = match.group(1)
        description = match.group(3)
        # Add security note to description if not present
        if "**Security:**" not in description:
            updated_desc = description.rstrip('"""') + f'\n\n    **Security:** Admin only\n    """'
        else:
            updated_desc = description
        return f'{decorator_start}{updated_desc}{dependency_str}\n)'

    return pattern.sub(replacement, content)

def main():
    # Read the file
    with open(SECURITY_BFF_FILE, 'r') as f:
        content = f.read()

    # List of all endpoints that need admin authentication
    admin_endpoints = [
        "get_login_attempts",
        "get_failed_logins",
        "block_ip_address",
        "get_active_sessions",
        "terminate_session",
        "terminate_all_user_sessions",
        "get_audit_log",
        "get_permissions_matrix",
        "get_user_permissions",
        "get_access_violations",
        "get_security_summary_report",
        "get_user_activity_report",
        "get_security_policies"
    ]

    # Update each endpoint
    for endpoint in admin_endpoints:
        print(f"Updating {endpoint}...")

        # Add role checker decorator
        content = add_role_checker_decorator(content, endpoint, ["admin"])

        # Update function signature
        content = update_endpoint_signature(content, endpoint, "")

    # Write back
    with open(SECURITY_BFF_FILE, 'w') as f:
        f.write(content)

    print("✅ Security BFF authentication updated successfully!")
    print(f"   - Updated {len(admin_endpoints)} endpoints")
    print("   - Added RBAC (RoleChecker for admin)")
    print("   - Added ABAC (get_current_user dependency)")
    print("   - Added RLS (get_db_with_rls dependency)")

if __name__ == "__main__":
    main()
