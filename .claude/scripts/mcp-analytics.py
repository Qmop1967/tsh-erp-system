#!/usr/bin/env python3
"""
MCP Usage Analytics - TSH ERP Ecosystem
Tracks and analyzes MCP server usage patterns

Usage: python3 mcp-analytics.py [--report] [--optimize]
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

# Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.NC} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.NC} {msg}")

def log_error(msg):
    print(f"{Colors.RED}✗{Colors.NC} {msg}")

def log_header(msg):
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}{msg}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}\n")

class MCPAnalytics:
    def __init__(self):
        self.mcp_config_path = Path('.claude/.mcp.json')
        self.state_path = Path('.claude/state/current-phase.json')
        self.usage_log_path = Path('.claude/state/mcp_usage_log.json')

        # Initialize usage log if it doesn't exist
        if not self.usage_log_path.exists():
            self.init_usage_log()

        self.load_config()
        self.load_usage_log()

    def init_usage_log(self):
        """Initialize MCP usage log"""
        initial_log = {
            "created": datetime.utcnow().isoformat() + "Z",
            "sessions": [],
            "total_sessions": 0,
            "total_token_usage": 0
        }

        self.usage_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_log_path, 'w') as f:
            json.dump(initial_log, f, indent=2)

        log_success(f"Initialized usage log: {self.usage_log_path}")

    def load_config(self):
        """Load MCP configuration"""
        try:
            with open(self.mcp_config_path, 'r') as f:
                self.mcp_config = json.load(f)
            log_success("Loaded MCP configuration")
        except Exception as e:
            log_error(f"Failed to load MCP config: {e}")
            sys.exit(1)

    def load_usage_log(self):
        """Load usage log"""
        try:
            with open(self.usage_log_path, 'r') as f:
                self.usage_log = json.load(f)
            log_success("Loaded usage log")
        except Exception as e:
            log_warning(f"Could not load usage log: {e}")
            self.usage_log = {
                "created": datetime.utcnow().isoformat() + "Z",
                "sessions": [],
                "total_sessions": 0,
                "total_token_usage": 0
            }

    def log_session(self, mcps_used, task_type, token_usage):
        """Log a session's MCP usage"""
        session = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "mcps_used": mcps_used,
            "task_type": task_type,
            "token_usage": token_usage
        }

        self.usage_log["sessions"].append(session)
        self.usage_log["total_sessions"] += 1
        self.usage_log["total_token_usage"] += token_usage

        # Keep only last 100 sessions
        self.usage_log["sessions"] = self.usage_log["sessions"][-100:]

        with open(self.usage_log_path, 'w') as f:
            json.dump(self.usage_log, f, indent=2)

        log_success(f"Logged session: {task_type} with {len(mcps_used)} MCPs")

    def generate_report(self):
        """Generate usage analytics report"""
        log_header("MCP Usage Analytics Report")

        # Basic stats
        total_sessions = self.usage_log.get("total_sessions", 0)
        total_tokens = self.usage_log.get("total_token_usage", 0)
        sessions = self.usage_log.get("sessions", [])

        print(f"📊 Overview:")
        print(f"  Total Sessions: {total_sessions}")
        print(f"  Total Token Usage: {total_tokens:,}")
        print(f"  Average Tokens per Session: {total_tokens // total_sessions if total_sessions > 0 else 0:,}")
        print()

        if not sessions:
            log_warning("No session data available yet")
            return

        # MCP usage frequency
        mcp_counter = Counter()
        task_counter = Counter()

        for session in sessions:
            for mcp in session.get("mcps_used", []):
                mcp_counter[mcp] += 1
            task_type = session.get("task_type", "unknown")
            task_counter[task_type] += 1

        # Most used MCPs
        print(f"🔌 MCP Usage Frequency:")
        for mcp, count in mcp_counter.most_common():
            percentage = (count / len(sessions)) * 100
            print(f"  {mcp}: {count} sessions ({percentage:.1f}%)")
        print()

        # Task type distribution
        print(f"📋 Task Type Distribution:")
        for task, count in task_counter.most_common():
            percentage = (count / len(sessions)) * 100
            print(f"  {task}: {count} sessions ({percentage:.1f}%)")
        print()

        # Token analysis
        token_by_mcp = defaultdict(int)
        sessions_by_mcp = defaultdict(int)

        for session in sessions:
            mcps = session.get("mcps_used", [])
            tokens = session.get("token_usage", 0)

            if mcps:
                tokens_per_mcp = tokens // len(mcps)
                for mcp in mcps:
                    token_by_mcp[mcp] += tokens_per_mcp
                    sessions_by_mcp[mcp] += 1

        print(f"💰 Token Usage by MCP:")
        for mcp in mcp_counter.keys():
            avg_tokens = token_by_mcp[mcp] // sessions_by_mcp[mcp] if sessions_by_mcp[mcp] > 0 else 0
            print(f"  {mcp}:")
            print(f"    Total: {token_by_mcp[mcp]:,} tokens")
            print(f"    Average per session: {avg_tokens:,} tokens")
        print()

        # Current MCP configuration
        print(f"⚙️  Current MCP Configuration:")
        for mcp_name, mcp_config in self.mcp_config.get("mcpServers", {}).items():
            enabled = "✓ Enabled" if mcp_config.get("enabled", False) else "✗ Disabled"
            priority = mcp_config.get("priority", "N/A")
            token_cost = mcp_config.get("token_cost", "N/A")
            print(f"  {mcp_name}:")
            print(f"    Status: {enabled}")
            print(f"    Priority: {priority}")
            print(f"    Token Cost: {token_cost}")
        print()

    def optimize_recommendations(self):
        """Provide optimization recommendations"""
        log_header("Optimization Recommendations")

        sessions = self.usage_log.get("sessions", [])
        if not sessions:
            log_warning("Not enough data for recommendations")
            return

        # Calculate MCP usage patterns
        mcp_usage = Counter()
        for session in sessions:
            for mcp in session.get("mcps_used", []):
                mcp_usage[mcp] += 1

        total_sessions = len(sessions)
        recommendations = []

        # Analyze each MCP
        for mcp_name, mcp_config in self.mcp_config.get("mcpServers", {}).items():
            usage_count = mcp_usage.get(mcp_name, 0)
            usage_percentage = (usage_count / total_sessions * 100) if total_sessions > 0 else 0
            is_enabled = mcp_config.get("enabled", False)
            priority = mcp_config.get("priority", "medium")

            # High usage but disabled
            if usage_percentage > 50 and not is_enabled:
                recommendations.append({
                    "type": "enable",
                    "priority": "high",
                    "mcp": mcp_name,
                    "reason": f"Used in {usage_percentage:.1f}% of sessions but currently disabled"
                })

            # Low usage but enabled
            elif usage_percentage < 10 and is_enabled:
                recommendations.append({
                    "type": "disable",
                    "priority": "medium",
                    "mcp": mcp_name,
                    "reason": f"Only used in {usage_percentage:.1f}% of sessions but currently enabled"
                })

            # High usage with low priority
            elif usage_percentage > 70 and priority == "low":
                recommendations.append({
                    "type": "upgrade_priority",
                    "priority": "high",
                    "mcp": mcp_name,
                    "reason": f"Used in {usage_percentage:.1f}% of sessions but has low priority"
                })

        # Display recommendations
        if recommendations:
            high_priority = [r for r in recommendations if r["priority"] == "high"]
            medium_priority = [r for r in recommendations if r["priority"] == "medium"]

            if high_priority:
                print(f"🔴 High Priority Recommendations:")
                for rec in high_priority:
                    print(f"  • {rec['type'].upper()}: {rec['mcp']}")
                    print(f"    Reason: {rec['reason']}")
                print()

            if medium_priority:
                print(f"🟡 Medium Priority Recommendations:")
                for rec in medium_priority:
                    print(f"  • {rec['type'].upper()}: {rec['mcp']}")
                    print(f"    Reason: {rec['reason']}")
                print()
        else:
            log_success("MCP configuration is well optimized!")

        # Token budget analysis
        token_limit = self.mcp_config.get("token_budget", {}).get("session_limit", 200000)
        avg_usage = self.usage_log.get("total_token_usage", 0) // max(total_sessions, 1)
        usage_percentage = (avg_usage / token_limit * 100)

        print(f"💰 Token Budget Analysis:")
        print(f"  Average Usage: {avg_usage:,} / {token_limit:,} ({usage_percentage:.1f}%)")

        if usage_percentage > 80:
            log_warning("High token usage - consider disabling unused MCPs")
        elif usage_percentage < 30:
            log_success("Token usage is well within budget")
        else:
            log_info("Token usage is moderate")
        print()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='MCP Usage Analytics')
    parser.add_argument('--report', action='store_true', help='Generate usage report')
    parser.add_argument('--optimize', action='store_true', help='Show optimization recommendations')
    parser.add_argument('--log-session', nargs=3, metavar=('MCPS', 'TASK', 'TOKENS'),
                       help='Log a session (mcps as comma-separated, task type, token count)')

    args = parser.parse_args()

    analytics = MCPAnalytics()

    if args.log_session:
        mcps = args.log_session[0].split(',')
        task = args.log_session[1]
        tokens = int(args.log_session[2])
        analytics.log_session(mcps, task, tokens)

    if args.report or (not args.optimize and not args.log_session):
        analytics.generate_report()

    if args.optimize:
        analytics.optimize_recommendations()

    if not any([args.report, args.optimize, args.log_session]):
        # Default: show both report and recommendations
        analytics.generate_report()
        analytics.optimize_recommendations()

if __name__ == '__main__':
    main()
