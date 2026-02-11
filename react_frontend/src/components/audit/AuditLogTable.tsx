import { useState } from 'react';
import { 
  Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell,
  Badge, Button, Card, Flex, Text, Title, Dialog, DialogPanel
} from '@tremor/react';
import type { AuditLogInDB } from '../../schemas/audit_log';
import type { AuditLogFilters } from '../../schemas/audit_log';

interface AuditLogTableProps {
  logs: AuditLogInDB[];
  totalRecords: number;
  filters: AuditLogFilters;
  onPageChange: (newSkip: number) => void;
  isLoading: boolean;
}

const AuditLogTable = ({
  logs,
  totalRecords,
  filters,
  onPageChange,
  isLoading,
}: AuditLogTableProps) => {
  const [selectedLog, setSelectedLog] = useState<AuditLogInDB | null>(null);

  const { skip = 0, limit = 20 } = filters;
  const totalPages = Math.ceil(totalRecords / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  const handlePrevPage = () => {
    if (skip > 0) {
      onPageChange(skip - limit);
    }
  };

  const handleNextPage = () => {
    if (skip + limit < totalRecords) {
      onPageChange(skip + limit);
    }
  };

  const renderDetails = (details: Record<string, any> | null | undefined) => {
    if (!details) return <Text>No details available.</Text>;

    // Special rendering for 'changes'
    if (details.changes) {
      return (
        <div>
          <Title>Changes</Title>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <Text>Old Values</Text>
              <pre className="text-xs bg-gray-100 p-2 rounded mt-1">{JSON.stringify(details.changes.old_values, null, 2)}</pre>
            </div>
            <div>
              <Text>New Values</Text>
              <pre className="text-xs bg-gray-100 p-2 rounded mt-1">{JSON.stringify(details.changes.new_values, null, 2)}</pre>
            </div>
          </div>
        </div>
      );
    }

    return <pre className="text-xs bg-gray-100 p-2 rounded">{JSON.stringify(details, null, 2)}</pre>;
  };

  return (
    <Card className="mt-6">
      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell>Timestamp</TableHeaderCell>
            <TableHeaderCell>User ID</TableHeaderCell>
            <TableHeaderCell>Action</TableHeaderCell>
            <TableHeaderCell>Resource</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Details</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <TableRow><TableCell colSpan={6} className="text-center">Loading...</TableCell></TableRow>
          ) : logs.length > 0 ? (
            logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                <TableCell>{log.user_id}</TableCell>
                <TableCell>{log.action}</TableCell>
                <TableCell>{log.resource_type}{log.resource_id ? ` (${log.resource_id})` : ''}</TableCell>
                <TableCell>
                  <Badge color={log.success ? 'emerald' : 'rose'}>
                    {log.success ? 'Success' : 'Failure'}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Button size="xs" variant="secondary" onClick={() => setSelectedLog(log)}>
                    View Details
                  </Button>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow><TableCell colSpan={6} className="text-center">No records found.</TableCell></TableRow>
          )}
        </TableBody>
      </Table>

      {/* Pagination Controls */}
      <Flex justifyContent="between" className="mt-4">
        <Text>
          Showing {Math.min(skip + 1, totalRecords)} to {Math.min(skip + limit, totalRecords)} of {totalRecords} records
        </Text>
        <Flex justifyContent="end" className="space-x-2">
          <Button onClick={handlePrevPage} disabled={currentPage <= 1 || isLoading}>Previous</Button>
          <Text>Page {currentPage} of {totalPages}</Text>
          <Button onClick={handleNextPage} disabled={currentPage >= totalPages || isLoading}>Next</Button>
        </Flex>
      </Flex>

      {/* Details Modal */}
      <Dialog open={selectedLog !== null} onClose={() => setSelectedLog(null)} static={true}>
        <DialogPanel>
          <Title className="mb-4">Audit Log Details (ID: {selectedLog?.id})</Title>
          {renderDetails(selectedLog?.details)}
          <div className="mt-6">
            <Button variant="secondary" onClick={() => setSelectedLog(null)}>Close</Button>
          </div>
        </DialogPanel>
      </Dialog>
    </Card>
  );
};

export default AuditLogTable;
