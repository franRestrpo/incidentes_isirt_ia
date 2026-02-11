/**
 * Types for the User Cross-Reference feature.
 */

// A base incident type, can be expanded as needed
export interface Incident {
    id: number;
    title: string;
    status: string;
}

export interface ActivityLogItem {
    log_id: number;
    incident_id: number;
    action: string;
    comments?: string;
    timestamp: string; // ISO date string
}

export interface HistoryLogItem {
    history_id: number;
    incident_id: number;
    field_changed: string;
    old_value?: string;
    new_value?: string;
    timestamp: string; // ISO date string
}

export interface UserActivityMetrics {
    user_id: number;
    full_name: string;
    email: string;
    role: string;
    is_active: boolean;
    total_incidents_created: number;
    total_incidents_resolved: number;
    total_incidents_assigned: number;
    last_login?: string; // ISO date string
    top_incident_types: string[];
    average_resolution_time_hours?: number;
    incidents_by_status: Record<string, number>;
    login_frequency_per_week?: number;
    total_comments_made: number;
    total_files_uploaded: number;
}

export interface IncidentRelationship extends Incident {
    relationship_type: string;
}

export interface UserCrossReferenceResponse {
    metrics: UserActivityMetrics;
    incidents: IncidentRelationship[];
    activity_logs: ActivityLogItem[];
    history_logs: HistoryLogItem[];
}
