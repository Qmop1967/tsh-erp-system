/**
 * Test Anthropic Claude SDK Installation (TypeScript/Node.js)
 */

import Anthropic from '@anthropic-ai/sdk';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

async function testClaudeConnection() {
    console.log('🔧 Testing Anthropic Claude SDK Setup (Node.js)...');
    console.log('='.repeat(70));
    
    // Get API key from environment
    const apiKey = process.env.ANTHROPIC_API_KEY;
    
    if (!apiKey) {
        console.log('❌ ERROR: ANTHROPIC_API_KEY not found in environment');
        console.log('   Please check your .env file');
        return false;
    }
    
    console.log(`✅ API Key found: ${apiKey.substring(0, 20)}...`);
    
    try {
        // Initialize client
        const client = new Anthropic({ apiKey });
        console.log('✅ Anthropic client initialized');
        
        // Test a simple message
        console.log('\n📤 Sending test message to Claude...');
        const message = await client.messages.create({
            model: 'claude-3-5-sonnet-20241022',
            max_tokens: 100,
            messages: [
                {
                    role: 'user',
                    content: "Say 'Hello from TSH ERP System!' in one sentence."
                }
            ]
        });
        
        console.log('✅ Message sent successfully!');
        console.log('\n📩 Claude\'s Response:');
        const textContent = message.content[0];
        if (textContent.type === 'text') {
            console.log(`   ${textContent.text}`);
        }
        console.log();
        console.log('='.repeat(70));
        console.log('🎉 Anthropic Claude SDK is working correctly!');
        return true;
        
    } catch (error) {
        console.log(`\n❌ ERROR: ${error.message}`);
        console.log('\n💡 Possible issues:');
        console.log('   1. Invalid API key');
        console.log('   2. Network connection problem');
        console.log('   3. API rate limit exceeded');
        return false;
    }
}

testClaudeConnection();
