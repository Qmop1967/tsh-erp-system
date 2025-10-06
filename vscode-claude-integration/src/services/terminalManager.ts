import * as vscode from 'vscode';

export interface CommandExecution {
    command: string;
    timestamp: Date;
    exitCode?: number;
    output?: string;
}

export class TerminalManager {
    private terminal: vscode.Terminal | null = null;
    private context: vscode.ExtensionContext;
    private executionHistory: CommandExecution[] = [];

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        
        // Clean up terminal when it's closed
        vscode.window.onDidCloseTerminal((closedTerminal) => {
            if (closedTerminal === this.terminal) {
                this.terminal = null;
            }
        });
    }

    getOrCreateTerminal(): vscode.Terminal {
        if (!this.terminal || this.terminal.exitStatus !== undefined) {
            this.terminal = vscode.window.createTerminal({
                name: 'Claude Terminal',
                iconPath: new vscode.ThemeIcon('robot')
            });
        }
        return this.terminal;
    }

    async executeCommand(command: string): Promise<void> {
        const terminal = this.getOrCreateTerminal();
        const config = vscode.workspace.getConfiguration('claude');
        const autoShow = config.get<boolean>('autoShow', true);

        if (autoShow) {
            terminal.show();
        }

        // Record execution
        const execution: CommandExecution = {
            command,
            timestamp: new Date()
        };
        this.executionHistory.push(execution);

        // Execute command
        if (terminal.shellIntegration) {
            try {
                const shellExecution = terminal.shellIntegration.executeCommand(command);
                
                // Wait for command to complete
                const exitCode = await shellExecution.exitCode;
                execution.exitCode = exitCode;
                
                vscode.window.showInformationMessage(
                    `Command completed with exit code: ${exitCode}`
                );
            } catch (error) {
                vscode.window.showErrorMessage(`Command execution failed: ${error}`);
                throw error;
            }
        } else {
            // Fallback for terminals without shell integration
            terminal.sendText(command);
            vscode.window.showWarningMessage(
                'Shell integration not available. Command sent but exit status unknown.'
            );
        }

        // Save to context for persistence
        await this.context.workspaceState.update('executionHistory', 
            this.executionHistory.slice(-50) // Keep last 50 executions
        );
    }

    async executeCommandSilent(command: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const terminal = this.getOrCreateTerminal();
            
            if (!terminal.shellIntegration) {
                reject(new Error('Shell integration required for silent execution'));
                return;
            }

            const execution = terminal.shellIntegration.executeCommand(command);
            let output = '';

            // Note: This is a simplified version. Full implementation would need
            // proper output capture which requires more complex terminal handling
            execution.exitCode.then((code) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`Command failed with exit code ${code}`));
                }
            }).catch(reject);
        });
    }

    getExecutionHistory(): CommandExecution[] {
        return [...this.executionHistory];
    }

    clearHistory(): void {
        this.executionHistory = [];
        this.context.workspaceState.update('executionHistory', []);
    }

    dispose(): void {
        if (this.terminal) {
            this.terminal.dispose();
        }
    }
}
