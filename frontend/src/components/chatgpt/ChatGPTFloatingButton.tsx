import React, { useState } from 'react';
import ChatGPTModal from './ChatGPTModal';

export const ChatGPTFloatingButton: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsChatOpen(true)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          cursor: 'pointer',
          boxShadow: isHovered 
            ? '0 15px 40px rgba(102, 126, 234, 0.6)' 
            : '0 10px 30px rgba(102, 126, 234, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          transition: 'all 0.3s ease',
          color: 'white',
          transform: isHovered ? 'scale(1.1)' : 'scale(1)',
        }}
        title="Chat with AI Assistant"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="28" 
          height="28" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        
        {/* Pulse Animation */}
        <span
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            opacity: 0.6,
            animation: 'pulse 2s infinite',
          }}
        />
      </button>

      {/* Tooltip */}
      {isHovered && (
        <div
          style={{
            position: 'fixed',
            bottom: '30px',
            right: '100px',
            backgroundColor: '#1f2937',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: 1001,
          }}
        >
          💬 Chat with AI Assistant
        </div>
      )}

      {/* Chat Modal */}
      <ChatGPTModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

      {/* Pulse Animation Keyframes */}
      <style>{`
        @keyframes pulse {
          0% {
            transform: scale(1);
            opacity: 0.6;
          }
          50% {
            transform: scale(1.1);
            opacity: 0.3;
          }
          100% {
            transform: scale(1);
            opacity: 0.6;
          }
        }
      `}</style>
    </>
  );
};

export default ChatGPTFloatingButton;
