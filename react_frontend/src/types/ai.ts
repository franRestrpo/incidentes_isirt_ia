/**
 * Types for AI-related data structures.
 */

export interface SourceFragment {
  source_name: string;
  source_version?: string;
  chunk_id: string; // Add chunk_id for curation
  content: string;
  confidence_score: number;
}

export interface RAGSuggestion {
  suggestion_text: string;
  confidence_level: string;
  sources: SourceFragment[];
}
