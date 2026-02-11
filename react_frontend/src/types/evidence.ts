/**
 * Types for Evidence Files.
 */

export interface EvidenceFile {
  file_id: number;
  file_name: string;
  file_path: string;
  file_type: string;
  file_size_bytes: number;
  file_hash?: string; // Make it optional for now to avoid breaking old data
  uploaded_at: string;
}
