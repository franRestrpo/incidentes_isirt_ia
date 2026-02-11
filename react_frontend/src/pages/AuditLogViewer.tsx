import { useState, useEffect, useCallback } from 'react';
import { Card, Title, Text } from '@tremor/react';
import { useAuth } from '../context/AuthContext'; // Corrected path
import { apiService } from '../services/apiService';
import type { PaginatedAuditLogs, AuditLogFilters } from '../schemas/audit_log';
import AuditLogTable from '../components/audit/AuditLogTable';
import FilterControls from '../components/audit/FilterControls';
import { debounce } from 'lodash';

const AuditLogViewer = () => {
  const { currentUser } = useAuth(); // No need for token, apiService handles it
  const [data, setData] = useState<PaginatedAuditLogs>({ logs: [], total: 0 });
  const [filters, setFilters] = useState<AuditLogFilters>({ skip: 0, limit: 20 });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(debounce(async (currentFilters: AuditLogFilters) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiService.getAuditLogs(currentFilters);
      setData(result);
    } catch (err) {
      setError('Failed to fetch audit logs. Please try again later.');
      console.error(err);
    }
    setIsLoading(false);
  }, 300), []);

  useEffect(() => {
    // Fetch data only when filters change and user is loaded
    if (currentUser) {
      fetchData(filters);
    }
  }, [filters, currentUser, fetchData]);

  const handleFilterChange = (newFilters: Partial<AuditLogFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, skip: 0 })); // Reset skip on filter change
  };

  const handlePageChange = (newSkip: number) => {
    setFilters(prev => ({ ...prev, skip: newSkip }));
  };

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <Title>Audit Logs</Title>
      <Text>Review all actions performed within the system.</Text>

      <Card className="mt-6">
        <FilterControls onFilterChange={handleFilterChange} />
        <AuditLogTable
          logs={data.logs}
          totalRecords={data.total}
          filters={filters}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />
        {error && <Text className="text-red-500 mt-4">{error}</Text>}
      </Card>
    </main>
  );
};

export default AuditLogViewer;
