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
  Target,
  Trophy,
  Users,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  TrendingUp,
  Award,
  Zap,
  BookOpen,
  Briefcase
} from 'lucide-react'

interface Challenge {
  id: string | number
  title: string
  description: string
  category: 'skill_development' | 'performance' | 'team_building' | 'innovation' | 'wellness'
  type: 'individual' | 'team' | 'department'
  difficulty: 'easy' | 'medium' | 'hard'
  points_reward: number
  start_date: string
  end_date: string
  status: 'draft' | 'active' | 'completed' | 'cancelled'
  participants_count: number
  completed_count: number
  created_by: string
  requirements: string[]
  prize_description?: string
  is_featured: boolean
  created_at: string
  updated_at?: string
}

// Mock data for challenges
const mockChallenges: Challenge[] = [
  {
    id: 1,
    title: 'Monthly Sales Excellence Challenge',
    description: 'Achieve 110% of your monthly sales target and win exciting rewards. Top 3 performers get special recognition.',
    category: 'performance',
    type: 'individual',
    difficulty: 'medium',
    points_reward: 500,
    start_date: '2024-01-01',
    end_date: '2024-01-31',
    status: 'active',
    participants_count: 12,
    completed_count: 3,
    created_by: 'Sales Manager',
    requirements: [
      'Achieve 110% of monthly target',
      'Maintain customer satisfaction above 90%',
      'Complete sales training module'
    ],
    prize_description: 'Gift voucher worth $500 and performance certificate',
    is_featured: true,
    created_at: '2023-12-28T10:00:00Z'
  },
  {
    id: 2,
    title: 'Digital Skills Mastery',
    description: 'Complete advanced digital skills training and earn certification. Boost your career with in-demand skills.',
    category: 'skill_development',
    type: 'individual',
    difficulty: 'hard',
    points_reward: 750,
    start_date: '2024-01-15',
    end_date: '2024-03-15',
    status: 'active',
    participants_count: 25,
    completed_count: 8,
    created_by: 'HR Department',
    requirements: [
      'Complete 40 hours of online training',
      'Pass certification exam with 85% score',
      'Present a project showcase'
    ],
    prize_description: 'Professional development budget of $1000',
    is_featured: true,
    created_at: '2024-01-10T14:30:00Z'
  },
  {
    id: 3,
    title: 'Team Innovation Sprint',
    description: 'Collaborate with your team to develop innovative solutions for workplace challenges. Best idea wins!',
    category: 'innovation',
    type: 'team',
    difficulty: 'hard',
    points_reward: 1000,
    start_date: '2024-02-01',
    end_date: '2024-02-28',
    status: 'active',
    participants_count: 18,
    completed_count: 0,
    created_by: 'Innovation Team',
    requirements: [
      'Form teams of 3-5 members',
      'Identify a workplace challenge',
      'Develop and present solution',
      'Create prototype or detailed plan'
    ],
    prize_description: 'Team lunch and innovation award',
    is_featured: false,
    created_at: '2024-01-25T09:15:00Z'
  },
  {
    id: 4,
    title: 'Wellness Week Challenge',
    description: 'Focus on your well-being with daily wellness activities. Track your progress and win health rewards.',
    category: 'wellness',
    type: 'individual',
    difficulty: 'easy',
    points_reward: 200,
    start_date: '2024-01-22',
    end_date: '2024-01-26',
    status: 'completed',
    participants_count: 45,
    completed_count: 38,
    created_by: 'Wellness Committee',
    requirements: [
      'Complete daily 30-minute exercise',
      'Log healthy meals for 5 days',
      'Practice mindfulness/meditation',
      'Share wellness tip with team'
    ],
    prize_description: 'Fitness tracker and wellness kit',
    is_featured: false,
    created_at: '2024-01-15T11:45:00Z'
  },
  {
    id: 5,
    title: 'Customer Experience Excellence',
    description: 'Deliver exceptional customer service and gather positive feedback. Help us exceed customer expectations.',
    category: 'performance',
    type: 'department',
    difficulty: 'medium',
    points_reward: 400,
    start_date: '2024-01-01',
    end_date: '2024-03-31',
    status: 'active',
    participants_count: 22,
    completed_count: 5,
    created_by: 'Customer Success Team',
    requirements: [
      'Achieve 95% customer satisfaction',
      'Reduce response time by 20%',
      'Complete customer service training',
      'Gather 5 positive testimonials'
    ],
    prize_description: 'Department celebration and recognition awards',
    is_featured: false,
    created_at: '2023-12-20T16:20:00Z'
  }
]

export function ChallengesPage() {
  const [challenges] = useState<Challenge[]>(mockChallenges)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [selectedType, setSelectedType] = useState<string>('all')

  // Filter challenges based on search and filters
  const filteredChallenges = challenges.filter(challenge => {
    const matchesSearch = 
      challenge.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      challenge.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      challenge.created_by.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = selectedCategory === 'all' || challenge.category === selectedCategory
    const matchesStatus = selectedStatus === 'all' || challenge.status === selectedStatus
    const matchesType = selectedType === 'all' || challenge.type === selectedType
    
    return matchesSearch && matchesCategory && matchesStatus && matchesType
  })

  // Statistics
  const stats = {
    total: challenges.length,
    active: challenges.filter(challenge => challenge.status === 'active').length,
    totalParticipants: challenges.reduce((sum, challenge) => sum + challenge.participants_count, 0),
    completionRate: Math.round(
      (challenges.reduce((sum, challenge) => sum + challenge.completed_count, 0) /
       challenges.reduce((sum, challenge) => sum + challenge.participants_count, 0)) * 100
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'completed': return <Trophy className="h-4 w-4 text-blue-600" />
      case 'cancelled': return <XCircle className="h-4 w-4 text-red-600" />
      case 'draft': return <AlertCircle className="h-4 w-4 text-yellow-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200'
      case 'completed': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-200'
      case 'draft': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800 border-green-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'hard': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'skill_development': return <BookOpen className="h-4 w-4" />
      case 'performance': return <TrendingUp className="h-4 w-4" />
      case 'team_building': return <Users className="h-4 w-4" />
      case 'innovation': return <Zap className="h-4 w-4" />
      case 'wellness': return <Briefcase className="h-4 w-4" />
      default: return <Target className="h-4 w-4" />
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'individual': return <Target className="h-4 w-4" />
      case 'team': return <Users className="h-4 w-4" />
      case 'department': return <Briefcase className="h-4 w-4" />
      default: return <Target className="h-4 w-4" />
    }
  }

  const getProgressPercentage = (completed: number, total: number) => {
    return total > 0 ? Math.round((completed / total) * 100) : 0
  }

  const isChallengeFeatured = (challenge: Challenge) => {
    return challenge.is_featured && challenge.status === 'active'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Employee Challenges</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Create and manage engaging challenges to motivate and develop your team
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Challenge
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Challenges</CardTitle>
            <Target className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.total}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400">All challenges</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Active Challenges</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">{stats.active}</div>
            <p className="text-xs text-green-600 dark:text-green-400">Currently running</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Total Participants</CardTitle>
            <Users className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">{stats.totalParticipants}</div>
            <p className="text-xs text-purple-600 dark:text-purple-400">All challenges</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-700 dark:text-yellow-300">Completion Rate</CardTitle>
            <Trophy className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">{stats.completionRate}%</div>
            <p className="text-xs text-yellow-600 dark:text-yellow-400">Average completion</p>
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
                  placeholder="Search challenges, descriptions, or creators..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-4">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Categories</option>
                <option value="skill_development">Skill Development</option>
                <option value="performance">Performance</option>
                <option value="team_building">Team Building</option>
                <option value="innovation">Innovation</option>
                <option value="wellness">Wellness</option>
              </select>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Types</option>
                <option value="individual">Individual</option>
                <option value="team">Team</option>
                <option value="department">Department</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Challenges List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredChallenges.map((challenge) => (
          <Card 
            key={challenge.id} 
            className={`hover:shadow-lg transition-shadow ${
              isChallengeFeatured(challenge) ? 'ring-2 ring-blue-500 ring-opacity-20' : ''
            }`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {isChallengeFeatured(challenge) && (
                      <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full border border-blue-200">
                        Featured
                      </span>
                    )}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(challenge.status)}`}>
                      {challenge.status.charAt(0).toUpperCase() + challenge.status.slice(1)}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(challenge.difficulty)}`}>
                      {challenge.difficulty.charAt(0).toUpperCase() + challenge.difficulty.slice(1)}
                    </span>
                  </div>
                  <CardTitle className="text-lg">{challenge.title}</CardTitle>
                  <CardDescription className="text-sm mt-1">
                    Created by {challenge.created_by}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(challenge.status)}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                  {challenge.description}
                </p>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-gray-500">
                    {getCategoryIcon(challenge.category)}
                    <span className="capitalize">{challenge.category.replace('_', ' ')}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500">
                    {getTypeIcon(challenge.type)}
                    <span className="capitalize">{challenge.type}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">
                      {new Date(challenge.start_date).toLocaleDateString()} - {new Date(challenge.end_date).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-yellow-600">
                    <Award className="h-4 w-4" />
                    <span className="font-medium">{challenge.points_reward} pts</span>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Progress</span>
                    <span className="text-gray-600">
                      {challenge.completed_count}/{challenge.participants_count} participants
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${getProgressPercentage(challenge.completed_count, challenge.participants_count)}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">
                    {getProgressPercentage(challenge.completed_count, challenge.participants_count)}% completion rate
                  </span>
                </div>

                {/* Requirements */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">Requirements:</h4>
                  <ul className="text-xs text-gray-600 dark:text-gray-300 space-y-1">
                    {challenge.requirements.slice(0, 2).map((req, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{req}</span>
                      </li>
                    ))}
                    {challenge.requirements.length > 2 && (
                      <li className="text-blue-600 hover:text-blue-700 cursor-pointer">
                        +{challenge.requirements.length - 2} more requirements...
                      </li>
                    )}
                  </ul>
                </div>

                {challenge.prize_description && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <Trophy className="h-4 w-4 text-yellow-600" />
                      <span className="text-sm font-medium text-yellow-800 dark:text-yellow-300">Prize:</span>
                    </div>
                    <p className="text-xs text-yellow-700 dark:text-yellow-400 mt-1">
                      {challenge.prize_description}
                    </p>
                  </div>
                )}
                
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

      {filteredChallenges.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No challenges found</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {searchQuery || selectedCategory !== 'all' || selectedStatus !== 'all' || selectedType !== 'all'
                ? 'Try adjusting your search criteria or filters.'
                : 'Create your first challenge to motivate and engage your team.'}
            </p>
            <Button className="flex items-center gap-2 mx-auto">
              <Plus className="h-4 w-4" />
              Create First Challenge
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
