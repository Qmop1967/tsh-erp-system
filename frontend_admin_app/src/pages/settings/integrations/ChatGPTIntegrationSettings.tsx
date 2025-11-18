import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Key, 
  Settings as SettingsIcon, 
  Save, 
  TestTube, 
  CheckCircle2, 
  XCircle, 
  Loader2,
  MessageSquare,
  Sparkles,
  TrendingUp,
  DollarSign,
  Clock,
  Activity
} from 'lucide-react';

interface ChatGPTConfig {
  enabled: boolean;
  api_key: string;
  model: string;
  max_tokens: number;
  temperature: number;
  max_history: number;
  include_user_context: boolean;
  include_company_context: boolean;
}

interface ChatGPTStats {
  total_conversations: number;
  total_messages: number;
  avg_response_time: number;
  total_tokens_used: number;
  estimated_cost: number;
}

const ChatGPTIntegrationSettings: React.FC = () => {
  const [config, setConfig] = useState<ChatGPTConfig>({
    enabled: true,
    api_key: '',
    model: 'gpt-4o',
    max_tokens: 2000,
    temperature: 0.7,
    max_history: 10,
    include_user_context: true,
    include_company_context: true,
  });

  const [stats, setStats] = useState<ChatGPTStats>({
    total_conversations: 0,
    total_messages: 0,
    avg_response_time: 0,
    total_tokens_used: 0,
    estimated_cost: 0,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    loadConfiguration();
    loadStats();
  }, []);

  const loadConfiguration = async () => {
    try {
      // Load configuration from backend or localStorage
      const savedConfig = localStorage.getItem('chatgpt_config');
      if (savedConfig) {
        setConfig(JSON.parse(savedConfig));
      }
    } catch (error) {
      console.error('Error loading configuration:', error);
    }
  };

  const loadStats = async () => {
    // Mock stats - in production, fetch from backend
    setStats({
      total_conversations: 156,
      total_messages: 892,
      avg_response_time: 1.8,
      total_tokens_used: 45230,
      estimated_cost: 0.68,
    });
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Save to localStorage (in production, save to backend)
      localStorage.setItem('chatgpt_config', JSON.stringify(config));
      
      // In production, you would call:
      // await fetch('/api/settings/chatgpt', {
      //   method: 'POST',
      //   body: JSON.stringify(config)
      // });
      
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (error) {
      console.error('Error saving configuration:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);

    try {
      // Get token from auth store
      let token = null;
      const authData = localStorage.getItem('tsh-erp-auth');
      if (authData) {
        try {
          const { state } = JSON.parse(authData);
          token = state?.token;
        } catch (e) {
          console.error('Error parsing auth data:', e);
        }
      }

      if (!token) {
        setTestResult({
          success: false,
          message: '❌ Not authenticated. Please login first.',
        });
        setIsTesting(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/chatgpt/health', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTestResult({
          success: true,
          message: `✅ Connected successfully! Model: ${data.model}`,
        });
      } else {
        setTestResult({
          success: false,
          message: '❌ Connection failed. Please check your API key.',
        });
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: '❌ Error connecting to ChatGPT service.',
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                ChatGPT Integration
              </h1>
              <p className="text-blue-100 text-lg">
                AI-Powered Assistant with OpenAI GPT-4o
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm mb-1">Conversations</p>
                <p className="text-2xl font-bold text-gray-800">{stats.total_conversations}</p>
              </div>
              <MessageSquare className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm mb-1">Messages</p>
                <p className="text-2xl font-bold text-gray-800">{stats.total_messages}</p>
              </div>
              <Activity className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm mb-1">Avg Response</p>
                <p className="text-2xl font-bold text-gray-800">{stats.avg_response_time}s</p>
              </div>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm mb-1">Tokens Used</p>
                <p className="text-2xl font-bold text-gray-800">{stats.total_tokens_used.toLocaleString()}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm mb-1">Est. Cost</p>
                <p className="text-2xl font-bold text-gray-800">${stats.estimated_cost}</p>
              </div>
              <DollarSign className="w-8 h-8 text-red-500" />
            </div>
          </div>
        </div>

        {/* Configuration Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <SettingsIcon className="w-6 h-6 text-gray-700" />
            <h2 className="text-2xl font-bold text-gray-800">Configuration</h2>
          </div>

          <div className="space-y-6">
            {/* Enable/Disable */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="text-lg font-semibold text-gray-700">Enable ChatGPT</label>
                <p className="text-sm text-gray-500">Activate AI assistant across the system</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.enabled}
                  onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* API Key */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <Key className="w-4 h-4 inline mr-2" />
                OpenAI API Key
              </label>
              <input
                type="password"
                value={config.api_key}
                onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                placeholder="sk-..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenAI Platform</a>
              </p>
            </div>

            {/* Model Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <Bot className="w-4 h-4 inline mr-2" />
                Model
              </label>
              <select
                value={config.model}
                onChange={(e) => setConfig({ ...config, model: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="gpt-4o">GPT-4o (Recommended)</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Faster, Cheaper)</option>
              </select>
            </div>

            {/* Advanced Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  value={config.max_tokens}
                  onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                  min="100"
                  max="4000"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Temperature (0-1)
                </label>
                <input
                  type="number"
                  value={config.temperature}
                  onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                  min="0"
                  max="1"
                  step="0.1"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Max History Messages
                </label>
                <input
                  type="number"
                  value={config.max_history}
                  onChange={(e) => setConfig({ ...config, max_history: parseInt(e.target.value) })}
                  min="1"
                  max="50"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Context Options */}
            <div className="space-y-3">
              <label className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                <input
                  type="checkbox"
                  checked={config.include_user_context}
                  onChange={(e) => setConfig({ ...config, include_user_context: e.target.checked })}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div>
                  <span className="font-semibold text-gray-700">Include User Context</span>
                  <p className="text-sm text-gray-500">Provide user information to personalize responses</p>
                </div>
              </label>

              <label className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                <input
                  type="checkbox"
                  checked={config.include_company_context}
                  onChange={(e) => setConfig({ ...config, include_company_context: e.target.checked })}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div>
                  <span className="font-semibold text-gray-700">Include Company Context</span>
                  <p className="text-sm text-gray-500">Provide company information for better context</p>
                </div>
              </label>
            </div>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`mt-6 p-4 rounded-lg ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-center gap-3">
                {testResult.success ? (
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-600" />
                )}
                <p className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                  {testResult.message}
                </p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 mt-8">
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : isSaved ? (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  Saved!
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Configuration
                </>
              )}
            </button>

            <button
              onClick={handleTest}
              disabled={isTesting}
              className="bg-white text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-100 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 border border-gray-300"
            >
              {isTesting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <TestTube className="w-5 h-5" />
                  Test Connection
                </>
              )}
            </button>
          </div>
        </div>

        {/* Documentation */}
        <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">📚 Documentation</h3>
          <ul className="space-y-2 text-blue-800">
            <li>• <strong>API Documentation:</strong> <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="underline">http://localhost:8000/docs</a></li>
            <li>• <strong>Integration Guide:</strong> See CHATGPT_INTEGRATION_GUIDE.md</li>
            <li>• <strong>Available Endpoints:</strong> /api/chatgpt/chat, /translate, /email, /report/summary</li>
            <li>• <strong>Cost Monitoring:</strong> Track usage in OpenAI dashboard</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ChatGPTIntegrationSettings;
