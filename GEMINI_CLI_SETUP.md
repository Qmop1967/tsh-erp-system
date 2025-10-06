# ✅ Gemini CLI Installation - COMPLETE

**Status:** Successfully Installed  
**Version:** 0.7.0  
**Date:** October 5, 2025

---

## 🎉 Installation Successful!

The Google Gemini CLI has been successfully installed on your Mac.

```bash
✅ Package: @google/gemini-cli
✅ Version: 0.7.0
✅ Installation: Global (-g)
✅ Command: gemini
```

---

## 🚀 Quick Start

### 1. Interactive Mode (Default)
Launch an interactive chat session with Gemini:
```bash
gemini
```

### 2. Direct Prompt Mode
Run a single prompt without interactive mode:
```bash
gemini "What is the weather today?"
```

### 3. Prompt from Stdin
Pipe content to Gemini:
```bash
cat myfile.txt | gemini "Summarize this content"
```

### 4. Continue in Interactive Mode After Prompt
Execute a prompt and then continue chatting:
```bash
gemini -i "Help me debug this code"
```

---

## 🔧 Configuration

### Set API Key
You'll need a Google AI API key to use Gemini CLI. Get one from:
https://makersuite.google.com/app/apikey

Set it as an environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or add to your `~/.zshrc` to make it permanent:
```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📚 Common Commands

### Basic Usage
```bash
# Interactive mode
gemini

# Direct prompt
gemini "Explain quantum computing"

# Use specific model
gemini -m gemini-2.0-flash-exp "Write a poem about coding"

# Include files in context
gemini --all-files "Review my code"
```

### Advanced Features

#### Auto-Approve Mode (YOLO 🎯)
Auto-approve all suggested actions:
```bash
gemini -y "Refactor my code"
```

#### Sandbox Mode
Run code in a sandbox environment:
```bash
gemini -s "Test this Python script"
```

#### Debug Mode
See detailed logs:
```bash
gemini -d "Debug this issue"
```

#### Output Format
Get JSON output:
```bash
gemini -o json "Analyze this data"
```

---

## 🛠️ MCP Server Management

Gemini CLI supports Model Context Protocol (MCP) servers:

```bash
# Manage MCP servers
gemini mcp

# Allow specific MCP servers
gemini --allowed-mcp-server-names server1 server2
```

---

## 🧩 Extensions

### List Available Extensions
```bash
gemini -l
```

### Use Specific Extensions
```bash
gemini -e extension1 extension2 "Use these extensions"
```

### Manage Extensions
```bash
gemini extensions <command>
```

---

## ⚙️ Useful Options

| Option | Description | Example |
|--------|-------------|---------|
| `-m, --model` | Specify model | `gemini -m gemini-pro` |
| `-p, --prompt` | Direct prompt | `gemini -p "Hello"` |
| `-i, --prompt-interactive` | Prompt then interactive | `gemini -i "Start chat"` |
| `-y, --yolo` | Auto-approve actions | `gemini -y` |
| `-d, --debug` | Debug mode | `gemini -d` |
| `-o, --output-format` | Output format (text/json) | `gemini -o json` |
| `--sandbox` | Run in sandbox | `gemini -s` |
| `-a, --all-files` | Include all files | `gemini -a` |
| `-v, --version` | Show version | `gemini -v` |
| `-h, --help` | Show help | `gemini -h` |

---

## 📖 Settings File

Gemini CLI uses a settings file for persistent configuration:
- Location: `~/.config/gemini-cli/settings.json`

Example settings:
```json
{
  "model": "gemini-2.0-flash-exp",
  "telemetry": {
    "enabled": false
  },
  "ui": {
    "showMemoryUsage": true
  },
  "general": {
    "checkpointing": {
      "enabled": true
    }
  }
}
```

---

## 🎯 Example Use Cases

### 1. Code Review
```bash
gemini "Review the code in this file" < mycode.js
```

### 2. Debugging Help
```bash
gemini -d "Why is my React component not rendering?"
```

### 3. Generate Code
```bash
gemini "Create a REST API with Express.js for user management"
```

### 4. Refactoring
```bash
gemini -y "Refactor this code to use async/await" < oldcode.js
```

### 5. Documentation
```bash
gemini "Generate documentation for these functions" < functions.js
```

### 6. Test Generation
```bash
gemini "Create unit tests for this module" < module.js
```

---

## 🔐 Security & Privacy

### Telemetry
By default, telemetry may be enabled. To disable:

**Via Command Line:**
```bash
gemini --telemetry false
```

**Via Settings File:**
Add to `~/.config/gemini-cli/settings.json`:
```json
{
  "telemetry": {
    "enabled": false
  }
}
```

### Approval Mode
Control what Gemini can do automatically:

```bash
# Prompt for all approvals (safest)
gemini --approval-mode default

# Auto-approve file edits only
gemini --approval-mode auto_edit

# Auto-approve everything (use with caution!)
gemini --approval-mode yolo
```

---

## 🆘 Troubleshooting

### Command Not Found
If `gemini` command is not found after installation:

1. Check global npm bin directory:
   ```bash
   npm config get prefix
   ```

2. Add to PATH in `~/.zshrc`:
   ```bash
   export PATH="$PATH:$(npm config get prefix)/bin"
   source ~/.zshrc
   ```

### API Key Issues
If you see authentication errors:

1. Verify API key is set:
   ```bash
   echo $GEMINI_API_KEY
   ```

2. Get a new key from: https://makersuite.google.com/app/apikey

3. Set it properly:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```

### Connection Issues
If using a proxy:
```bash
gemini --proxy http://user:pass@proxy:port
```

Or set in settings file:
```json
{
  "proxy": "http://user:pass@proxy:port"
}
```

---

## 📱 Integration with TSH ERP

You can use Gemini CLI to help with your TSH ERP development:

```bash
# Analyze code structure
cd /Users/khaleelal-mulla/TSH_ERP_System_Local
gemini "Analyze the architecture of this ERP system"

# Debug issues
gemini -i "Help me fix authentication issues in the React app"

# Generate new features
gemini "Create a new inventory management component with TypeScript"

# Code review
gemini "Review the recent changes in the frontend" < frontend/src/App.tsx
```

---

## 📚 Resources

- **Official Documentation:** https://github.com/google/generative-ai-cli
- **Google AI Studio:** https://makersuite.google.com/
- **API Key:** https://makersuite.google.com/app/apikey
- **Gemini Models:** https://ai.google.dev/models/gemini

---

## ✅ Next Steps

1. **Set up your API key:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

2. **Try it out:**
   ```bash
   gemini "Hello! Can you help me with coding?"
   ```

3. **Explore features:**
   ```bash
   gemini -h  # See all options
   ```

4. **Integrate with your workflow:**
   - Use for code reviews
   - Generate documentation
   - Debug complex issues
   - Refactor code
   - Generate tests

---

**Installation Complete!** 🎉

You're ready to use Gemini CLI for AI-powered coding assistance!

---

**Installed:** October 5, 2025  
**Version:** 0.7.0  
**Command:** `gemini`
