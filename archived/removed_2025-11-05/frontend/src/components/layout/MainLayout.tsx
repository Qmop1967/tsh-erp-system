import React, { useState, useMemo, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate, useLocation } from 'react-router-dom';
import ChatGPTFloatingButton from '../chatgpt/ChatGPTFloatingButton';
import { 
  LayoutDashboard, 
  Users, 
  ShoppingCart, 
  Package, 
  Calculator,
  DollarSign,
  Monitor,
  Building2,
  Shield,
  BarChart3,
  Settings,
  Menu,
  X,
  Search,
  Bell,
  User,
  LogOut,
  Moon,
  Sun,
  ChevronRight,
  ChevronDown,
  ChevronsLeft,
  ChevronsRight
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

interface MainLayoutProps {
  children: React.ReactNode;
}

// Notification interface
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  read: boolean;
}

export function MainLayout({ children }: MainLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState<string[]>(['user-management']);
  const [hoveredMenu, setHoveredMenu] = useState<string | null>(null);
  const [hoveredDropdown, setHoveredDropdown] = useState<string | null>(null);
  const [dropdownPosition, setDropdownPosition] = useState<{ top: number; left: number } | null>(null);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const menuItemRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  
  // Notification state
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      title: 'New Order',
      message: 'Order #12345 has been placed',
      type: 'info',
      timestamp: new Date(Date.now() - 5 * 60000),
      read: false
    },
    {
      id: '2',
      title: 'Low Stock Alert',
      message: 'Product ABC is running low on stock',
      type: 'warning',
      timestamp: new Date(Date.now() - 30 * 60000),
      read: false
    },
    {
      id: '3',
      title: 'Payment Received',
      message: 'Payment of $500 received from Customer XYZ',
      type: 'success',
      timestamp: new Date(Date.now() - 2 * 60 * 60000),
      read: false
    }
  ]);
  const [showNotifications, setShowNotifications] = useState(false);
  const notificationRef = useRef<HTMLDivElement>(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

  // Close notifications dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };

    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showNotifications]);

  // Notification functions
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notif => notif.id === id ? { ...notif, read: true } : notif)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  // Theme configuration
  const lightTheme = {
    primary: '#2563eb',
    secondary: '#6b7280',
    background: '#f9fafb',
    surface: '#ffffff',
    text: '#111827',
    textSecondary: '#6b7280',
    border: '#e5e7eb',
    sidebar: '#ffffff',
    sidebarText: '#111827',
    hover: '#f3f4f6'
  };

  const darkTheme = {
    primary: '#3b82f6',
    secondary: '#94a3b8',
    background: '#0f172a',
    surface: '#1e293b',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
    sidebar: '#1e293b',
    sidebarText: '#cbd5e1',
    hover: '#334155'
  };

  const theme = useMemo(() => isDark ? darkTheme : lightTheme, [isDark]);

  const menuItems = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      color: '#3b82f6'
    },
    {
      id: 'user-management',
      name: 'User Management',
      icon: Users,
      path: '/users',
      color: '#8b5cf6',
      subItems: [
        { name: 'All Users', path: '/users' },
        { name: 'Permissions', path: '/permissions' },
        { name: 'Roles', path: '/roles' }
      ]
    },
    {
      id: 'hr',
      name: 'Human Resources',
      icon: User,
      path: '/hr',
      color: '#ec4899'
    },
    {
      id: 'sales',
      name: 'Sales Management',
      icon: ShoppingCart,
      path: '/sales',
      color: '#10b981'
    },
    {
      id: 'inventory',
      name: 'Inventory',
      icon: Package,
      path: '/inventory',
      color: '#f59e0b',
      subItems: [
        { name: 'Items', path: '/inventory/items' },
        { name: 'Categories', path: '/inventory/categories' },
        { name: 'Stock Movement', path: '/inventory/movements' }
      ]
    },
    {
      id: 'purchase',
      name: 'Purchase',
      icon: ShoppingCart,
      path: '/purchase',
      color: '#06b6d4'
    },
    {
      id: 'accounting',
      name: 'Accounting',
      icon: Calculator,
      path: '/accounting',
      color: '#8b5cf6'
    },
    {
      id: 'financial',
      name: 'Financial Management',
      icon: DollarSign,
      path: '/financial',
      color: '#eab308'
    },
    {
      id: 'pos',
      name: 'Point of Sale',
      icon: Monitor,
      path: '/pos',
      color: '#ec4899'
    },
    {
      id: 'branches',
      name: 'Branches',
      icon: Building2,
      path: '/branches',
      color: '#14b8a6'
    },
    {
      id: 'security',
      name: 'Security',
      icon: Shield,
      path: '/security',
      color: '#ef4444'
    },
    {
      id: 'reports',
      name: 'Reports',
      icon: BarChart3,
      path: '/reports',
      color: '#8b5cf6'
    },
  ];

  const toggleMenu = (menuId: string) => {
    setExpandedMenus(prev => 
      prev.includes(menuId) 
        ? prev.filter(id => id !== menuId)
        : [...prev, menuId]
    );
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', backgroundColor: theme.background }}>
      {/* Sidebar */}
      <div
        style={{
          width: !isSidebarOpen ? '0' : (isSidebarCollapsed ? '80px' : '280px'),
          backgroundColor: theme.sidebar,
          borderRight: `1px solid ${theme.border}`,
          transition: 'width 0.3s ease',
          overflow: 'visible', // Changed from 'hidden' to allow dropdowns to extend beyond sidebar
          display: 'flex',
          flexDirection: 'column',
          position: 'relative', // Ensure proper positioning context
          zIndex: 100 // Ensure sidebar and its dropdowns are above main content
        }}
      >
        {/* Logo & Brand */}
        <div
          style={{
            padding: '24px 20px',
            borderBottom: `1px solid ${theme.border}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: isSidebarCollapsed ? 'center' : 'flex-start',
            gap: '12px'
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              backgroundColor: theme.primary,
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '20px',
              fontWeight: 'bold'
            }}
          >
            TE
          </div>
          {!isSidebarCollapsed && (
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: '700', fontSize: '18px', color: theme.text }}>
                TSH ERP
              </div>
              <div style={{ fontSize: '12px', color: theme.textSecondary }}>
                Enterprise System
              </div>
            </div>
          )}
        </div>

        {/* Navigation Menu */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          overflowX: 'visible', 
          padding: '16px 0',
          position: 'relative' // This allows absolute positioned children to escape
        }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = isActiveRoute(item.path);
            const isExpanded = expandedMenus.includes(item.id);
            const hasSubItems = item.subItems && item.subItems.length > 0;

            return (
              <div 
                key={item.id} 
                ref={(el) => { menuItemRefs.current[item.id] = el; }}
                style={{ position: 'relative' }}
                onMouseEnter={(e) => {
                  // Clear any pending hide timeout
                  if (hoverTimeoutRef.current) {
                    clearTimeout(hoverTimeoutRef.current);
                    hoverTimeoutRef.current = null;
                  }
                  
                  // Calculate dropdown position relative to viewport
                  const rect = e.currentTarget.getBoundingClientRect();
                  setDropdownPosition({
                    top: rect.top,
                    left: rect.right + 12 // 12px gap from sidebar edge
                  });
                  
                  setHoveredMenu(item.id);
                  // In collapsed mode, always show dropdown/tooltip
                  // In expanded mode, only show dropdown if menu is NOT manually expanded
                  if (isSidebarCollapsed || (!isSidebarCollapsed && hasSubItems && !expandedMenus.includes(item.id))) {
                    setHoveredDropdown(item.id);
                  }
                }}
                onMouseLeave={() => {
                  // Delay hiding to prevent flicker when moving to dropdown
                  hoverTimeoutRef.current = setTimeout(() => {
                    setHoveredMenu(null);
                    setHoveredDropdown(null);
                  }, 100); // 100ms delay
                }}
              >
                <div
                  onClick={() => {
                    // If sidebar is collapsed, expand it first
                    if (isSidebarCollapsed) {
                      setSidebarCollapsed(false);
                    }
                    
                    if (hasSubItems) {
                      toggleMenu(item.id);
                    } else {
                      navigate(item.path);
                    }
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: isSidebarCollapsed ? 'center' : 'flex-start',
                    gap: '12px',
                    padding: isSidebarCollapsed ? '12px' : '12px 20px',
                    margin: '2px 12px',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    backgroundColor: isActive ? `${theme.primary}15` : 'transparent',
                    color: isActive ? theme.primary : theme.sidebarText,
                    transition: 'all 0.2s ease',
                    fontWeight: isActive ? '600' : '500',
                    fontSize: '14px',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = theme.hover;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                  title={isSidebarCollapsed ? item.name : ''}
                >
                  <Icon size={20} style={{ color: isActive ? theme.primary : item.color }} />
                  {!isSidebarCollapsed && (
                    <>
                      <span style={{ flex: 1 }}>{item.name}</span>
                      {hasSubItems && (
                        isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
                      )}
                    </>
                  )}
                </div>

                {/* Tooltip/Dropdown for collapsed state */}
                {isSidebarCollapsed && hoveredDropdown === item.id && (
                  <div
                    onMouseEnter={() => {
                      // Clear any pending hide timeout
                      if (hoverTimeoutRef.current) {
                        clearTimeout(hoverTimeoutRef.current);
                        hoverTimeoutRef.current = null;
                      }
                      setHoveredMenu(item.id);
                      setHoveredDropdown(item.id);
                    }}
                    onMouseLeave={() => {
                      // Delay hiding to prevent flicker
                      hoverTimeoutRef.current = setTimeout(() => {
                        setHoveredMenu(null);
                        setHoveredDropdown(null);
                      }, 100);
                    }}
                    style={{
                      position: 'fixed', // Changed to fixed to break out of overflow context
                      left: dropdownPosition ? `${dropdownPosition.left}px` : '0',
                      top: dropdownPosition ? `${dropdownPosition.top}px` : '0',
                      transform: hasSubItems ? 'translateY(0)' : 'translateY(-50%)',
                      padding: hasSubItems ? '8px' : '8px 16px',
                      backgroundColor: theme.surface,
                      color: theme.text,
                      borderRadius: '10px',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.2), 0 2px 8px rgba(0,0,0,0.15)', // Enhanced shadow for overlay effect
                      border: `1px solid ${theme.border}`,
                      whiteSpace: 'nowrap',
                      fontSize: '14px',
                      fontWeight: '500',
                      zIndex: 9999, // Very high z-index to ensure it overlays main content
                      pointerEvents: hasSubItems ? 'auto' : 'none',
                      animation: 'fadeIn 0.2s ease',
                      minWidth: hasSubItems ? '220px' : 'auto'
                    }}
                  >
                    {/* Menu title */}
                    {hasSubItems && (
                      <div style={{ 
                        padding: '8px 12px', 
                        fontWeight: '600',
                        fontSize: '13px',
                        color: theme.textSecondary,
                        borderBottom: `1px solid ${theme.border}`,
                        marginBottom: '4px'
                      }}>
                        {item.name}
                      </div>
                    )}
                    
                    {/* Simple tooltip for items without sub-items */}
                    {!hasSubItems && item.name}
                    
                    {/* Sub-menu items */}
                    {hasSubItems && item.subItems!.map((subItem) => {
                      const isSubActive = location.pathname === subItem.path;
                      return (
                        <div
                          key={subItem.path}
                          onClick={() => {
                            setSidebarCollapsed(false);
                            navigate(subItem.path);
                            setHoveredMenu(null);
                            setHoveredDropdown(null);
                          }}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '10px 12px',
                            margin: '2px 0',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            backgroundColor: isSubActive ? `${theme.primary}10` : 'transparent',
                            color: isSubActive ? theme.primary : theme.text,
                            transition: 'all 0.2s ease',
                            fontSize: '13px',
                            fontWeight: isSubActive ? '600' : '400'
                          }}
                          onMouseEnter={(e) => {
                            if (!isSubActive) {
                              e.currentTarget.style.backgroundColor = theme.hover;
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!isSubActive) {
                              e.currentTarget.style.backgroundColor = isSubActive ? `${theme.primary}10` : 'transparent';
                            }
                          }}
                        >
                          <div
                            style={{
                              width: '4px',
                              height: '4px',
                              borderRadius: '50%',
                              backgroundColor: isSubActive ? theme.primary : theme.textSecondary
                            }}
                          />
                          <span>{subItem.name}</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Sub-items - Traditional Click-to-Expand (shown when manually expanded) */}
                {hasSubItems && isExpanded && !isSidebarCollapsed && (
                  <div style={{ marginLeft: '20px' }}>
                    {item.subItems!.map((subItem) => {
                      const isSubActive = location.pathname === subItem.path;
                      return (
                        <div
                          key={subItem.path}
                          onClick={() => {
                            // If sidebar is collapsed, expand it first
                            if (isSidebarCollapsed) {
                              setSidebarCollapsed(false);
                            }
                            navigate(subItem.path);
                          }}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '10px 20px',
                            margin: '2px 12px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            backgroundColor: isSubActive ? `${theme.primary}10` : 'transparent',
                            color: isSubActive ? theme.primary : theme.textSecondary,
                            transition: 'all 0.2s ease',
                            fontSize: '13px',
                            fontWeight: isSubActive ? '600' : '400'
                          }}
                          onMouseEnter={(e) => {
                            if (!isSubActive) {
                              e.currentTarget.style.backgroundColor = theme.hover;
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!isSubActive) {
                              e.currentTarget.style.backgroundColor = 'transparent';
                            }
                          }}
                        >
                          <div
                            style={{
                              width: '6px',
                              height: '6px',
                              borderRadius: '50%',
                              backgroundColor: isSubActive ? theme.primary : theme.textSecondary
                            }}
                          />
                          <span>{subItem.name}</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Hover Dropdown for Expanded Sidebar (Zoho-style) */}
                {!isSidebarCollapsed && hasSubItems && hoveredDropdown === item.id && !isExpanded && (
                  <div
                    style={{
                      position: 'fixed', // Changed to fixed to break out of overflow context
                      left: dropdownPosition ? `${dropdownPosition.left}px` : '0',
                      top: dropdownPosition ? `${dropdownPosition.top}px` : '0',
                      padding: '8px',
                      backgroundColor: theme.surface,
                      color: theme.text,
                      borderRadius: '10px',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.2), 0 2px 8px rgba(0,0,0,0.15)', // Enhanced shadow for overlay effect
                      border: `1px solid ${theme.border}`,
                      whiteSpace: 'nowrap',
                      fontSize: '14px',
                      fontWeight: '500',
                      zIndex: 9999, // Very high z-index to ensure it overlays main content
                      pointerEvents: 'auto',
                      animation: 'fadeIn 0.2s ease',
                      minWidth: '240px'
                    }}
                    onMouseEnter={() => {
                      // Clear any pending hide timeout
                      if (hoverTimeoutRef.current) {
                        clearTimeout(hoverTimeoutRef.current);
                        hoverTimeoutRef.current = null;
                      }
                      setHoveredMenu(item.id);
                      setHoveredDropdown(item.id);
                    }}
                    onMouseLeave={() => {
                      // Delay hiding to prevent flicker
                      hoverTimeoutRef.current = setTimeout(() => {
                        setHoveredMenu(null);
                        setHoveredDropdown(null);
                      }, 100);
                    }}
                  >
                    {/* Dropdown title */}
                    <div style={{ 
                      padding: '8px 12px', 
                      fontWeight: '600',
                      fontSize: '14px',
                      color: theme.text,
                      borderBottom: `1px solid ${theme.border}`,
                      marginBottom: '4px'
                    }}>
                      {item.name}
                    </div>
                    
                    {/* Sub-menu items in dropdown */}
                    {item.subItems!.map((subItem) => {
                      const isSubActive = location.pathname === subItem.path;
                      return (
                        <div
                          key={subItem.path}
                          onClick={() => {
                            navigate(subItem.path);
                            setHoveredDropdown(null);
                            setHoveredMenu(null);
                          }}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px',
                            padding: '10px 12px',
                            margin: '2px 0',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            backgroundColor: isSubActive ? `${theme.primary}12` : 'transparent',
                            color: isSubActive ? theme.primary : theme.text,
                            transition: 'all 0.2s ease',
                            fontSize: '13px',
                            fontWeight: isSubActive ? '600' : '400'
                          }}
                          onMouseEnter={(e) => {
                            if (!isSubActive) {
                              e.currentTarget.style.backgroundColor = theme.hover;
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!isSubActive) {
                              e.currentTarget.style.backgroundColor = isSubActive ? `${theme.primary}12` : 'transparent';
                            }
                          }}
                        >
                          <div
                            style={{
                              width: '5px',
                              height: '5px',
                              borderRadius: '50%',
                              backgroundColor: isSubActive ? theme.primary : theme.textSecondary
                            }}
                          />
                          <span>{subItem.name}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Collapse/Expand Button */}
        <div
          style={{
            padding: '12px 20px',
            borderTop: `1px solid ${theme.border}`
          }}
        >
          <button
            onClick={() => setSidebarCollapsed(!isSidebarCollapsed)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: isSidebarCollapsed ? 'center' : 'space-between',
              padding: '10px 12px',
              background: theme.hover,
              border: `1px solid ${theme.border}`,
              borderRadius: '8px',
              cursor: 'pointer',
              color: theme.text,
              fontSize: '13px',
              fontWeight: '500',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = theme.primary + '15';
              e.currentTarget.style.borderColor = theme.primary;
              e.currentTarget.style.color = theme.primary;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = theme.hover;
              e.currentTarget.style.borderColor = theme.border;
              e.currentTarget.style.color = theme.text;
            }}
            title={isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {!isSidebarCollapsed && <span>Collapse</span>}
            {isSidebarCollapsed ? (
              <ChevronsRight size={18} />
            ) : (
              <ChevronsLeft size={18} />
            )}
          </button>
        </div>

        {/* User Profile Section */}
        <div
          style={{
            padding: '16px 20px',
            borderTop: `1px solid ${theme.border}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: isSidebarCollapsed ? 'center' : 'flex-start',
            gap: '12px',
            flexWrap: isSidebarCollapsed ? 'wrap' : 'nowrap'
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: `${theme.primary}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: theme.primary,
              fontWeight: '600'
            }}
            title={isSidebarCollapsed ? (user?.name || 'Demo User') : ''}
          >
            {user?.name?.charAt(0) || 'D'}
          </div>
          {!isSidebarCollapsed && (
            <>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: theme.text,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {user?.name || 'Demo User'}
                </div>
                <div style={{ fontSize: '12px', color: theme.textSecondary }}>
                  {user?.role || 'Administrator'}
                </div>
              </div>
              <button
                onClick={handleLogout}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '8px',
                  borderRadius: '8px',
                  color: theme.textSecondary,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = theme.hover;
                  e.currentTarget.style.color = '#ef4444';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = theme.textSecondary;
                }}
                title="Logout"
              >
                <LogOut size={18} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top Header */}
        <div
          style={{
            height: '70px',
            backgroundColor: theme.surface,
            borderBottom: `1px solid ${theme.border}`,
            display: 'flex',
            alignItems: 'center',
            padding: '0 24px',
            gap: '16px'
          }}
        >
          <button
            onClick={() => setSidebarOpen(!isSidebarOpen)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              color: theme.text,
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = theme.hover;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          {/* Search Bar */}
          <div
            style={{
              flex: 1,
              maxWidth: '600px',
              position: 'relative'
            }}
          >
            <Search
              size={20}
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: theme.textSecondary
              }}
            />
            <input
              type="text"
              placeholder="Search anything..."
              style={{
                width: '100%',
                padding: '10px 12px 10px 44px',
                border: `1px solid ${theme.border}`,
                borderRadius: '10px',
                backgroundColor: theme.background,
                color: theme.text,
                fontSize: '14px',
                outline: 'none',
                transition: 'all 0.2s ease'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = theme.primary;
                e.currentTarget.style.boxShadow = `0 0 0 3px ${theme.primary}15`;
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = theme.border;
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
          </div>

          {/* Right Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: 'auto' }}>
            <button
              onClick={() => setIsDark(!isDark)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '10px',
                borderRadius: '8px',
                color: theme.text,
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = theme.hover;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {isDark ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Settings Button */}
            <button
              onClick={() => navigate('/settings')}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '10px',
                borderRadius: '8px',
                color: theme.text,
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = theme.hover;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              title="Settings"
            >
              <Settings size={20} />
            </button>

            {/* Notification Button with Dropdown */}
            <div style={{ position: 'relative' }} ref={notificationRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '10px',
                  borderRadius: '8px',
                  color: theme.text,
                  position: 'relative',
                  transition: 'background-color 0.2s',
                  backgroundColor: showNotifications ? theme.hover : 'transparent'
                }}
                onMouseEnter={(e) => {
                  if (!showNotifications) {
                    e.currentTarget.style.backgroundColor = theme.hover;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!showNotifications) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
                title={`${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`}
              >
                <Bell size={20} />
                {unreadCount > 0 && (
                  <span
                    style={{
                      position: 'absolute',
                      top: '6px',
                      right: '6px',
                      minWidth: '18px',
                      height: '18px',
                      backgroundColor: '#ef4444',
                      borderRadius: '10px',
                      border: `2px solid ${theme.surface}`,
                      fontSize: '10px',
                      fontWeight: '600',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '0 4px'
                    }}
                  >
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Notification Dropdown */}
              {showNotifications && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    right: 0,
                    marginTop: '8px',
                    width: '380px',
                    maxHeight: '500px',
                    backgroundColor: theme.surface,
                    borderRadius: '12px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                    border: `1px solid ${theme.border}`,
                    zIndex: 1000,
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column'
                  }}
                >
                  {/* Header */}
                  <div
                    style={{
                      padding: '16px 20px',
                      borderBottom: `1px solid ${theme.border}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <h3
                      style={{
                        margin: 0,
                        fontSize: '16px',
                        fontWeight: '600',
                        color: theme.text
                      }}
                    >
                      Notifications
                      {unreadCount > 0 && (
                        <span
                          style={{
                            marginLeft: '8px',
                            fontSize: '12px',
                            fontWeight: '500',
                            color: theme.textSecondary
                          }}
                        >
                          ({unreadCount} new)
                        </span>
                      )}
                    </h3>
                    {notifications.length > 0 && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {unreadCount > 0 && (
                          <button
                            onClick={markAllAsRead}
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              fontSize: '12px',
                              color: theme.primary,
                              fontWeight: '500',
                              padding: '4px 8px',
                              borderRadius: '6px',
                              transition: 'background-color 0.2s'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.backgroundColor = `${theme.primary}15`;
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                          >
                            Mark all read
                          </button>
                        )}
                        <button
                          onClick={clearAllNotifications}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '12px',
                            color: '#ef4444',
                            fontWeight: '500',
                            padding: '4px 8px',
                            borderRadius: '6px',
                            transition: 'background-color 0.2s'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#ef444415';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = 'transparent';
                          }}
                        >
                          Clear all
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Notifications List */}
                  <div
                    style={{
                      overflowY: 'auto',
                      maxHeight: '400px'
                    }}
                  >
                    {notifications.length === 0 ? (
                      <div
                        style={{
                          padding: '40px 20px',
                          textAlign: 'center',
                          color: theme.textSecondary
                        }}
                      >
                        <Bell
                          size={48}
                          style={{
                            opacity: 0.3,
                            marginBottom: '12px'
                          }}
                        />
                        <p style={{ margin: 0, fontSize: '14px' }}>No notifications</p>
                      </div>
                    ) : (
                      notifications.map((notification) => (
                        <div
                          key={notification.id}
                          onClick={() => {
                            markAsRead(notification.id);
                            setShowNotifications(false);
                          }}
                          style={{
                            padding: '16px 20px',
                            borderBottom: `1px solid ${theme.border}`,
                            cursor: 'pointer',
                            backgroundColor: notification.read ? 'transparent' : `${theme.primary}08`,
                            transition: 'background-color 0.2s',
                            position: 'relative'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = theme.hover;
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = notification.read ? 'transparent' : `${theme.primary}08`;
                          }}
                        >
                          <div style={{ display: 'flex', gap: '12px', alignItems: 'start' }}>
                            <span style={{ fontSize: '20px', flexShrink: 0 }}>
                              {getNotificationIcon(notification.type)}
                            </span>
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div
                                style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '8px',
                                  marginBottom: '4px'
                                }}
                              >
                                <h4
                                  style={{
                                    margin: 0,
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    color: theme.text
                                  }}
                                >
                                  {notification.title}
                                </h4>
                                {!notification.read && (
                                  <div
                                    style={{
                                      width: '6px',
                                      height: '6px',
                                      borderRadius: '50%',
                                      backgroundColor: theme.primary,
                                      flexShrink: 0
                                    }}
                                  />
                                )}
                              </div>
                              <p
                                style={{
                                  margin: '0 0 4px 0',
                                  fontSize: '13px',
                                  color: theme.textSecondary,
                                  lineHeight: '1.4'
                                }}
                              >
                                {notification.message}
                              </p>
                              <span
                                style={{
                                  fontSize: '11px',
                                  color: theme.textSecondary,
                                  opacity: 0.8
                                }}
                              >
                                {formatTimeAgo(notification.timestamp)}
                              </span>
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteNotification(notification.id);
                              }}
                              style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px',
                                color: theme.textSecondary,
                                opacity: 0,
                                transition: 'opacity 0.2s, background-color 0.2s',
                                fontSize: '18px',
                                lineHeight: '1',
                                flexShrink: 0
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#ef444420';
                                e.currentTarget.style.color = '#ef4444';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'transparent';
                                e.currentTarget.style.color = theme.textSecondary;
                              }}
                              className="notification-delete-btn"
                            >
                              ×
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Footer */}
                  {notifications.length > 0 && (
                    <div
                      style={{
                        padding: '12px 20px',
                        borderTop: `1px solid ${theme.border}`,
                        textAlign: 'center'
                      }}
                    >
                      <button
                        onClick={() => {
                          setShowNotifications(false);
                          navigate('/notifications');
                        }}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          fontSize: '13px',
                          color: theme.primary,
                          fontWeight: '500',
                          padding: '4px 8px',
                          borderRadius: '6px',
                          transition: 'background-color 0.2s',
                          width: '100%'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = `${theme.primary}15`;
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }}
                      >
                        View all notifications
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            <style>
              {`
                .notification-delete-btn {
                  opacity: 0 !important;
                }
                div:hover > div > .notification-delete-btn {
                  opacity: 1 !important;
                }
              `}
            </style>
          </div>
        </div>

        {/* Page Content */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            backgroundColor: theme.background,
            padding: '24px'
          }}
        >
          {children}
        </div>
      </div>
      
      {/* ChatGPT Floating Button */}
      <ChatGPTFloatingButton />
    </div>
  );
}
