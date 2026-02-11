import React from 'react';
import { } from '@tremor/react';
import MessageBubble from './MessageBubble';

interface IncidentAIConversationProps {
  aiConversation: any;
}

const IncidentAIConversation: React.FC<IncidentAIConversationProps> = ({ aiConversation }) => {
  const getBubbleClass = (sender: string) => {
    return sender === 'user-message'
      ? 'bg-blue-50 border border-blue-200 text-slate-900 self-end rounded-md shadow-sm'
      : 'bg-slate-100 border border-slate-300 text-slate-900 self-start rounded-md shadow-sm';
  };

  const renderConversation = () => {
    if (!aiConversation) {
      return (
        <div className="flex flex-col items-center justify-center h-96 text-slate-600">
          <i className="fas fa-robot text-4xl mb-4 text-slate-400"></i>
          <p className="text-center font-medium">No hay conversación registrada con el asistente de IA.</p>
          <p className="text-sm text-center mt-2 text-slate-500">Inicia una conversación para obtener ayuda con la descripción del incidente.</p>
        </div>
      );
    }

    let messages: any[] = [];
    try {
      // First, try to parse it as JSON
      messages = JSON.parse(aiConversation);
    } catch (e) {
      // If it fails, assume it's the plain text format and parse it manually
      try {
        messages = aiConversation.split('\n').filter(Boolean).map((line: string) => {
          if (line.startsWith('[IA]:')) {
            return { sender: 'ai-message', text: line.replace('[IA]:', '').trim() };
          } else if (line.startsWith('[USUARIO]:')) {
            return { sender: 'user-message', text: line.replace('[USUARIO]:', '').trim() };
          }
          return { sender: 'unknown', text: line }; // Fallback for unknown lines
        });
      } catch (error) {
        console.error('Error parsing AI conversation:', error);
        return <p className="text-red-500 text-center p-4">Error al cargar la conversación.</p>;
      }
    }

    try {
      return messages
        .filter((msg: any) => msg.sender === 'user-message' || msg.sender === 'ai-message')
        .map((msg: any, index: number) => (
          <div key={index} className={`w-full flex ${msg.sender === 'user-message' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-md p-3 rounded-lg ${getBubbleClass(msg.sender)}`}>
              <MessageBubble markdownContent={msg.text || ''} />
            </div>
          </div>
        ));
    } catch (error) {
      console.error('Error rendering conversation messages:', error);
      return <p className="text-red-500 text-center p-4">Error al mostrar los mensajes de la conversación.</p>;
    }
  };

  return (
    <div className="bg-white rounded-md p-4 h-96 flex flex-col border border-slate-200">
      <div className="flex-1 overflow-y-auto space-y-3 flex flex-col">
        {renderConversation()}
      </div>
    </div>
  );
};

export default IncidentAIConversation;
