import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Settings,
  Plug,
  Shield,
  Users,
  KeyRound,
  ScrollText,
  Layers,
  Globe,
  Building,
  Languages,
  BookOpen,
  Smartphone,
  Fingerprint,
  Activity,
  FileText,
  Eye,
  Scale,
  UserCog,
  ShieldCheck,
  ListTree,
  GitBranch,
  Calculator,
  ChevronRight,
  Zap,
  Database,
  MessageSquare,
  Sparkles,
  HelpCircle,
} from 'lucide-react';

interface SettingCard {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  items: {
    name: string;
    description: string;
    icon: React.ComponentType<{ className?: string }>;
    path: string;
    enabled: boolean;
  }[];
}

const ModernSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const settingsModules: SettingCard[] = [
    {
      id: 'integrations',
      title: 'Integrations',
      description: 'Connect with external services and APIs',
      icon: Plug,
      color: 'text-blue-600',
      bgColor: 'bg-gradient-to-br from-blue-50 to-blue-100',
      items: [
        {
          name: 'ChatGPT AI Assistant',
          description: 'Configure OpenAI ChatGPT integration for intelligent assistance',
          icon: Sparkles,
          path: '/settings/integrations/chatgpt',
          enabled: true,
        },
        {
          name: 'WhatsApp Business API',
          description: 'Configure WhatsApp Business integration for customer communication',
          icon: MessageSquare,
          path: '/settings/integrations/whatsapp',
          enabled: true,
        },
        {
          name: 'Zoho Integration',
          description: 'Sync data with Zoho CRM, Books, and Inventory',
          icon: Database,
          path: '/settings/integrations/zoho',
          enabled: true,
        },
        {
          name: 'API Configuration',
          description: 'Manage API keys and webhook endpoints',
          icon: Zap,
          path: '/settings/integrations/api',
          enabled: true,
        },
      ],
    },
    {
      id: 'authentication',
      title: 'Authentication & Security',
      description: 'Manage authentication methods and security settings',
      icon: Shield,
      color: 'text-purple-600',
      bgColor: 'bg-gradient-to-br from-purple-50 to-purple-100',
      items: [
        {
          name: 'Devices Management',
          description: 'View and manage authorized devices',
          icon: Smartphone,
          path: '/settings/auth/devices',
          enabled: true,
        },
        {
          name: 'Multi-Factor Authentication',
          description: 'Configure 2FA and MFA settings',
          icon: Fingerprint,
          path: '/settings/auth/mfa',
          enabled: true,
        },
        {
          name: 'Active Sessions',
          description: 'Monitor and manage active user sessions',
          icon: Activity,
          path: '/settings/auth/sessions',
          enabled: true,
        },
        {
          name: 'User Tracking',
          description: 'Track user activities and login history',
          icon: Eye,
          path: '/settings/auth/tracking',
          enabled: true,
        },
        {
          name: 'Audit Logging',
          description: 'View system audit logs and security events',
          icon: FileText,
          path: '/settings/auth/audit',
          enabled: true,
        },
        {
          name: 'Governance',
          description: 'Define security policies and compliance rules',
          icon: Scale,
          path: '/settings/auth/governance',
          enabled: true,
        },
      ],
    },
    {
      id: 'rbac',
      title: 'RBAC & Record Security',
      description: 'Role-Based Access Control and Record-Level Security',
      icon: ShieldCheck,
      color: 'text-emerald-600',
      bgColor: 'bg-gradient-to-br from-emerald-50 to-emerald-100',
      items: [
        {
          name: 'Users',
          description: 'Manage system users and their accounts',
          icon: Users,
          path: '/users',
          enabled: true,
        },
        {
          name: 'Roles',
          description: 'Create and configure user roles',
          icon: UserCog,
          path: '/roles',
          enabled: true,
        },
        {
          name: 'Permissions',
          description: 'Define granular permissions and access rights',
          icon: KeyRound,
          path: '/permissions',
          enabled: true,
        },
        {
          name: 'Record Rules',
          description: 'Set up record-level security rules (RSL)',
          icon: ScrollText,
          path: '/settings/rbac/record-rules',
          enabled: true,
        },
        {
          name: 'Rule Groups',
          description: 'Organize and manage groups of security rules',
          icon: ListTree,
          path: '/settings/rbac/rule-groups',
          enabled: true,
        },
      ],
    },
    {
      id: 'general',
      title: 'General Settings',
      description: 'Company information and system preferences',
      icon: Settings,
      color: 'text-orange-600',
      bgColor: 'bg-gradient-to-br from-orange-50 to-orange-100',
      items: [
        {
          name: 'Organization Profile',
          description: 'Company details, logo, and contact information',
          icon: Building,
          path: '/settings/general/organization',
          enabled: true,
        },
        {
          name: 'Translation Subsystem',
          description: 'Manage multi-language translations and localization',
          icon: Languages,
          path: '/settings/translations',
          enabled: true,
        },
        {
          name: 'System Preferences',
          description: 'Configure date formats, timezone, and defaults',
          icon: Globe,
          path: '/settings/general/preferences',
          enabled: true,
        },
      ],
    },
    {
      id: 'accounting',
      title: 'Accounting & Finance',
      description: 'Financial configuration and accounting settings',
      icon: Calculator,
      color: 'text-indigo-600',
      bgColor: 'bg-gradient-to-br from-indigo-50 to-indigo-100',
      items: [
        {
          name: 'Journals',
          description: 'Configure accounting journals and posting rules',
          icon: BookOpen,
          path: '/accounting/journal-entries',
          enabled: true,
        },
        {
          name: 'Chart of Accounts',
          description: 'Manage account structure and categories',
          icon: Layers,
          path: '/accounting/chart-of-accounts',
          enabled: true,
        },
        {
          name: 'Fiscal Periods',
          description: 'Define fiscal years and accounting periods',
          icon: GitBranch,
          path: '/settings/accounting/periods',
          enabled: true,
        },
      ],
    },
    {
      id: 'documentation',
      title: 'Documentation Center',
      description: 'API references, user guides, and troubleshooting resources',
      icon: BookOpen,
      color: 'text-green-600',
      bgColor: 'bg-gradient-to-br from-green-50 to-green-100',
      items: [
        {
          name: 'API Documentation',
          description: 'Complete API reference with examples and responses',
          icon: Database,
          path: '/settings/documentation',
          enabled: true,
        },
        {
          name: 'User Guides',
          description: 'Step-by-step guides and tutorials for system features',
          icon: BookOpen,
          path: '/settings/documentation#user-guides',
          enabled: true,
        },
        {
          name: 'Troubleshooting',
          description: 'Common issues, solutions, and FAQ',
          icon: HelpCircle,
          path: '/settings/documentation#troubleshooting',
          enabled: true,
        },
        {
          name: 'Integration Guides',
          description: 'Third-party integration documentation and examples',
          icon: Plug,
          path: '/settings/documentation#integrations',
          enabled: true,
        },
      ],
    },
    {
      id: 'system',
      title: 'System & Maintenance',
      description: 'Backup, restore, and system health monitoring',
      icon: HardDrive,
      color: 'text-red-600',
      bgColor: 'bg-gradient-to-br from-red-50 to-red-100',
      items: [
        {
          name: 'Backup & Restore',
          description: 'Automated backups for database, images, and configuration',
          icon: Shield,
          path: '/settings/system/backup-restore',
          enabled: true,
        },
        {
          name: 'System Health',
          description: 'Monitor system performance and resource usage',
          icon: Activity,
          path: '/settings/system/health',
          enabled: false,
        },
        {
          name: 'Database Management',
          description: 'Database optimization and maintenance tools',
          icon: Database,
          path: '/settings/system/database',
          enabled: false,
        },
      ],
    },
  ];

  const handleCardClick = (path: string) => {
    navigate(path);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
            <Settings className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
              System Settings
            </h1>
            <p className="text-gray-600 mt-1">
              Configure and manage your ERP system settings
            </p>
          </div>
        </div>
      </div>

      {/* Settings Cards Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        {settingsModules.map((module) => (
          <div
            key={module.id}
            className={`${module.bgColor} rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden ${
              hoveredCard === module.id ? 'scale-[1.02]' : 'scale-100'
            }`}
            onMouseEnter={() => setHoveredCard(module.id)}
            onMouseLeave={() => setHoveredCard(null)}
          >
            {/* Module Header */}
            <div className="p-6 border-b border-white/50">
              <div className="flex items-start gap-4">
                <div className={`p-4 bg-white rounded-xl shadow-md ${module.color}`}>
                  <module.icon className="w-8 h-8" />
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-800 mb-1">
                    {module.title}
                  </h2>
                  <p className="text-gray-600 text-sm">
                    {module.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Module Items */}
            <div className="p-4">
              <div className="space-y-2">
                {module.items.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => item.enabled && handleCardClick(item.path)}
                    disabled={!item.enabled}
                    className={`w-full group relative overflow-hidden ${
                      item.enabled
                        ? 'cursor-pointer hover:bg-white/70'
                        : 'cursor-not-allowed opacity-50'
                    } bg-white/40 backdrop-blur-sm rounded-xl p-4 transition-all duration-200 ${
                      hoveredItem === `${module.id}-${index}`
                        ? 'shadow-md scale-[1.02]'
                        : 'shadow-sm'
                    }`}
                    onMouseEnter={() => setHoveredItem(`${module.id}-${index}`)}
                    onMouseLeave={() => setHoveredItem(null)}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`p-2 rounded-lg ${
                          item.enabled ? module.color : 'text-gray-400'
                        } bg-white shadow-sm group-hover:shadow-md transition-shadow`}
                      >
                        <item.icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 text-left">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-gray-800 group-hover:text-gray-900">
                            {item.name}
                          </h3>
                          {item.enabled && (
                            <ChevronRight
                              className={`w-5 h-5 text-gray-400 transition-transform ${
                                hoveredItem === `${module.id}-${index}`
                                  ? 'translate-x-1'
                                  : 'translate-x-0'
                              }`}
                            />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {item.description}
                        </p>
                        {!item.enabled && (
                          <span className="inline-block mt-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded">
                            Coming Soon
                          </span>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions Footer */}
      <div className="max-w-7xl mx-auto mt-8 p-6 bg-white rounded-2xl shadow-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate('/settings/backup')}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
          >
            <Database className="w-4 h-4" />
            Backup & Restore
          </button>
          <button
            onClick={() => navigate('/settings/system-logs')}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-2"
          >
            <FileText className="w-4 h-4" />
            System Logs
          </button>
          <button
            onClick={() => navigate('/settings/advanced')}
            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center gap-2"
          >
            <Settings className="w-4 h-4" />
            Advanced Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModernSettingsPage;
