import * as vscode from 'vscode';
import { CommandExecution } from '../services/terminalManager';

export class ExecutionHistoryProvider implements vscode.TreeDataProvider<ExecutionHistoryItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ExecutionHistoryItem | undefined | null | void> = new vscode.EventEmitter<ExecutionHistoryItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ExecutionHistoryItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private history: CommandExecution[] = [];
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.loadHistory();
    }

    private loadHistory() {
        const saved = this.context.workspaceState.get<CommandExecution[]>('executionHistory', []);
        this.history = saved;
    }

    refresh(): void {
        this.loadHistory();
        this._onDidChangeTreeData.fire();
    }

    clear(): void {
        this.history = [];
        this.context.workspaceState.update('executionHistory', []);
        this.refresh();
    }

    addExecution(execution: CommandExecution): void {
        this.history.unshift(execution);
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
        this.context.workspaceState.update('executionHistory', this.history);
        this.refresh();
    }

    getTreeItem(element: ExecutionHistoryItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ExecutionHistoryItem): Thenable<ExecutionHistoryItem[]> {
        if (element) {
            return Promise.resolve([]);
        }

        if (this.history.length === 0) {
            return Promise.resolve([]);
        }

        return Promise.resolve(
            this.history.map((exec, index) => new ExecutionHistoryItem(
                exec.command,
                exec.timestamp,
                exec.exitCode,
                index
            ))
        );
    }
}

class ExecutionHistoryItem extends vscode.TreeItem {
    constructor(
        public readonly command: string,
        public readonly timestamp: Date,
        public readonly exitCode: number | undefined,
        public readonly index: number
    ) {
        super(command, vscode.TreeItemCollapsibleState.None);

        const timeStr = timestamp.toLocaleTimeString();
        const dateStr = timestamp.toLocaleDateString();
        
        this.tooltip = `${command}\nExecuted: ${dateStr} ${timeStr}${exitCode !== undefined ? `\nExit Code: ${exitCode}` : ''}`;
        this.description = timeStr;
        
        if (exitCode === 0) {
            this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
        } else if (exitCode !== undefined) {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
        } else {
            this.iconPath = new vscode.ThemeIcon('terminal');
        }

        this.contextValue = 'executionHistoryItem';
        this.command = {
            command: 'claude.runHistoryItem',
            title: 'Run Command',
            arguments: [command]
        };
    }
}
