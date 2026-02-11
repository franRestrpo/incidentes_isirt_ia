export interface AuditLogInDB {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id?: number | null;
  details?: Record<string, any> | null;
  ip_address?: string | null;
  user_agent?: string | null;
  success: boolean;
  timestamp: string; // ISO 8601 date string
}

export interface PaginatedAuditLogs {
  total: number;
  logs: AuditLogInDB[];
}

export interface AuditLogFilters {
  skip?: number;
  limit?: number;
  user_id?: number;
  action?: string;
  resource_type?: string;
  start_date?: string; // ISO 8601 format
  end_date?: string; // ISO 8601 format
}
