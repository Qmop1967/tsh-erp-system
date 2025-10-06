import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'
import { useNotifications } from '@/components/ui/NotificationProvider'
import { Button } from '@/components/ui/button'
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher'
import { BranchSwitcher } from '@/components/ui/BranchSwitcher'
import {
  Bell,
  Search,
  Sun,
  Moon,
  User,
  Settings,
  ChevronDown,
  Check,
  X
} from 'lucide-react'

export function Header() {
  const [darkMode, setDarkMode] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const { user } = useAuthStore()
  const { language, isRTL } = useLanguageStore()
  const t = useTranslations(language)
  const { addNotification } = useNotifications()
  
  // Sample notifications state
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'New sales order #SO-2024-001',
      message: 'A new sales order has been created',
      time: '5 minutes ago',
      type: 'info',
      read: false
    },
    {
      id: 2,
      title: 'Payment received',
      message: 'Payment of $5,000 received for invoice #INV-2024-156',
      time: '2 hours ago',
      type: 'success',
      read: false
    },
    {
      id: 3,
      title: 'Low stock alert',
      message: 'Product "Premium Widget" is running low on stock',
      time: '1 day ago',
      type: 'warning',
      read: false
    }
  ])

  const unreadCount = notifications.filter(n => !n.read).length

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('.notification-dropdown') && !target.closest('.user-menu')) {
        setShowNotifications(false)
        setShowUserMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const markAsRead = (id: number) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    )
  }

  const handleNotificationClick = (notification: any) => {
    markAsRead(notification.id)
    // Add toast notification using the notification system
    addNotification({
      type: notification.type as 'success' | 'error' | 'warning' | 'info',
      title: notification.title,
      message: notification.message,
      duration: 3000
    })
    setShowNotifications(false)
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500'
      case 'warning':
        return 'bg-yellow-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-blue-500'
    }
  }

  // Function to add a test notification
  const addTestNotification = () => {
    const types = ['info', 'success', 'warning', 'error']
    const randomType = types[Math.floor(Math.random() * types.length)]
    const newNotification = {
      id: Date.now(),
      title: `Test ${randomType} notification`,
      message: `This is a test ${randomType} notification to demonstrate the functionality.`,
      time: 'Just now',
      type: randomType,
      read: false
    }
    setNotifications(prev => [newNotification, ...prev])
    
    // Also show as toast
    addNotification({
      type: randomType as 'success' | 'error' | 'warning' | 'info',
      title: newNotification.title,
      message: newNotification.message,
      duration: 5000
    })
  }

  const hasPermission = (permissions: string[]) => {
    // For testing purposes, always return true to show notification functionality
    console.log('🧪 Testing mode: granting all permissions for notification testing')
    return true
    
    if (!user || !user.permissions) return false
    const userPerms = user.permissions || []
    if (userPerms.includes('admin')) return true
    return permissions.some(permission => userPerms.includes(permission))
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 shadow-sm backdrop-blur-sm">
      <div className="flex items-center justify-between">
        {/* Left side - Search */}
        <div className="flex-1 max-w-md">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
            <input
              type="text"
              placeholder={t.searchPlaceholder}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white dark:focus:bg-gray-600 transition-all duration-200"
            />
          </div>
        </div>

        {/* Center - Branch Switcher */}
        <div className="flex-1 flex justify-center mx-8">
          <BranchSwitcher />
        </div>

        {/* Right side actions */}
        <div className={`flex items-center ${isRTL ? 'space-x-reverse' : ''} space-x-3 flex-1 justify-end`}>
          {/* Language switcher */}
          <LanguageSwitcher />

          {/* Dark mode toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleDarkMode}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200"
          >
            {darkMode ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>

          {/* Settings */}
          {hasPermission(['admin', 'settings.view']) && (
            <Link to="/settings">
              <Button
                variant="ghost"
                size="icon"
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200"
              >
                <Settings className="h-5 w-5" />
              </Button>
            </Link>
          )}

          {/* Test Notification Button (Admin only for testing) */}
          {hasPermission(['admin']) && (
            <Button
              variant="ghost"
              size="icon"
              onClick={addTestNotification}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200"
              title="Add test notification"
            >
              <Check className="h-5 w-5" />
            </Button>
          )}

          {/* Notifications */}
          <div className="relative notification-dropdown">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowNotifications(!showNotifications)}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 relative hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse shadow-lg">
                  {unreadCount}
                </span>
              )}
            </Button>

            {/* Notifications dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                    Notifications
                  </h3>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                    >
                      Mark all as read
                    </button>
                  )}
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                      <Bell className="h-12 w-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
                      <p className="text-sm">No notifications yet</p>
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <div
                        key={notification.id}
                        onClick={() => handleNotificationClick(notification)}
                        className={`px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 ${
                          !notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        <div className="flex items-start">
                          <div className="flex-shrink-0">
                            <div className={`w-2 h-2 ${getNotificationIcon(notification.type)} rounded-full mt-2`}></div>
                          </div>
                          <div className="ml-3 flex-1">
                            <p className={`text-sm ${!notification.read ? 'font-semibold' : 'font-medium'} text-gray-900 dark:text-white`}>
                              {notification.title}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                              {notification.time}
                            </p>
                          </div>
                          {!notification.read && (
                            <div className="flex-shrink-0 ml-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  markAsRead(notification.id)
                                }}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                  <button className="w-full text-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                    View all notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className={`group flex items-center ${isRTL ? 'space-x-reverse' : ''} space-x-3 text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-white focus:outline-none p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200`}
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                <span className="text-white font-bold text-sm">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-semibold">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {user?.role || 'Role'}
                </p>
              </div>
              <ChevronDown className="h-4 w-4" />
            </button>

            {/* User dropdown menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                <a
                  href="#"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <User className={`h-4 w-4 ${isRTL ? 'ml-3' : 'mr-3'}`} />
                  {t.yourProfile}
                </a>
                <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                <button
                  className="w-full text-left flex items-center px-4 py-2 text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => {
                    setShowUserMenu(false)
                    // Handle logout will be handled by sidebar
                  }}
                >
                  {t.signOut}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
