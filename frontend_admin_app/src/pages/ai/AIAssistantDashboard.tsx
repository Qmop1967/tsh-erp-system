import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { 
  MessageSquare, 
  Bot, 
  Phone, 
  ShoppingCart, 
  TrendingUp, 
  Users, 
  Clock,
  CheckCircle,
  AlertCircle,
  Globe,
  Headphones,
  Zap,
  BarChart3,
  MessageCircle,
  Settings,
  Send,
  Image,
  FileText,
  Mic
} from 'lucide-react';

interface AIMessage {
  id: string;
  phone_number: string;
  content: string;
  type: 'text' | 'image' | 'audio' | 'document';
  language: 'ar' | 'en';
  direction: 'inbound' | 'outbound';
  intent: string;
  confidence: number;
  timestamp: string;
  customer_name?: string;
}

interface AIConversation {
  id: string;
  customer_phone: string;
  customer_name: string;
  status: 'active' | 'resolved' | 'escalated';
  message_count: number;
  last_activity: string;
  language: 'ar' | 'en';
  intents: string[];
  created_at: string;
}

interface AIAnalytics {
  total_conversations: number;
  total_messages: number;
  ai_generated_orders: number;
  support_tickets: number;
  average_confidence: number;
  escalation_rate: number;
  intent_breakdown: { intent: string; count: number }[];
  language_usage: { language: string; count: number }[];
  platform_usage: { platform: string; count: number }[];
}

const AIAssistantDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [analytics, setAnalytics] = useState<AIAnalytics | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    setRefreshInterval(interval);
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load analytics
      const analyticsResponse = await fetch('/api/ai/analytics/dashboard');
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }
      
      // Load conversations (mock data for now)
      const mockConversations: AIConversation[] = [
        {
          id: '1',
          customer_phone: '+964790123456',
          customer_name: 'أحمد علي',
          status: 'active',
          message_count: 12,
          last_activity: '2024-01-15T10:30:00Z',
          language: 'ar',
          intents: ['product_search', 'price_inquiry'],
          created_at: '2024-01-15T09:00:00Z'
        },
        {
          id: '2',
          customer_phone: '+964791234567',
          customer_name: 'Sara Mohammed',
          status: 'escalated',
          message_count: 8,
          last_activity: '2024-01-15T10:25:00Z',
          language: 'ar',
          intents: ['complaint', 'support'],
          created_at: '2024-01-15T09:15:00Z'
        },
        {
          id: '3',
          customer_phone: '+964792345678',
          customer_name: 'John Smith',
          status: 'resolved',
          message_count: 5,
          last_activity: '2024-01-15T10:20:00Z',
          language: 'en',
          intents: ['order_placement', 'payment_inquiry'],
          created_at: '2024-01-15T09:30:00Z'
        }
      ];
      
      setConversations(mockConversations);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    try {
      setLoading(true);
      
      // Mock messages for the conversation
      const mockMessages: AIMessage[] = [
        {
          id: '1',
          phone_number: '+964790123456',
          content: 'مرحباً، أريد أن أسأل عن أسعار اللابتوب',
          type: 'text',
          language: 'ar',
          direction: 'inbound',
          intent: 'price_inquiry',
          confidence: 0.92,
          timestamp: '2024-01-15T09:00:00Z',
          customer_name: 'أحمد علي'
        },
        {
          id: '2',
          phone_number: '+964790123456',
          content: 'مرحباً بك في TSH! يمكنني مساعدتك في الحصول على أسعار اللابتوب. ما هو نوع اللابتوب الذي تبحث عنه؟',
          type: 'text',
          language: 'ar',
          direction: 'outbound',
          intent: 'product_search',
          confidence: 0.88,
          timestamp: '2024-01-15T09:01:00Z'
        },
        {
          id: '3',
          phone_number: '+964790123456',
          content: 'أبحث عن لابتوب HP للألعاب',
          type: 'text',
          language: 'ar',
          direction: 'inbound',
          intent: 'product_search',
          confidence: 0.95,
          timestamp: '2024-01-15T09:02:00Z',
          customer_name: 'أحمد علي'
        }
      ];
      
      setMessages(mockMessages);
      setSelectedConversation(conversationId);
      
    } catch (error) {
      console.error('Error loading conversation messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    try {
      setLoading(true);
      
      // Add message to UI immediately
      const newMsg: AIMessage = {
        id: Date.now().toString(),
        phone_number: '+964790123456',
        content: newMessage,
        type: 'text',
        language: 'ar',
        direction: 'outbound',
        intent: 'manual_response',
        confidence: 1.0,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, newMsg]);
      setNewMessage('');
      
      // Here you would send the actual message via API
      // await fetch('/api/whatsapp/send/text', { ... });
      
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'escalated': return 'bg-red-100 text-red-800';
      case 'resolved': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getIntentColor = (intent: string) => {
    switch (intent) {
      case 'product_search': return 'bg-purple-100 text-purple-800';
      case 'price_inquiry': return 'bg-yellow-100 text-yellow-800';
      case 'order_placement': return 'bg-green-100 text-green-800';
      case 'complaint': return 'bg-red-100 text-red-800';
      case 'support': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ar-IQ', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: '2-digit'
    });
  };

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">مساعد الذكي AI</h1>
          <p className="text-gray-600">24/7 خدمة العملاء الذكية</p>
        </div>
        <div className="flex items-center space-x-4 space-x-reverse">
          <Badge className="bg-green-100 text-green-800">
            <Bot className="w-4 h-4 mr-2" />
            نشط
          </Badge>
          <Button onClick={loadDashboardData} variant="outline">
            <Zap className="w-4 h-4 mr-2" />
            تحديث
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">المحادثات اليوم</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.total_conversations || 0}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <MessageSquare className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">الرسائل المعالجة</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.total_messages || 0}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <MessageCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">طلبات AI</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.ai_generated_orders || 0}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <ShoppingCart className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">معدل الثقة</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.average_confidence ? 
                    `${(analytics.average_confidence * 100).toFixed(1)}%` : 
                    '0%'
                  }
                </p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <TrendingUp className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">نظرة عامة</TabsTrigger>
          <TabsTrigger value="conversations">المحادثات</TabsTrigger>
          <TabsTrigger value="analytics">التحليلات</TabsTrigger>
          <TabsTrigger value="settings">الإعدادات</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Active Conversations */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  المحادثات النشطة
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {conversations.filter(c => c.status === 'active').map((conversation) => (
                    <div
                      key={conversation.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                      onClick={() => loadConversationMessages(conversation.id)}
                    >
                      <div className="flex items-center space-x-3 space-x-reverse">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <MessageSquare className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">{conversation.customer_name}</p>
                          <p className="text-sm text-gray-600">{conversation.customer_phone}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge className={getStatusColor(conversation.status)}>
                          {conversation.status}
                        </Badge>
                        <p className="text-sm text-gray-600 mt-1">
                          {formatTimestamp(conversation.last_activity)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  إحصائيات سريعة
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">معدل التصعيد</span>
                    <span className="font-medium">
                      {analytics?.escalation_rate ? 
                        `${analytics.escalation_rate.toFixed(1)}%` : 
                        '0%'
                      }
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">اللغة العربية</span>
                    <span className="font-medium">
                      {analytics?.language_usage?.find(l => l.language === 'ar')?.count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">اللغة الإنجليزية</span>
                    <span className="font-medium">
                      {analytics?.language_usage?.find(l => l.language === 'en')?.count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">واتساب</span>
                    <span className="font-medium">
                      {analytics?.platform_usage?.find(p => p.platform === 'whatsapp')?.count || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="conversations" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Conversations List */}
            <Card>
              <CardHeader>
                <CardTitle>قائمة المحادثات</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="max-h-96 overflow-y-auto">
                  {conversations.map((conversation) => (
                    <div
                      key={conversation.id}
                      className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                        selectedConversation === conversation.id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => loadConversationMessages(conversation.id)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-medium">{conversation.customer_name}</p>
                        <Badge className={getStatusColor(conversation.status)}>
                          {conversation.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        {conversation.customer_phone}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex space-x-1 space-x-reverse">
                          {conversation.intents.map((intent) => (
                            <Badge key={intent} variant="outline" className="text-xs">
                              {intent}
                            </Badge>
                          ))}
                        </div>
                        <p className="text-xs text-gray-500">
                          {conversation.message_count} رسالة
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Conversation Messages */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>الرسائل</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedConversation ? (
                  <div className="space-y-4">
                    <div className="max-h-96 overflow-y-auto space-y-3">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${
                            message.direction === 'outbound' ? 'justify-end' : 'justify-start'
                          }`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.direction === 'outbound'
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-100 text-gray-900'
                            }`}
                          >
                            <div className="flex items-center space-x-2 space-x-reverse mb-1">
                              {message.type === 'image' && <Image className="w-4 h-4" />}
                              {message.type === 'audio' && <Mic className="w-4 h-4" />}
                              {message.type === 'document' && <FileText className="w-4 h-4" />}
                              <span className="text-xs opacity-75">
                                {formatTimestamp(message.timestamp)}
                              </span>
                            </div>
                            <p className="text-sm">{message.content}</p>
                            <div className="flex items-center justify-between mt-2 text-xs opacity-75">
                              <Badge variant="outline" className={getIntentColor(message.intent)}>
                                {message.intent}
                              </Badge>
                              <span>{(message.confidence * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {/* Send Message */}
                    <div className="flex space-x-2 space-x-reverse">
                      <Input
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="اكتب رسالتك..."
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      />
                      <Button onClick={sendMessage} disabled={loading}>
                        <Send className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MessageSquare className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">اختر محادثة لعرض الرسائل</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Intent Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>تحليل النوايا</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics?.intent_breakdown?.map((item) => (
                    <div key={item.intent} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 space-x-reverse">
                        <Badge className={getIntentColor(item.intent)}>
                          {item.intent}
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-2 space-x-reverse">
                        <span className="text-sm text-gray-600">{item.count}</span>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ 
                              width: `${(item.count / Math.max(...(analytics?.intent_breakdown?.map(i => i.count) || [1]))) * 100}%` 
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>مقاييس الأداء</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">إجمالي المحادثات</span>
                    <span className="font-medium">{analytics?.total_conversations || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">إجمالي الرسائل</span>
                    <span className="font-medium">{analytics?.total_messages || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">طلبات AI</span>
                    <span className="font-medium">{analytics?.ai_generated_orders || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">تذاكر الدعم</span>
                    <span className="font-medium">{analytics?.support_tickets || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">معدل الثقة</span>
                    <span className="font-medium">
                      {analytics?.average_confidence ? 
                        `${(analytics.average_confidence * 100).toFixed(1)}%` : 
                        '0%'
                      }
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">معدل التصعيد</span>
                    <span className="font-medium">
                      {analytics?.escalation_rate ? 
                        `${analytics.escalation_rate.toFixed(1)}%` : 
                        '0%'
                      }
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                إعدادات المساعد الذكي
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h4 className="font-medium mb-3">الاستجابة التلقائية</h4>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>تفعيل الاستجابة التلقائية</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>استجابة فورية للتحية</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span>تصعيد تلقائي للشكاوى</span>
                    </label>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-3">إعدادات اللغة</h4>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>اللغة العربية</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>اللغة الإنجليزية</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span>الكردية</span>
                    </label>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-3">معايير الثقة</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span>الحد الأدنى للثقة</span>
                      <span className="font-medium">85%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>تصعيد عند الثقة أقل من</span>
                      <span className="font-medium">70%</span>
                    </div>
                  </div>
                </div>

                <Button className="w-full">
                  <Settings className="w-4 h-4 mr-2" />
                  حفظ الإعدادات
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AIAssistantDashboard; 