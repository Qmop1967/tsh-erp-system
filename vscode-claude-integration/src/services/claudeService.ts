import * as vscode from 'vscode';
import Anthropic from '@anthropic-ai/sdk';

export class ClaudeService {
    private client: Anthropic | null = null;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.initializeClient();
    }

    private initializeClient() {
        const apiKey = vscode.workspace.getConfiguration('claude').get<string>('apiKey');
        if (apiKey) {
            this.client = new Anthropic({
                apiKey: apiKey
            });
        }
    }

    async analyzeCode(code: string, language: string): Promise<string> {
        if (!this.client) {
            throw new Error('Claude API key not configured');
        }

        const config = vscode.workspace.getConfiguration('claude');
        const model = config.get<string>('model', 'claude-3-5-sonnet-20241022');
        const maxTokens = config.get<number>('maxTokens', 4096);

        const message = await this.client.messages.create({
            model: model,
            max_tokens: maxTokens,
            messages: [{
                role: 'user',
                content: `Analyze this ${language} code and provide insights:\n\n\`\`\`${language}\n${code}\n\`\`\`\n\nProvide:\n1. Code quality assessment\n2. Potential issues or bugs\n3. Performance suggestions\n4. Best practices recommendations\n5. Security considerations`
            }]
        });

        const content = message.content[0];
        if (content.type === 'text') {
            return content.text;
        }
        
        return 'No analysis available';
    }

    async generateCommand(description: string, context?: string): Promise<string> {
        if (!this.client) {
            throw new Error('Claude API key not configured');
        }

        const config = vscode.workspace.getConfiguration('claude');
        const model = config.get<string>('model', 'claude-3-5-sonnet-20241022');

        const prompt = context 
            ? `Given this context:\n${context}\n\nGenerate a shell command to: ${description}\n\nProvide only the command, no explanation.`
            : `Generate a shell command to: ${description}\n\nProvide only the command, no explanation.`;

        const message = await this.client.messages.create({
            model: model,
            max_tokens: 500,
            messages: [{
                role: 'user',
                content: prompt
            }]
        });

        const content = message.content[0];
        if (content.type === 'text') {
            return content.text.trim();
        }
        
        return '';
    }

    async explainError(error: string, code?: string): Promise<string> {
        if (!this.client) {
            throw new Error('Claude API key not configured');
        }

        const config = vscode.workspace.getConfiguration('claude');
        const model = config.get<string>('model', 'claude-3-5-sonnet-20241022');

        let prompt = `Explain this error and suggest how to fix it:\n\n${error}`;
        if (code) {
            prompt += `\n\nRelevant code:\n\`\`\`\n${code}\n\`\`\``;
        }

        const message = await this.client.messages.create({
            model: model,
            max_tokens: 2000,
            messages: [{
                role: 'user',
                content: prompt
            }]
        });

        const content = message.content[0];
        if (content.type === 'text') {
            return content.text;
        }
        
        return 'No explanation available';
    }
}
