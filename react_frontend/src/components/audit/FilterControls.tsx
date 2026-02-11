import { Grid, TextInput, DateRangePicker } from '@tremor/react';
import type { DateRangePickerValue } from '@tremor/react';
import type { AuditLogFilters } from '../../schemas/audit_log';

interface FilterControlsProps {
  onFilterChange: (filters: Partial<AuditLogFilters>) => void;
}

const FilterControls = ({ onFilterChange }: FilterControlsProps) => {

  const handleDateRangeChange = (value: DateRangePickerValue) => {
    onFilterChange({
      start_date: value.from ? value.from.toISOString() : undefined,
      end_date: value.to ? value.to.toISOString() : undefined,
    });
  };

  return (
    <Grid numItemsSm={2} numItemsLg={4} className="gap-6">
      <TextInput
        placeholder="Filter by User ID..."
        onChange={(e) => onFilterChange({ user_id: e.target.value ? Number(e.target.value) : undefined })}
      />
      <TextInput
        placeholder="Filter by Action..."
        onChange={(e) => onFilterChange({ action: e.target.value })}
      />
      <TextInput
        placeholder="Filter by Resource Type..."
        onChange={(e) => onFilterChange({ resource_type: e.target.value })}
      />
      <DateRangePicker
        className="mx-auto max-w-sm"
        onValueChange={handleDateRangeChange}
        placeholder="Filter by date range..."
      />
    </Grid>
  );
};

export default FilterControls;
