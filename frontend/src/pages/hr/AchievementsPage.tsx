import { useState } from 'react'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2,
  Award,
  Medal,
  Star,
  Trophy,
  Target,
  Calendar,
  TrendingUp,
  CheckCircle
} from 'lucide-react'

interface Achievement {
  id: string | number
  title: string
  description: string
  category: 'performance' | 'milestone' | 'recognition' | 'skill' | 'project'
  employee_id: string
  employee_name: string
  department: string
  date_achieved: string
  points?: number
  level: 'bronze' | 'silver' | 'gold' | 'platinum'
  badge_url?: string
  verified_by: string
  is_public: boolean
  created_at: string
  updated_at?: string
}

// Mock data for achievements
const mockAchievements: Achievement[] = [
  {
    id: 1,
    title: 'Top Sales Performer Q4 2023',
    description: 'Exceeded quarterly sales target by 125% and brought in 15 new major clients',
    category: 'performance',
    employee_id: 'EMP-001',
    employee_name: 'Ahmed Al-Rashid',
    department: 'Sales',
    date_achieved: '2023-12-31',
    points: 500,
    level: 'gold',
    verified_by: 'Sarah Johnson',
    is_public: true,
    created_at: '2024-01-05T10:00:00Z'
  },
  {
    id: 2,
    title: 'Project Leadership Excellence',
    description: 'Successfully led the digital transformation project, delivered on time and under budget',
    category: 'project',
    employee_id: 'EMP-002',
    employee_name: 'Sarah Johnson',
    department: 'IT',
    date_achieved: '2023-11-15',
    points: 750,
    level: 'platinum',
    verified_by: 'Michael Smith',
    is_public: true,
    created_at: '2023-11-16T14:30:00Z'
  },
  {
    id: 3,
    title: '5 Years of Service',
    description: 'Celebrating 5 years of dedicated service and commitment to the company',
    category: 'milestone',
    employee_id: 'EMP-003',
    employee_name: 'Michael Smith',
    department: 'Marketing',
    date_achieved: '2023-10-20',
    points: 300,
    level: 'silver',
    verified_by: 'HR Team',
    is_public: true,
    created_at: '2023-10-20T09:15:00Z'
  },
  {
    id: 4,
    title: 'Customer Service Excellence',
    description: 'Achieved 98% customer satisfaction rating for 6 consecutive months',
    category: 'recognition',
    employee_id: 'EMP-004',
    employee_name: 'Fatima Al-Zahra',
    department: 'HR',
    date_achieved: '2023-09-30',
    points: 400,
    level: 'gold',
    verified_by: 'Customer Experience Manager',
    is_public: true,
    created_at: '2023-10-01T11:45:00Z'
  },
  {
    id: 5,
    title: 'Advanced Financial Analysis Certification',
    description: 'Completed advanced certification in financial analysis and reporting',
    category: 'skill',
    employee_id: 'EMP-005',
    employee_name: 'Omar Ibrahim',
    department: 'Finance',
    date_achieved: '2023-08-22',
    points: 250,
    level: 'bronze',
    verified_by: 'Finance Director',
    is_public: true,
    created_at: '2023-08-22T16:20:00Z'
  },
  {
    id: 6,
    title: 'Innovation Award',
    description: 'Developed an innovative solution that improved operational efficiency by 30%',
    category: 'recognition',
    employee_id: 'EMP-002',
    employee_name: 'Sarah Johnson',
    department: 'IT',
    date_achieved: '2023-07-10',
    points: 600,
    level: 'platinum',
    verified_by: 'CTO',
    is_public: true,
    created_at: '2023-07-11T08:30:00Z'
  }
]

export function AchievementsPage() {
  const [achievements] = useState<Achievement[]>(mockAchievements)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')

  // Filter achievements based on search and filters
  const filteredAchievements = achievements.filter(achievement => {
    const matchesSearch = 
      achievement.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      achievement.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      achievement.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      achievement.description.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = selectedCategory === 'all' || achievement.category === selectedCategory
    const matchesLevel = selectedLevel === 'all' || achievement.level === selectedLevel
    
    return matchesSearch && matchesCategory && matchesLevel
  })

  // Statistics
  const stats = {
    total: achievements.length,
    thisMonth: achievements.filter(achievement => {
      const achievementDate = new Date(achievement.date_achieved)
      const now = new Date()
      return achievementDate.getMonth() === now.getMonth() && 
             achievementDate.getFullYear() === now.getFullYear()
    }).length,
    totalPoints: achievements.reduce((sum, achievement) => sum + (achievement.points || 0), 0),
    categories: [...new Set(achievements.map(achievement => achievement.category))].length
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'platinum': return <Trophy className="h-5 w-5 text-purple-600" />
      case 'gold': return <Medal className="h-5 w-5 text-yellow-600" />
      case 'silver': return <Award className="h-5 w-5 text-gray-600" />
      case 'bronze': return <Star className="h-5 w-5 text-amber-600" />
      default: return <Star className="h-5 w-5 text-gray-600" />
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'platinum': return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'gold': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'silver': return 'bg-gray-100 text-gray-800 border-gray-200'
      case 'bronze': return 'bg-amber-100 text-amber-800 border-amber-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'performance': return <TrendingUp className="h-4 w-4" />
      case 'milestone': return <Calendar className="h-4 w-4" />
      case 'recognition': return <Award className="h-4 w-4" />
      case 'skill': return <Target className="h-4 w-4" />
      case 'project': return <CheckCircle className="h-4 w-4" />
      default: return <Star className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Employee Achievements</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Track and celebrate employee accomplishments, milestones, and recognition
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Achievement
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Total Achievements</CardTitle>
            <Trophy className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">{stats.total}</div>
            <p className="text-xs text-purple-600 dark:text-purple-400">All time records</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">This Month</CardTitle>
            <Calendar className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.thisMonth}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400">New achievements</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-700 dark:text-yellow-300">Total Points</CardTitle>
            <Medal className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">{stats.totalPoints.toLocaleString()}</div>
            <p className="text-xs text-yellow-600 dark:text-yellow-400">Points earned</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Categories</CardTitle>
            <Target className="h-4 w-4 text-green-600 dark:text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">{stats.categories}</div>
            <p className="text-xs text-green-600 dark:text-green-400">Achievement types</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search achievements, employees, or departments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-4">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Categories</option>
                <option value="performance">Performance</option>
                <option value="milestone">Milestone</option>
                <option value="recognition">Recognition</option>
                <option value="skill">Skill</option>
                <option value="project">Project</option>
              </select>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Levels</option>
                <option value="bronze">Bronze</option>
                <option value="silver">Silver</option>
                <option value="gold">Gold</option>
                <option value="platinum">Platinum</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Achievements List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAchievements.map((achievement) => (
          <Card key={achievement.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  {getLevelIcon(achievement.level)}
                  <div>
                    <CardTitle className="text-lg">{achievement.title}</CardTitle>
                    <CardDescription className="text-sm">
                      {achievement.employee_name} • {achievement.department}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getLevelColor(achievement.level)}`}>
                    {achievement.level.charAt(0).toUpperCase() + achievement.level.slice(1)}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                  {achievement.description}
                </p>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-gray-500">
                    {getCategoryIcon(achievement.category)}
                    <span className="capitalize">{achievement.category}</span>
                  </div>
                  {achievement.points && (
                    <div className="flex items-center gap-1 text-yellow-600">
                      <Star className="h-4 w-4" />
                      <span className="font-medium">{achievement.points} pts</span>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>{new Date(achievement.date_achieved).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-4 w-4" />
                    <span>Verified by {achievement.verified_by}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-end gap-2 pt-2 border-t">
                  <Button variant="outline" size="sm" className="flex items-center gap-1">
                    <Edit className="h-3 w-3" />
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" className="flex items-center gap-1 text-red-600 hover:text-red-700">
                    <Trash2 className="h-3 w-3" />
                    Delete
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAchievements.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No achievements found</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {searchQuery || selectedCategory !== 'all' || selectedLevel !== 'all'
                ? 'Try adjusting your search criteria or filters.'
                : 'Start recognizing employee achievements to see them here.'}
            </p>
            <Button className="flex items-center gap-2 mx-auto">
              <Plus className="h-4 w-4" />
              Add First Achievement
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
