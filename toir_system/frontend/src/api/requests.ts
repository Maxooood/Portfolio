import apiClient from './client';
import type { Request, RequestDetail, FaultType, Diagnostic, Repair, Report } from '../types';

export const requestsApi = {
  list: async (params?: {
    status?: string;
    priority?: string;
    service_id?: number;
    equipment_id?: number;
    skip?: number;
    limit?: number;
  }): Promise<Request[]> => {
    const res = await apiClient.get('/requests', { params });
    return res.data;
  },

  get: async (id: number): Promise<RequestDetail> => {
    const res = await apiClient.get(`/requests/${id}`);
    return res.data;
  },

  create: async (data: Partial<Request>): Promise<Request> => {
    const res = await apiClient.post('/requests', data);
    return res.data;
  },

  update: async (id: number, data: any): Promise<Request> => {
    const res = await apiClient.patch(`/requests/${id}`, data);
    return res.data;
  },

  // Fault types
  listFaultTypes: async (): Promise<FaultType[]> => {
    const res = await apiClient.get('/fault-types');
    return res.data;
  },

  createFaultType: async (data: { name: string; description?: string }): Promise<FaultType> => {
    const res = await apiClient.post('/fault-types', data);
    return res.data;
  },

  // Diagnostics
  listDiagnostics: async (requestId: number): Promise<Diagnostic[]> => {
    const res = await apiClient.get(`/requests/${requestId}/diagnostics`);
    return res.data;
  },

  createDiagnostic: async (requestId: number, data: any): Promise<Diagnostic> => {
    const res = await apiClient.post(`/requests/${requestId}/diagnostics`, data);
    return res.data;
  },

  // Repairs
  listRepairs: async (requestId: number): Promise<Repair[]> => {
    const res = await apiClient.get(`/requests/${requestId}/repairs`);
    return res.data;
  },

  createRepair: async (requestId: number, data: any): Promise<Repair> => {
    const res = await apiClient.post(`/requests/${requestId}/repairs`, data);
    return res.data;
  },

  // Reports
  listReports: async (requestId: number): Promise<Report[]> => {
    const res = await apiClient.get(`/requests/${requestId}/reports`);
    return res.data;
  },

  createReport: async (requestId: number, data: any): Promise<Report> => {
    const res = await apiClient.post(`/requests/${requestId}/reports`, data);
    return res.data;
  },
};
