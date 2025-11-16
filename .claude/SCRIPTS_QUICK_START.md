# 🚀 Claude Code Scripts - Quick Start Guide

**5-minute guide to using the automation scripts**

---

## 📋 Available Commands

### **1. Validate Configuration**

```bash
./.claude/scripts/validate-state.sh
```

**When to use:** Before committing, after manual edits
**What it does:** Checks if state file is valid

---

### **2. Update Metrics**

```bash
./.claude/scripts/update-state.sh
```

**When to use:** Weekly, before important updates
**What it does:** Fetches latest DB metrics, checks health

---

### **3. Bump Version**

```bash
# Bug fix
./.claude/scripts/bump-version.sh patch "Fixed validation bug"

# New feature
./.claude/scripts/bump-version.sh minor "Added analytics dashboard"

# Breaking change
./.claude/scripts/bump-version.sh major "Restructured configuration"
```

**When to use:** After significant config changes
**What it does:** Updates version across all files

---

### **4. View MCP Analytics**

```bash
python3 .claude/scripts/mcp-analytics.py
```

**When to use:** Monthly optimization reviews
**What it does:** Shows MCP usage patterns and recommendations

---

## ⚡ Quick Workflows

### **Daily Workflow**

```bash
# Check everything is valid
./.claude/scripts/validate-state.sh && echo "✓ All good!"
```

### **Weekly Workflow**

```bash
# Update metrics
./.claude/scripts/update-state.sh

# Validate
./.claude/scripts/validate-state.sh
```

### **Before Git Commit**

```bash
# Validate
./.claude/scripts/validate-state.sh

# If config changed significantly
./.claude/scripts/bump-version.sh patch "Description"

# Commit
git add .claude/
git commit -m "chore: update configuration"
```

### **Monthly Optimization**

```bash
# Check usage patterns
python3 .claude/scripts/mcp-analytics.py

# Review and optimize .mcp.json based on recommendations
# Then bump version
./.claude/scripts/bump-version.sh minor "Optimized MCP config"
```

---

## 🎯 Common Use Cases

### **I edited state file manually:**

```bash
./.claude/scripts/validate-state.sh
```

### **I want fresh metrics from DB:**

```bash
./.claude/scripts/update-state.sh
```

### **I made config changes:**

```bash
./.claude/scripts/bump-version.sh patch "Your change description"
```

### **I want to optimize token usage:**

```bash
python3 .claude/scripts/mcp-analytics.py --optimize
```

---

## 🔍 Quick Reference

| Script | Purpose | Frequency |
|--------|---------|-----------|
| validate-state.sh | Check validity | Before commits |
| update-state.sh | Refresh metrics | Weekly |
| bump-version.sh | Version control | After changes |
| mcp-analytics.py | Optimization | Monthly |

---

## 📖 Full Documentation

See [`.claude/scripts/README.md`](.claude/scripts/README.md) for:
- Detailed usage instructions
- All command-line options
- Troubleshooting guide
- Integration with Git hooks
- Best practices

---

## 🆘 Troubleshooting

**Scripts not executable?**
```bash
chmod +x .claude/scripts/*.sh .claude/scripts/*.py
```

**Validation fails?**
```bash
python3 -m json.tool .claude/state/current-phase.json
```

**Need more info?**
```bash
./.claude/scripts/validate-state.sh --verbose
python3 .claude/scripts/mcp-analytics.py --help
```

---

**Created:** 2025-11-14
**Version:** 1.0.0
