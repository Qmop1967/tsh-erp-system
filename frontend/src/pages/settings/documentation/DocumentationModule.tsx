import React, { useState } from 'react';
import {
  BookOpen,
  ChevronDown,
  ChevronRight,
  Code,
  HelpCircle,
  ExternalLink,
  Copy,
  CheckCircle,
  Globe,
  Zap,
  Database,
  Users,
  ShoppingCart,
  BarChart3,
  Lock,
  Smartphone,
  MessageSquare,
  Sparkles,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ApiEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  endpoint: string;
  description: string;
  params?: string[];
  example?: string;
  response?: string;
}

interface GuideItem {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  content: string;
  lastUpdated: string;
}

interface DocumentationSection {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  content: ApiEndpoint[] | GuideItem[] | any[];
}

const DocumentationModule: React.FC = () => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['api-endpoints']);
  const [copiedEndpoint, setCopiedEndpoint] = useState<string | null>(null);

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const copyToClipboard = async (text: string, endpointId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedEndpoint(endpointId);
      setTimeout(() => setCopiedEndpoint(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-green-100 text-green-800 border-green-200';
      case 'POST': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'PUT': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'DELETE': return 'bg-red-100 text-red-800 border-red-200';
      case 'PATCH': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const apiEndpoints: ApiEndpoint[] = [
    {
      method: 'GET',
      endpoint: '/api/auth/me',
      description: 'Get current user information',
      example: 'curl -H "Authorization: Bearer <token>" http://localhost:8000/api/auth/me',
      response: '{"id": 1, "email": "admin@tsh.sale", "role": "admin"}'
    },
    {
      method: 'POST',
      endpoint: '/api/auth/login',
      description: 'Authenticate user and get access token',
      params: ['email', 'password'],
      example: 'curl -X POST -H "Content-Type: application/json" -d \'{"email":"admin@tsh.sale","password":"password"}\' http://localhost:8000/api/auth/login',
      response: '{"access_token": "eyJ...", "token_type": "bearer", "user": {...}}'
    },
    {
      method: 'GET',
      endpoint: '/api/users',
      description: 'Get list of all users (Admin only)',
      params: ['page', 'limit', 'search'],
      example: 'curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users?page=1&limit=20',
      response: '{"users": [...], "total": 50, "page": 1, "pages": 3}'
    },
    {
      method: 'POST',
      endpoint: '/api/users',
      description: 'Create a new user',
      params: ['email', 'password', 'full_name', 'role_id'],
      example: 'curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d \'{"email":"user@example.com","password":"password","full_name":"John Doe","role_id":2}\' http://localhost:8000/api/users',
      response: '{"id": 5, "email": "user@example.com", "full_name": "John Doe", "created_at": "..."}'
    },
    {
      method: 'GET',
      endpoint: '/api/inventory/items',
      description: 'Get inventory items with filters',
      params: ['category', 'search', 'in_stock', 'page', 'limit'],
      example: 'curl -H "Authorization: Bearer <token>" http://localhost:8000/api/inventory/items?in_stock=true&category=electronics',
      response: '{"items": [...], "total": 100, "categories": [...], "low_stock_count": 5}'
    },
    {
      method: 'POST',
      endpoint: '/api/inventory/items',
      description: 'Add new inventory item',
      params: ['name', 'description', 'category_id', 'price', 'quantity', 'sku'],
      example: 'curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d \'{"name":"Laptop","price":999.99,"quantity":10,"sku":"LAP001"}\' http://localhost:8000/api/inventory/items',
      response: '{"id": 15, "name": "Laptop", "sku": "LAP001", "created_at": "..."}'
    },
    {
      method: 'GET',
      endpoint: '/api/sales/orders',
      description: 'Get sales orders',
      params: ['status', 'customer_id', 'date_from', 'date_to', 'page'],
      example: 'curl -H "Authorization: Bearer <token>" http://localhost:8000/api/sales/orders?status=pending',
      response: '{"orders": [...], "total_amount": 15000.50, "count": 25}'
    },
    {
      method: 'POST',
      endpoint: '/api/sales/orders',
      description: 'Create new sales order',
      params: ['customer_id', 'items', 'discount', 'notes'],
      example: 'curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d \'{"customer_id":5,"items":[{"item_id":1,"quantity":2,"price":50.00}]}\' http://localhost:8000/api/sales/orders',
      response: '{"id": 123, "order_number": "ORD-2025-123", "total": 100.00, "status": "pending"}'
    }
  ];

  const guides: GuideItem[] = [
    {
      title: 'Getting Started Guide',
      description: 'Complete setup and onboarding guide for new users',
      icon: Sparkles,
      lastUpdated: '2025-10-05',
      content: `
# Getting Started with TSH ERP System

## Overview
Welcome to TSH ERP System - your comprehensive business management solution.

## Initial Setup
1. **Admin Account**: Use admin@tsh.sale / admin123 for initial login
2. **Company Profile**: Navigate to Settings > Organization Profile
3. **User Management**: Add your team members in Users section
4. **Roles & Permissions**: Configure access levels for different users

## Key Features
- **Inventory Management**: Track products, stock levels, and categories
- **Sales Processing**: Handle orders, invoices, and customer management  
- **User Management**: RBAC system with granular permissions
- **Integrations**: ChatGPT AI, WhatsApp Business, Zoho sync
- **Multi-language**: Arabic and English support

## Quick Actions
- Add new inventory item: Inventory > Items > Add Item
- Create sales order: Sales > Orders > New Order
- Manage users: Users > Add User
- Configure integrations: Settings > Integrations
      `
    },
    {
      title: 'API Integration Guide',
      description: 'How to integrate with TSH ERP APIs',
      icon: Code,
      lastUpdated: '2025-10-05',
      content: `
# API Integration Guide

## Authentication
All API requests require a Bearer token obtained from the login endpoint.

\`\`\`bash
# Get access token
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "admin@tsh.sale", "password": "admin123"}'
\`\`\`

## Rate Limiting
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated endpoints

## Error Handling
Standard HTTP status codes:
- 200: Success
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Server Error

## SDKs Available
- JavaScript/TypeScript SDK
- Python SDK
- PHP SDK (Coming Soon)
      `
    },
    {
      title: 'User Management',
      description: 'Comprehensive guide to managing users and permissions',
      icon: Users,
      lastUpdated: '2025-10-04',
      content: `
# User Management Guide

## User Roles
1. **Admin**: Full system access
2. **Manager**: Department management access
3. **Sales**: Sales and customer management
4. **Inventory**: Stock and product management
5. **Cashier**: POS and payment processing

## Creating Users
1. Navigate to Users section
2. Click "Add User"
3. Fill required information
4. Assign appropriate role
5. Set initial password (user must change on first login)

## Permission Management
- Granular permissions for each feature
- Role-based access control (RBAC)
- Record-level security rules
- Branch/location-based access
      `
    },
    {
      title: 'Inventory Management',
      description: 'Guide to managing products, stock, and categories',
      icon: Database,
      lastUpdated: '2025-10-03',
      content: `
# Inventory Management Guide

## Product Categories
Organize your inventory with hierarchical categories:
- Electronics > Laptops > Gaming Laptops
- Clothing > Men's > Shirts

## Stock Tracking
- Real-time stock levels
- Low stock alerts
- Stock movement history
- Automatic reorder points

## Barcode Integration
- Generate SKU codes automatically
- Barcode scanning support
- Bulk import from CSV/Excel

## Pricing Management
- Cost price tracking
- Multiple selling prices
- Discount configurations
- Tax calculations
      `
    },
    {
      title: 'Sales Processing',
      description: 'Complete guide to processing sales and orders',
      icon: ShoppingCart,
      lastUpdated: '2025-10-02',
      content: `
# Sales Processing Guide

## Order Management
1. **Create Order**: Add customer and items
2. **Apply Discounts**: Percentage or fixed amount
3. **Payment Processing**: Cash, card, or credit
4. **Generate Invoice**: Automatic invoice creation
5. **Track Status**: Pending > Processing > Completed

## Customer Management
- Customer database with history
- Credit limits and payment terms
- Loyalty program integration
- Communication tracking

## Reporting
- Daily sales reports
- Customer analytics
- Product performance
- Profit margin analysis
      `
    },
    {
      title: 'Mobile Applications',
      description: 'Guide to using TSH ERP mobile apps',
      icon: Smartphone,
      lastUpdated: '2025-10-01',
      content: `
# Mobile Applications Guide

## Available Apps
1. **Salesperson App**: On-the-go sales processing
2. **Inventory App**: Stock checking and updates
3. **Manager App**: Real-time business insights
4. **Cashier App**: POS system for retail

## Installation
- Download from TSH Mobile Hub
- Use company code: TSH-DEMO
- Login with your ERP credentials

## Features
- Offline mode support
- Real-time synchronization
- Barcode scanning
- Location-based services
      `
    }
  ];

  const troubleshooting = [
    {
      title: 'Common Login Issues',
      description: 'Resolve authentication and access problems',
      icon: Lock,
      lastUpdated: '2025-10-05',
      content: 'Solutions for login failures, password resets, and access issues...'
    },
    {
      title: 'API Troubleshooting',
      description: 'Debug API integration problems',
      icon: Zap,
      lastUpdated: '2025-10-04',
      content: 'Common API errors and their solutions...'
    },
    {
      title: 'Performance Optimization',
      description: 'Improve system performance and speed',
      icon: BarChart3,
      lastUpdated: '2025-10-03',
      content: 'Tips for optimizing database queries and system performance...'
    },
    {
      title: 'Data Backup & Recovery',
      description: 'Backup procedures and data recovery methods',
      icon: Database,
      lastUpdated: '2025-10-02',
      content: 'Step-by-step backup and recovery procedures...'
    }
  ];

  const documentationSections: DocumentationSection[] = [
    {
      id: 'api-endpoints',
      title: 'API Endpoints',
      description: 'Complete API reference with examples and responses',
      icon: Code,
      content: apiEndpoints
    },
    {
      id: 'user-guides',
      title: 'User Guides & Tutorials',
      description: 'Step-by-step guides for using the system',
      icon: BookOpen,
      content: guides
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting & FAQ',
      description: 'Common issues and their solutions',
      icon: HelpCircle,
      content: troubleshooting
    }
  ];

  const isExpanded = (sectionId: string) => expandedSections.includes(sectionId);

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg">
          <BookOpen className="h-5 w-5 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Documentation Center</h2>
          <p className="text-gray-600">API references, guides, and troubleshooting resources</p>
        </div>
      </div>

      <div className="grid gap-6">
        {documentationSections.map((section) => (
          <Card key={section.id} className="overflow-hidden">
            <CardHeader 
              className="cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleSection(section.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 bg-indigo-100 rounded-lg">
                    <section.icon className="h-4 w-4 text-indigo-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{section.title}</CardTitle>
                    <CardDescription className="text-sm">{section.description}</CardDescription>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary" className="text-xs">
                    {section.content.length} items
                  </Badge>
                  {isExpanded(section.id) ? (
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-gray-500" />
                  )}
                </div>
              </div>
            </CardHeader>

            {isExpanded(section.id) && (
              <CardContent className="pt-0">
                <div className="border-t border-gray-200 pt-4">
                  {section.id === 'api-endpoints' && (
                    <div className="space-y-4">
                      {(section.content as ApiEndpoint[]).map((endpoint, index) => (
                        <div key={index} className="bg-gray-50 rounded-lg p-4 border">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <Badge className={`text-xs font-mono ${getMethodColor(endpoint.method)}`}>
                                {endpoint.method}
                              </Badge>
                              <code className="text-sm font-mono bg-white px-2 py-1 rounded border">
                                {endpoint.endpoint}
                              </code>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(endpoint.endpoint, `${endpoint.method}-${index}`)}
                              className="h-6 w-6 p-0"
                            >
                              {copiedEndpoint === `${endpoint.method}-${index}` ? (
                                <CheckCircle className="h-3 w-3 text-green-600" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </Button>
                          </div>

                          <p className="text-sm text-gray-700 mb-3">{endpoint.description}</p>

                          {endpoint.params && (
                            <div className="mb-3">
                              <p className="text-xs font-medium text-gray-600 mb-1">Parameters:</p>
                              <div className="flex flex-wrap gap-1">
                                {endpoint.params.map((param, paramIndex) => (
                                  <Badge key={paramIndex} variant="outline" className="text-xs">
                                    {param}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {endpoint.example && (
                            <div className="mb-3">
                              <p className="text-xs font-medium text-gray-600 mb-1">Example:</p>
                              <div className="bg-gray-900 text-gray-100 p-2 rounded text-xs font-mono overflow-x-auto">
                                {endpoint.example}
                              </div>
                            </div>
                          )}

                          {endpoint.response && (
                            <div>
                              <p className="text-xs font-medium text-gray-600 mb-1">Response:</p>
                              <div className="bg-green-50 border border-green-200 p-2 rounded text-xs font-mono overflow-x-auto">
                                {endpoint.response}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {(section.id === 'user-guides' || section.id === 'troubleshooting') && (
                    <div className="grid gap-4 md:grid-cols-2">
                      {(section.content as GuideItem[]).map((item, index) => (
                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex items-start space-x-3 mb-3">
                            <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-lg">
                              <item.icon className="h-4 w-4 text-blue-600" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 mb-1">{item.title}</h4>
                              <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                              <p className="text-xs text-gray-500">Updated: {item.lastUpdated}</p>
                            </div>
                          </div>
                          
                          <div className="bg-gray-50 rounded-md p-3 text-xs">
                            <pre className="whitespace-pre-wrap text-gray-700 font-mono leading-relaxed">
                              {item.content.substring(0, 200)}...
                            </pre>
                          </div>
                          
                          <div className="mt-3 flex justify-between items-center">
                            <Button variant="outline" size="sm" className="text-xs">
                              <ExternalLink className="h-3 w-3 mr-1" />
                              View Full Guide
                            </Button>
                            <Button variant="ghost" size="sm" className="text-xs">
                              <Copy className="h-3 w-3 mr-1" />
                              Copy Link
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg">
              <Globe className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">Need More Help?</h3>
              <p className="text-sm text-gray-600 mb-3">
                Can't find what you're looking for? Our support team is here to help.
              </p>
              <div className="flex space-x-3">
                <Button variant="outline" size="sm">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Contact Support
                </Button>
                <Button variant="outline" size="sm">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Online Documentation
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentationModule;