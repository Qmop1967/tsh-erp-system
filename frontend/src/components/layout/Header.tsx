import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'
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
  ChevronDown 
} from 'lucide-react'

export function Header() {
  const [darkMode, setDarkMode] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const { user } = useAuthStore()
  const { language, isRTL } = useLanguageStore()
  const t = useTranslations(language)

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

          {/* Notifications */}
          <Button
            variant="ghost"
            size="icon"
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 relative hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse shadow-lg">
              3
            </span>
          </Button>

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
                <a
                  href="#"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Settings className={`h-4 w-4 ${isRTL ? 'ml-3' : 'mr-3'}`} />
                  {t.settings}
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
