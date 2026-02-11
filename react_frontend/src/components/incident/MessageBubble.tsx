import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

interface MessageBubbleProps {
  markdownContent: string;
}

/**
 * Componente que renderiza de forma segura contenido Markdown a HTML.
 * Maneja la conversión asíncrona de `marked` y la sanitización con `DOMPurify`.
 */
const MessageBubble: React.FC<MessageBubbleProps> = ({ markdownContent }) => {
  const [html, setHtml] = useState('');

  useEffect(() => {
    const translateMarkdown = async () => {
      if (!markdownContent) {
        setHtml('');
        return;
      }
      // La función `marked` es asíncrona
      const rawHtml = await marked(markdownContent);
      setHtml(DOMPurify.sanitize(rawHtml));
    };

    translateMarkdown();
  }, [markdownContent]);

  return <div dangerouslySetInnerHTML={{ __html: html }} />;
};

export default MessageBubble;
