import * as vscode from 'vscode';

export class QuickActionsProvider implements vscode.TreeDataProvider<QuickActionItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<QuickActionItem | undefined | null | void> = new vscode.EventEmitter<QuickActionItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<QuickActionItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private context: vscode.ExtensionContext) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: QuickActionItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: QuickActionItem): Thenable<QuickActionItem[]> {
        if (element) {
            return Promise.resolve([]);
        }

        const actions: QuickActionItem[] = [
            new QuickActionItem(
                'Run Custom Command',
                'Execute any terminal command',
                'claude.runCommand',
                'terminal'
            ),
            new QuickActionItem(
                'Execute Current File',
                'Run the active file in terminal',
                'claude.executeScript',
                'play'
            ),
            new QuickActionItem(
                'Analyze Code',
                'Get Claude AI analysis of current file',
                'claude.analyzeCode',
                'sparkle'
            ),
            new QuickActionItem(
                'Open Claude Terminal',
                'Open dedicated Claude terminal',
                'claude.openTerminal',
                'terminal-bash'
            ),
            new QuickActionItem(
                'Clear History',
                'Clear execution history',
                'claude.clearHistory',
                'trash'
            )
        ];

        return Promise.resolve(actions);
    }
}

class QuickActionItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly commandId: string,
        public readonly icon: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        
        this.tooltip = description;
        this.iconPath = new vscode.ThemeIcon(icon);
        this.command = {
            command: commandId,
            title: label,
            arguments: []
        };
    }
}
