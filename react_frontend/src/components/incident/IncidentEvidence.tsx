import React from 'react';
import { Card, Title, Text, Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell, Button } from '@tremor/react';
import type { EvidenceFile } from '../../types/evidence';

interface IncidentEvidenceProps {
  incidentId: number;
  evidenceFiles?: EvidenceFile[];
}

const IncidentEvidence: React.FC<IncidentEvidenceProps> = ({ incidentId, evidenceFiles }) => {
  const hasEvidence = evidenceFiles && evidenceFiles.length > 0;

  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <Card>
      <Title>Parte IV: Evidencia Adjunta</Title>
      <div className="mt-4">
        {hasEvidence ? (
          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>Nombre del Archivo</TableHeaderCell>
                <TableHeaderCell>Tamaño</TableHeaderCell>
                <TableHeaderCell>Hash (SHA-256)</TableHeaderCell>
                <TableHeaderCell>Acción</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {evidenceFiles.map((file) => (
                <TableRow key={file.file_id}>
                  <TableCell>{file.file_name}</TableCell>
                  <TableCell>{formatBytes(file.file_size_bytes)}</TableCell>
                  <TableCell><Text className="truncate font-mono text-xs">{file.file_hash || 'N/A'}</Text></TableCell>
                  <TableCell>
                    <a
                      href={`/api/v1/incidents/${incidentId}/evidence/${file.file_id}/download`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button size="xs" variant="secondary">Descargar</Button>
                    </a>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <Text className="italic text-center p-4">No hay evidencia adjunta.</Text>
        )}
      </div>
    </Card>
  );
};

export default IncidentEvidence;
