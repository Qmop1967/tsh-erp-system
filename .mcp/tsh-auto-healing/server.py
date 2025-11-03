#!/usr/bin/env python3
"""
TSH Auto-Healing MCP Server
Provides Claude Code with tools to monitor and heal the TSH ERP System
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp")
    exit(1)

# Server configuration
PROJECT_ROOT = Path(os.getenv("TSH_PROJECT_ROOT", "/Users/khaleelal-mulla/TSH_ERP_Ecosystem"))
VPS_HOST = os.getenv("TSH_VPS_HOST", "167.71.39.50")
VPS_USER = os.getenv("TSH_VPS_USER", "root")

# Initialize MCP server
app = Server("tsh-auto-healing")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available auto-healing tools"""
    return [
        Tool(
            name="check_system_health",
            description="Check the health of TSH ERP system on VPS",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["all", "staging", "production", "database", "zoho", "tds-worker"],
                        "description": "Component to check (default: all)",
                        "default": "all"
                    }
                }
            }
        ),
        Tool(
            name="get_healing_suggestions",
            description="Get auto-healing suggestions from the last CI/CD run",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="execute_healing_action",
            description="Execute a specific healing action on VPS",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "restart_staging",
                            "restart_production",
                            "restart_tds_worker",
                            "retry_failed_syncs",
                            "check_zoho_webhooks",
                            "clear_sync_queue"
                        ],
                        "description": "Healing action to execute"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, show what would be done without executing",
                        "default": True
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="view_system_logs",
            description="View recent logs from TSH ERP system components",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["staging", "production", "tds-worker", "auto-healing"],
                        "description": "Component to view logs for"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of log lines to retrieve",
                        "default": 50,
                        "minimum": 10,
                        "maximum": 500
                    }
                },
                "required": ["component"]
            }
        ),
        Tool(
            name="check_zoho_sync_status",
            description="Check Zoho synchronization status and statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed sync queue information",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="run_github_workflow",
            description="Trigger a specific GitHub Actions workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "enum": ["intelligent-staging", "intelligent-production", "test"],
                        "description": "Workflow to run"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch to run workflow on",
                        "default": "develop"
                    }
                },
                "required": ["workflow"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "check_system_health":
        return await check_system_health(arguments.get("component", "all"))

    elif name == "get_healing_suggestions":
        return await get_healing_suggestions()

    elif name == "execute_healing_action":
        return await execute_healing_action(
            arguments["action"],
            arguments.get("dry_run", True)
        )

    elif name == "view_system_logs":
        return await view_system_logs(
            arguments["component"],
            arguments.get("lines", 50)
        )

    elif name == "check_zoho_sync_status":
        return await check_zoho_sync_status(arguments.get("detailed", False))

    elif name == "run_github_workflow":
        return await run_github_workflow(
            arguments["workflow"],
            arguments.get("branch", "develop")
        )

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def check_system_health(component: str) -> list[TextContent]:
    """Check system health on VPS"""

    commands = {
        "all": "systemctl status tsh-erp-staging tsh-erp-production tds-core-worker postgresql --no-pager",
        "staging": "systemctl status tsh-erp-staging --no-pager && curl -f http://127.0.0.1:8002/health",
        "production": "systemctl status tsh-erp-production --no-pager && curl -f http://127.0.0.1:8001/health",
        "database": "systemctl status postgresql --no-pager && psql -U tsh_admin -d tsh_erp -c 'SELECT version();'",
        "zoho": "cd /opt/tsh_erp && python3 -c 'from app.services.zoho.zoho_client import ZohoClient; client = ZohoClient(); print(client.test_connection())'",
        "tds-worker": "systemctl status tds-core-worker --no-pager"
    }

    cmd = commands.get(component, commands["all"])

    try:
        result = subprocess.run(
            ["ssh", f"{VPS_USER}@{VPS_HOST}", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = f"🏥 System Health Check - {component}\n\n"
        output += f"{'='*60}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}\n"
        output += f"{'='*60}\n"
        output += f"Exit Code: {result.returncode}\n"

        if result.returncode == 0:
            output += "\n✅ Health check passed"
        else:
            output += "\n❌ Health check failed"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="❌ Health check timed out after 30 seconds")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def get_healing_suggestions() -> list[TextContent]:
    """Get auto-healing suggestions from GitHub Actions artifacts"""

    try:
        # Get latest workflow run
        result = subprocess.run(
            ["gh", "run", "list", "--workflow=intelligent-staging.yml", "--limit=1", "--json=databaseId"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if result.returncode != 0:
            return [TextContent(type="text", text="❌ Failed to get workflow runs")]

        runs = json.loads(result.stdout)
        if not runs:
            return [TextContent(type="text", text="ℹ️ No workflow runs found")]

        run_id = runs[0]["databaseId"]

        # Download auto-healing report artifact
        result = subprocess.run(
            ["gh", "run", "download", str(run_id), "-n", "auto-healing-report"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if result.returncode != 0:
            return [TextContent(type="text", text="ℹ️ No auto-healing report available yet")]

        # Read the suggestions file
        suggestions_file = PROJECT_ROOT / "auto_healing_suggestions.txt"
        if suggestions_file.exists():
            content = suggestions_file.read_text()
            return [TextContent(type="text", text=f"🤖 Auto-Healing Suggestions\n\n{content}")]
        else:
            return [TextContent(type="text", text="ℹ️ No suggestions file found in artifact")]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def execute_healing_action(action: str, dry_run: bool = True) -> list[TextContent]:
    """Execute a healing action on VPS"""

    actions = {
        "restart_staging": "systemctl restart tsh-erp-staging && sleep 3 && systemctl status tsh-erp-staging",
        "restart_production": "systemctl restart tsh-erp-production && sleep 3 && systemctl status tsh-erp-production",
        "restart_tds_worker": "systemctl restart tds-core-worker && sleep 3 && systemctl status tds-core-worker",
        "retry_failed_syncs": "cd /opt/tsh_erp && python3 -c \"import psycopg2; conn = psycopg2.connect('postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp'); cur = conn.cursor(); cur.execute('UPDATE tds_sync_queue SET status=\\'pending\\', retry_count=0 WHERE status=\\'failed\\''); print(f'Updated {cur.rowcount} failed syncs'); conn.commit()\"",
        "check_zoho_webhooks": "cd /opt/tsh_erp && python3 -c 'from app.services.zoho.zoho_client import ZohoClient; client = ZohoClient(); print(client.check_webhook_health())'",
        "clear_sync_queue": "cd /opt/tsh_erp && python3 -c \"import psycopg2; conn = psycopg2.connect('postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp'); cur = conn.cursor(); cur.execute('DELETE FROM tds_sync_queue WHERE status=\\'completed\\' AND updated_at < NOW() - INTERVAL \\'7 days\\''); print(f'Cleared {cur.rowcount} old completed syncs'); conn.commit()\""
    }

    cmd = actions.get(action)
    if not cmd:
        return [TextContent(type="text", text=f"❌ Unknown action: {action}")]

    if dry_run:
        output = f"🔍 DRY RUN - Would execute:\n\n"
        output += f"Action: {action}\n"
        output += f"Command: {cmd}\n\n"
        output += f"To execute for real, set dry_run=false"
        return [TextContent(type="text", text=output)]

    try:
        result = subprocess.run(
            ["ssh", f"{VPS_USER}@{VPS_HOST}", cmd],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = f"🔧 Healing Action Executed: {action}\n\n"
        output += f"{'='*60}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}\n"
        output += f"{'='*60}\n"
        output += f"Exit Code: {result.returncode}\n"

        if result.returncode == 0:
            output += "\n✅ Action completed successfully"
        else:
            output += "\n❌ Action failed"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def view_system_logs(component: str, lines: int = 50) -> list[TextContent]:
    """View system logs"""

    services = {
        "staging": "tsh-erp-staging",
        "production": "tsh-erp-production",
        "tds-worker": "tds-core-worker",
        "auto-healing": "cat /var/log/tsh_erp/auto_healing.log"
    }

    if component in ["staging", "production", "tds-worker"]:
        cmd = f"journalctl -u {services[component]} -n {lines} --no-pager"
    else:
        cmd = f"{services[component]} | tail -n {lines}"

    try:
        result = subprocess.run(
            ["ssh", f"{VPS_USER}@{VPS_HOST}", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = f"📋 System Logs - {component} (last {lines} lines)\n\n"
        output += f"{'='*60}\n"
        output += result.stdout
        output += f"\n{'='*60}\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def check_zoho_sync_status(detailed: bool = False) -> list[TextContent]:
    """Check Zoho synchronization status"""

    cmd = """
    PGPASSWORD='TSH@2025Secure!Production' psql -U tsh_admin -d tsh_erp -c "
    SELECT
        status,
        COUNT(*) as count,
        MIN(created_at) as oldest,
        MAX(created_at) as newest
    FROM tds_sync_queue
    GROUP BY status
    ORDER BY status;
    "
    """

    if detailed:
        cmd += """
        PGPASSWORD='TSH@2025Secure!Production' psql -U tsh_admin -d tsh_erp -c "
        SELECT * FROM tds_sync_queue
        WHERE status IN ('failed', 'pending')
        ORDER BY created_at DESC
        LIMIT 20;
        "
        """

    try:
        result = subprocess.run(
            ["ssh", f"{VPS_USER}@{VPS_HOST}", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = f"🔄 Zoho Sync Status\n\n"
        output += f"{'='*60}\n"
        output += result.stdout
        output += f"\n{'='*60}\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def run_github_workflow(workflow: str, branch: str = "develop") -> list[TextContent]:
    """Trigger a GitHub Actions workflow"""

    workflow_files = {
        "intelligent-staging": "intelligent-staging.yml",
        "intelligent-production": "intelligent-production.yml",
        "test": "test.yml"
    }

    workflow_file = workflow_files.get(workflow)
    if not workflow_file:
        return [TextContent(type="text", text=f"❌ Unknown workflow: {workflow}")]

    try:
        # Trigger workflow
        result = subprocess.run(
            ["gh", "workflow", "run", workflow_file, "--ref", branch],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if result.returncode != 0:
            return [TextContent(type="text", text=f"❌ Failed to trigger workflow:\n{result.stderr}")]

        # Get latest run
        await asyncio.sleep(2)  # Wait for workflow to register

        result = subprocess.run(
            ["gh", "run", "list", f"--workflow={workflow_file}", "--limit=1", "--json=databaseId,status,conclusion"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if result.returncode == 0:
            runs = json.loads(result.stdout)
            if runs:
                run = runs[0]
                output = f"✅ Workflow triggered successfully\n\n"
                output += f"Workflow: {workflow}\n"
                output += f"Branch: {branch}\n"
                output += f"Run ID: {run['databaseId']}\n"
                output += f"Status: {run['status']}\n"
                output += f"\nMonitor: gh run watch {run['databaseId']}"
                return [TextContent(type="text", text=output)]

        return [TextContent(type="text", text=f"✅ Workflow triggered (check GitHub Actions)")]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
