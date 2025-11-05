import React, { useState } from 'react';
import { MessageSquare } from 'lucide-react';

interface ChatGPTButtonProps {
  onOpenChat: () => void;
}

export const ChatGPTButton: React.FC<ChatGPTButtonProps> = ({ onOpenChat }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onOpenChat}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 z-50 hover:scale-110"
      title="AI Assistant"
    >
      <MessageSquare className="w-6 h-6" />
      {isHovered && (
        <span className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 bg-gray-900 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap">
          AI Assistant
        </span>
      )}
    </button>
  );
};

export default ChatGPTButton;
