import * as vscode from 'vscode';
import { ClaudeService } from './services/claudeService';
import { TerminalManager } from './services/terminalManager';
import { ExecutionHistoryProvider } from './providers/executionHistoryProvider';
import { QuickActionsProvider } from './providers/quickActionsProvider';

let claudeService: ClaudeService;
let terminalManager: TerminalManager;

export function activate(context: vscode.ExtensionContext) {
    console.log('Claude Code Runner extension is now active!');

    // Initialize services
    claudeService = new ClaudeService(context);
    terminalManager = new TerminalManager(context);

    // Register providers
    const executionHistoryProvider = new ExecutionHistoryProvider(context);
    const quickActionsProvider = new QuickActionsProvider(context);

    vscode.window.registerTreeDataProvider('claude.executionHistory', executionHistoryProvider);
    vscode.window.registerTreeDataProvider('claude.quickActions', quickActionsProvider);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('claude.runCommand', async () => {
            await runCommand();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claude.openTerminal', () => {
            terminalManager.getOrCreateTerminal().show();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claude.executeScript', async () => {
            await executeScript();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claude.analyzeCode', async () => {
            await analyzeCode();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claude.clearHistory', () => {
            executionHistoryProvider.clear();
            vscode.window.showInformationMessage('Execution history cleared!');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claude.runHistoryItem', async (command: string) => {
            await executeCommandInTerminal(command);
        })
    );

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(robot) Claude";
    statusBarItem.tooltip = "Click to run a command with Claude";
    statusBarItem.command = 'claude.runCommand';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Show welcome message
    vscode.window.showInformationMessage(
        'Claude Code Runner is ready! Press Cmd+Shift+C (Mac) or Ctrl+Shift+C (Windows/Linux) to run commands.',
        'Open Settings'
    ).then(selection => {
        if (selection === 'Open Settings') {
            vscode.commands.executeCommand('workbench.action.openSettings', 'claude');
        }
    });
}

async function runCommand() {
    const command = await vscode.window.showInputBox({
        prompt: 'Enter command to execute',
        placeHolder: 'e.g., npm install, python script.py, etc.',
        validateInput: (value) => {
            return value.trim().length === 0 ? 'Command cannot be empty' : null;
        }
    });

    if (command) {
        await executeCommandInTerminal(command);
    }
}

async function executeCommandInTerminal(command: string) {
    const config = vscode.workspace.getConfiguration('claude');
    const confirmBeforeRun = config.get<boolean>('confirmBeforeRun', true);

    if (confirmBeforeRun) {
        const confirm = await vscode.window.showWarningMessage(
            `Execute command: ${command}?`,
            { modal: true },
            'Execute',
            'Cancel'
        );

        if (confirm !== 'Execute') {
            return;
        }
    }

    try {
        await terminalManager.executeCommand(command);
        vscode.window.showInformationMessage(`✓ Executed: ${command}`);
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to execute command: ${error}`);
    }
}

async function executeScript() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found!');
        return;
    }

    const document = editor.document;
    const selection = editor.selection;
    const text = selection.isEmpty ? document.getText() : document.getText(selection);

    if (!text.trim()) {
        vscode.window.showErrorMessage('No code to execute!');
        return;
    }

    // Detect language and create appropriate command
    const languageId = document.languageId;
    let command = '';

    switch (languageId) {
        case 'python':
            // Save to temp file and run
            const pythonFile = document.fileName;
            command = `python "${pythonFile}"`;
            break;
        case 'javascript':
        case 'typescript':
            const jsFile = document.fileName;
            command = `node "${jsFile}"`;
            break;
        case 'shellscript':
        case 'bash':
            const shellFile = document.fileName;
            command = `bash "${shellFile}"`;
            break;
        default:
            vscode.window.showErrorMessage(`Language ${languageId} is not supported for direct execution`);
            return;
    }

    // Save the file first
    await document.save();
    await executeCommandInTerminal(command);
}

async function analyzeCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found!');
        return;
    }

    const apiKey = vscode.workspace.getConfiguration('claude').get<string>('apiKey');
    if (!apiKey) {
        const configure = await vscode.window.showErrorMessage(
            'Claude API key not configured',
            'Configure'
        );
        if (configure === 'Configure') {
            vscode.commands.executeCommand('workbench.action.openSettings', 'claude.apiKey');
        }
        return;
    }

    const document = editor.document;
    const text = document.getText();

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "Analyzing code with Claude...",
        cancellable: false
    }, async () => {
        try {
            const analysis = await claudeService.analyzeCode(text, document.languageId);
            
            // Create a new document with the analysis
            const doc = await vscode.workspace.openTextDocument({
                content: analysis,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to analyze code: ${error}`);
        }
    });
}

export function deactivate() {
    console.log('Claude Code Runner extension is now deactivated');
}
