// ─── User ────────────────────────────────────────────────────────────────────
export type UserRole =
  | 'admin'
  | 'manager'
  | 'dispatcher'
  | 'shift_manager'
  | 'executor'
  | 'ppr_engineer';

export interface User {
  id: number;
  employee_number: string;
  full_name: string;
  email: string;
  role: UserRole;
  department?: string;
  phone?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

export interface UserShort {
  id: number;
  full_name: string;
  employee_number: string;
  role: UserRole;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

// ─── Equipment ───────────────────────────────────────────────────────────────
export type EquipmentStatus =
  | 'operational'
  | 'under_maintenance'
  | 'broken'
  | 'decommissioned';

export interface Equipment {
  id: number;
  name: string;
  inventory_number: string;
  equipment_type?: string;
  location?: string;
  department?: string;
  manufacturer?: string;
  model?: string;
  year_of_manufacture?: number;
  status: EquipmentStatus;
  created_at: string;
}

export interface EquipmentNorm {
  id: number;
  equipment_id: number;
  norm_type: string;
  interval_days: number;
  description?: string;
  is_active: boolean;
  created_at: string;
}

// ─── PPR ─────────────────────────────────────────────────────────────────────
export type PprTaskStatus =
  | 'planned'
  | 'in_progress'
  | 'completed'
  | 'overdue'
  | 'cancelled';

export interface PprSchedule {
  id: number;
  year: number;
  month: number;
  generated_at: string;
  generated_by_id: number;
  is_approved: boolean;
  approved_by_id?: number;
  approved_at?: string;
  generated_by?: UserShort;
  approved_by?: UserShort;
}

export interface PprTask {
  id: number;
  schedule_id: number;
  equipment_id: number;
  norm_id: number;
  planned_date: string;
  status: PprTaskStatus;
  request_id?: number;
  notes?: string;
  created_at: string;
  equipment?: Equipment;
  norm?: EquipmentNorm;
}

// ─── Request ─────────────────────────────────────────────────────────────────
export type RequestStatus =
  | 'new'
  | 'assigned'
  | 'in_progress'
  | 'waiting_parts'
  | 'completed'
  | 'closed'
  | 'cancelled';

export type RequestPriority = 'low' | 'medium' | 'high' | 'critical';
export type RequestType = 'unplanned' | 'ppr';

export interface FaultType {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuxiliaryService {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface StatusHistoryEntry {
  id: number;
  old_status?: string;
  new_status: string;
  changed_by?: UserShort;
  changed_at: string;
  comment?: string;
}

export interface Request {
  id: number;
  request_number: string;
  request_type: RequestType;
  title: string;
  description?: string;
  status: RequestStatus;
  priority: RequestPriority;
  equipment_id: number;
  fault_type_id?: number;
  service_id?: number;
  initiator_id: number;
  executor_id?: number;
  planned_start?: string;
  planned_end?: string;
  actual_start?: string;
  actual_end?: string;
  closed_at?: string;
  created_at: string;
  equipment?: Equipment;
  initiator?: UserShort;
  executor?: UserShort;
  fault_type?: FaultType;
}

export interface RequestDetail extends Request {
  status_history: StatusHistoryEntry[];
}

// ─── Work ────────────────────────────────────────────────────────────────────
export interface Diagnostic {
  id: number;
  request_id: number;
  performed_by_id: number;
  performed_at: string;
  findings: string;
  recommended_action?: string;
  estimated_repair_hours?: number;
  performed_by?: UserShort;
  created_at: string;
}

export interface RepairMaterial {
  id: number;
  name: string;
  quantity: number;
  unit?: string;
  cost?: number;
}

export interface Repair {
  id: number;
  request_id: number;
  performed_by_id: number;
  started_at: string;
  completed_at?: string;
  work_description: string;
  labor_hours?: number;
  result?: string;
  performed_by?: UserShort;
  materials: RepairMaterial[];
  created_at: string;
}

export interface Report {
  id: number;
  request_id: number;
  report_type: string;
  summary: string;
  recommendations?: string;
  created_by_id: number;
  created_by?: UserShort;
  created_at: string;
}

// ─── Analytics ───────────────────────────────────────────────────────────────
export interface DashboardStats {
  total_open_requests: number;
  critical_requests: number;
  overdue_ppr_tasks: number;
  equipment_broken: number;
  requests_by_status: { status: string; count: number }[];
  requests_by_priority: { priority: string; count: number }[];
  recent_activity: any[];
}

export interface AnalyticsReport {
  requests_by_status: { status: string; count: number }[];
  requests_by_priority: { priority: string; count: number }[];
  equipment_faults: { equipment_name: string; equipment_id: number; fault_count: number }[];
  service_performance: {
    service_name: string;
    service_id: number;
    total_requests: number;
    completed_requests: number;
    avg_completion_hours?: number;
  }[];
  ppr_completion_rate: number;
  monthly_requests: { month: string; count: number }[];
}

// ─── Routing Rules ───────────────────────────────────────────────────────────
export interface RoutingRule {
  id: number;
  service_id: number;
  equipment_type?: string;
  fault_type_id?: number;
  priority?: string;
  executor_id?: number;
  order: number;
  is_active: boolean;
  created_at: string;
}
