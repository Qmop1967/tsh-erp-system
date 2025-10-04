import React, { useState, useMemo, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate, useLocation } from 'react-router-dom';
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

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

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
    {
      id: 'settings',
      name: 'Settings',
      icon: Settings,
      path: '/settings',
      color: '#6b7280'
    }
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

            <button
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '10px',
                borderRadius: '8px',
                color: theme.text,
                position: 'relative',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = theme.hover;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <Bell size={20} />
              <span
                style={{
                  position: 'absolute',
                  top: '8px',
                  right: '8px',
                  width: '8px',
                  height: '8px',
                  backgroundColor: '#ef4444',
                  borderRadius: '50%',
                  border: `2px solid ${theme.surface}`
                }}
              />
            </button>
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
    </div>
  );
}
