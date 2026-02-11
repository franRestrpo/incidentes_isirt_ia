import React, { useRef, useEffect } from 'react';
import { Textarea, Button } from '@tremor/react';

interface Message {
  sender: 'user-message' | 'ai-message' | 'ai-status-message';
  text: string;
}

interface ChatWindowProps {
  chatHistory: Message[];
  userInput: string;
  setUserInput: (input: string) => void;
  isAiTyping: boolean;
  onSendMessage: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  chatHistory,
  userInput,
  setUserInput,
  isAiTyping,
  onSendMessage
}) => {
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const getBubbleClass = (sender: Message['sender']) => {
    switch (sender) {
      case 'user-message':
        return 'bg-slate-100 border border-slate-300 text-slate-700 self-end rounded-md shadow-sm';
      case 'ai-message':
        return 'bg-teal-50 border border-teal-200 text-teal-800 self-start rounded-md shadow-sm';
      case 'ai-status-message':
        return 'bg-slate-50 border border-slate-200 text-slate-500 self-center text-sm rounded-md';
      default:
        return '';
    }
  };

  return (
    <fieldset className="rounded-lg border p-4">
      <legend className="text-lg font-semibold text-slate-800 px-2">Parte I: Converse con SecBot</legend>
      <div className="flex flex-col h-96 bg-white rounded-md p-2">
        <div ref={chatHistoryRef} className="flex-1 overflow-y-auto p-2 space-y-3">
          {chatHistory.map((message, index) => (
            <div key={index} className={`w-full flex ${message.sender === 'user-message' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs md:max-w-md p-3 rounded-lg ${getBubbleClass(message.sender)}`}>
                {message.text}
              </div>
            </div>
          ))}
          {isAiTyping && (
            <div className={`w-full flex justify-start`}>
              <div className={`max-w-xs md:max-w-md p-3 rounded-lg ${getBubbleClass('ai-message')}`}>
                <div className="flex items-center space-x-2">
                  <span className="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="h-2 w-2 bg-white rounded-full animate-bounce"></span>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center p-2 border-t">
          <Textarea
            value={userInput}
            onValueChange={setUserInput}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                onSendMessage();
              }
            }}
            placeholder="Escribe tu respuesta aquí..."
            rows={2}
            disabled={isAiTyping}
            className="flex-1"
          />
          <Button
            onClick={onSendMessage}
            disabled={isAiTyping || !userInput.trim()}
            className="ml-2"
          >
            <i className="fas fa-paper-plane"></i>
          </Button>
        </div>
      </div>
    </fieldset>
  );
};

export default ChatWindow;
