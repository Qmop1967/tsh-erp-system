import { cn } from '@/lib/utils'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  text?: string
}

export function Loading({ size = 'md', className, text }: LoadingProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className={cn('flex flex-col items-center justify-center space-y-4', className)}>
      <div className="relative">
        <div className={cn(
          'border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin',
          sizeClasses[size]
        )}></div>
        <div className={cn(
          'absolute top-0 left-0 border-4 border-transparent border-t-purple-500 rounded-full animate-spin',
          sizeClasses[size]
        )} style={{ animationDirection: 'reverse', animationDuration: '0.8s' }}></div>
      </div>
      {text && (
        <p className="text-sm text-gray-600 animate-pulse">{text}</p>
      )}
    </div>
  )
}

export function LoadingSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('animate-pulse', className)}>
      <div className="bg-gray-200 rounded-lg h-4 mb-3"></div>
      <div className="bg-gray-200 rounded-lg h-4 mb-3 w-3/4"></div>
      <div className="bg-gray-200 rounded-lg h-4 w-1/2"></div>
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-white rounded-xl p-6 shadow-md animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="bg-gray-200 rounded h-4 w-24"></div>
        <div className="bg-gray-200 rounded-lg w-10 h-10"></div>
      </div>
      <div className="bg-gray-200 rounded h-8 w-16 mb-2"></div>
      <div className="bg-gray-200 rounded h-4 w-20"></div>
    </div>
  )
}
