import { Construction } from 'lucide-react';

interface ComingSoonPageProps {
  title: string;
  description?: string;
}

export function ComingSoonPage({ title, description }: ComingSoonPageProps) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div className="mx-auto w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mb-6">
          <Construction className="w-12 h-12 text-blue-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">{title}</h1>
        <p className="text-lg text-gray-600 mb-8">
          {description || 'This feature is under construction and will be available soon.'}
        </p>
        <div className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-medium">
          Coming Soon
        </div>
      </div>
    </div>
  );
}
