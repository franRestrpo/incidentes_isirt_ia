export interface User {
  user_id?: number;
  full_name: string;
  email: string;
  position?: string;
  city?: string;
  role: string;
  group_id?: number;
  is_active: boolean;
  last_activity?: string; // ISO date string
  deactivation_reason?: string;
  auto_deactivated?: boolean;
  created_at?: string;
}

export interface Group {
  id: number;
  name: string;
}
