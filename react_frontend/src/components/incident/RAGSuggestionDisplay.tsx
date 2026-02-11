/**
 * Component to display RAG suggestions with traceability and curation actions.
 */
import React from 'react';
import { Card, Title, Text, Badge, Button, Accordion, AccordionHeader, AccordionBody } from '@tremor/react';
import type { RAGSuggestion } from '../../types/ai'; // Assuming types are in ai.ts
import { apiService } from '../../services/apiService';

interface RAGSuggestionDisplayProps {
  ragSuggestion: RAGSuggestion;
}

const RAGSuggestionDisplay: React.FC<RAGSuggestionDisplayProps> = ({ ragSuggestion }) => {

  const handleFlagChunk = async (sourceName: string, chunkId: string) => {
    const notes = prompt("Por favor, introduce una breve nota sobre por qué esta fuente es incorrecta:");
    if (notes === null) return; // User cancelled

    try {
      // This needs an apiService function
      await apiService.flagKnowledgeChunk({ source_name: sourceName, chunk_id: chunkId, notes });
      alert(`Fuente marcada para revisión: ${sourceName} (${chunkId})`);
    } catch (error) {
      console.error("Error flagging knowledge chunk:", error);
      alert("Error al marcar la fuente para revisión.");
    }
  };

  const getConfidenceColor = (level: string) => {
    if (level === 'Alta') return 'emerald';
    if (level === 'Media') return 'yellow';
    return 'red';
  };

  if (!ragSuggestion) {
    return null;
  }

  return (
    <Card className="mt-6">
      <div className="flex justify-between items-start">
        <Title>Sugerencia de Análisis (Potenciada por RAG)</Title>
        <div className="flex items-center gap-2">
          <Text>Nivel de Confianza:</Text>
          <Badge color={getConfidenceColor(ragSuggestion.confidence_level)}>
            {ragSuggestion.confidence_level}
          </Badge>
        </div>
      </div>
      
      <Text className="mt-2 mb-4">{ragSuggestion.suggestion_text}</Text>

      <Accordion>
        <AccordionHeader>Ver Fuentes ({ragSuggestion.sources.length})</AccordionHeader>
        <AccordionBody>
          <div className="space-y-4 mt-2">
            {ragSuggestion.sources.map((source, index) => (
              <div key={index} className="p-3 border rounded-md bg-slate-50">
                <div className="flex justify-between items-center">
                  <p className="text-sm font-medium text-slate-700">
                    Fuente: {source.source_name} (v{source.source_version || 'N/A'})
                  </p>
                  <div className="flex items-center gap-x-3">
                     <Badge color="gray">Score: {source.confidence_score.toFixed(2)}</Badge>
                     <Button 
                        size="xs" 
                        variant="secondary" 
                        color="red"
                        onClick={() => handleFlagChunk(source.source_name, source.chunk_id)} // Placeholder for chunk_id
                        icon={() => <i className="fas fa-flag mr-1"></i>}
                     >
                        Marcar
                     </Button>
                  </div>
                </div>
                <p className="text-xs text-slate-600 mt-2 p-2 border-t border-slate-200">{source.content}</p>
              </div>
            ))}
          </div>
        </AccordionBody>
      </Accordion>
    </Card>
  );
};

export default RAGSuggestionDisplay;
