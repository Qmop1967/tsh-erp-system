import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Minimize2, Maximize2, Sparkles, Loader2, Bot, User, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatGPTModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatGPTModal: React.FC<ChatGPTModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const [contextType, setContextType] = useState<'general' | 'sales' | 'inventory' | 'financial'>('general');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const language = localStorage.getItem('language') || 'en';
  const isArabic = language === 'ar';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

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
        throw new Error('Not authenticated. Please login first.');
      }

      const response = await fetch('http://localhost:8000/api/chatgpt/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputMessage,
          context_type: contextType,
          conversation_id: conversationId || undefined,
          include_user_context: true,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.message,
          timestamp: data.timestamp,
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setConversationId(data.conversation_id);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      
      let errorContent = '';
      if (error.message === 'Not authenticated. Please login first.') {
        errorContent = isArabic
          ? '⚠️ يجب تسجيل الدخول أولاً لاستخدام مساعد ChatGPT.'
          : '⚠️ Please login first to use the ChatGPT assistant.';
      } else {
        errorContent = isArabic
          ? 'عذراً، حدث خطأ في الاتصال. يرجى التحقق من إعدادات ChatGPT.'
          : 'Sorry, there was an error. Please check your ChatGPT settings.';
      }
      
      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId('');
  };

  const goToSettings = () => {
    navigate('/settings/integrations/chatgpt');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      onClick={onClose}
    >
      <div
        className={`bg-white rounded-2xl shadow-2xl transition-all duration-300 ${
          isMinimized ? 'w-96 h-16' : 'w-full max-w-4xl h-[600px]'
        } m-4`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-full">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">
                {isArabic ? 'مساعد الذكاء الاصطناعي' : 'AI Assistant'}
              </h3>
              <p className="text-xs text-blue-100">
                {isArabic ? 'مدعوم بـ ChatGPT' : 'Powered by ChatGPT'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Context Selector */}
            {!isMinimized && (
              <select
                value={contextType}
                onChange={(e) => setContextType(e.target.value as any)}
                className="text-sm px-3 py-1 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
              >
                <option value="general" className="text-gray-800">General</option>
                <option value="sales" className="text-gray-800">Sales</option>
                <option value="inventory" className="text-gray-800">Inventory</option>
                <option value="financial" className="text-gray-800">Financial</option>
              </select>
            )}
            
            <button
              onClick={goToSettings}
              className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
            
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="hover:bg-white/20 p-2 rounded-lg transition-colors"
            >
              {isMinimized ? <Maximize2 className="w-5 h-5" /> : <Minimize2 className="w-5 h-5" />}
            </button>
            
            <button
              onClick={onClose}
              className="hover:bg-white/20 p-2 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50 h-[calc(600px-180px)]">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-20">
                  <Bot className="w-16 h-16 mx-auto mb-4 text-blue-500" />
                  <p className="text-lg font-semibold">
                    {isArabic
                      ? 'مرحباً! كيف يمكنني مساعدتك اليوم؟'
                      : 'Hello! How can I help you today?'}
                  </p>
                  <p className="text-sm mt-2">
                    {isArabic
                      ? 'اسألني عن المبيعات، المخزون، التقارير المالية، وأكثر'
                      : 'Ask me about sales, inventory, financial reports, and more'}
                  </p>
                  
                  {/* Quick Actions */}
                  <div className="mt-6 grid grid-cols-2 gap-3 max-w-md mx-auto">
                    <button
                      onClick={() => setInputMessage("What are today's sales?")}
                      className="p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all text-left border border-gray-200"
                    >
                      <p className="text-sm font-medium text-gray-700">📊 Today's Sales</p>
                      <p className="text-xs text-gray-500">View sales summary</p>
                    </button>
                    <button
                      onClick={() => setInputMessage('Show low stock items')}
                      className="p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all text-left border border-gray-200"
                    >
                      <p className="text-sm font-medium text-gray-700">📦 Low Stock</p>
                      <p className="text-xs text-gray-500">Check inventory</p>
                    </button>
                    <button
                      onClick={() => setInputMessage('Generate monthly report')}
                      className="p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all text-left border border-gray-200"
                    >
                      <p className="text-sm font-medium text-gray-700">📈 Monthly Report</p>
                      <p className="text-xs text-gray-500">Financial summary</p>
                    </button>
                    <button
                      onClick={() => setInputMessage('Top customers this month')}
                      className="p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all text-left border border-gray-200"
                    >
                      <p className="text-sm font-medium text-gray-700">👥 Top Customers</p>
                      <p className="text-xs text-gray-500">Customer insights</p>
                    </button>
                  </div>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="bg-blue-600 text-white p-2 rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}
                  <div
                    className={`max-w-[75%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-800 shadow-md border border-gray-200'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p
                      className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  {message.role === 'user' && (
                    <div className="bg-gray-600 text-white p-2 rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="bg-blue-600 text-white p-2 rounded-full h-8 w-8 flex items-center justify-center">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-md border border-gray-200">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4 bg-white rounded-b-2xl">
              {messages.length > 0 && (
                <button
                  onClick={clearConversation}
                  className="text-xs text-gray-500 hover:text-gray-700 mb-2 transition-colors"
                >
                  {isArabic ? 'مسح المحادثة' : 'Clear conversation'}
                </button>
              )}
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    isArabic
                      ? 'اكتب رسالتك هنا...'
                      : 'Type your message here...'
                  }
                  className={`flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isArabic ? 'text-right' : 'text-left'
                  }`}
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center gap-2"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span className="font-medium">Send</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ChatGPTModal;
