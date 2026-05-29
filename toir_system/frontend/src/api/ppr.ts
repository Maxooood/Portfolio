import apiClient from './client';
import type { PprSchedule, PprTask } from '../types';

export const pprApi = {
  listSchedules: async (params?: { year?: number }): Promise<PprSchedule[]> => {
    const res = await apiClient.get('/ppr/schedules', { params });
    return res.data;
  },

  getSchedule: async (id: number): Promise<PprSchedule & { tasks: PprTask[] }> => {
    const res = await apiClient.get(`/ppr/schedules/${id}`);
    return res.data;
  },

  generateSchedule: async (year: number, month: number): Promise<PprSchedule> => {
    const res = await apiClient.post('/ppr/schedules/generate', { year, month });
    return res.data;
  },

  approveSchedule: async (id: number): Promise<PprSchedule> => {
    const res = await apiClient.post(`/ppr/schedules/${id}/approve`);
    return res.data;
  },

  getScheduleTasks: async (scheduleId: number): Promise<PprTask[]> => {
    const res = await apiClient.get(`/ppr/schedules/${scheduleId}/tasks`);
    return res.data;
  },

  updateTaskStatus: async (taskId: number, status: string, notes?: string): Promise<PprTask> => {
    const res = await apiClient.put(`/ppr/tasks/${taskId}/status`, { status, notes });
    return res.data;
  },

  createRequestFromTask: async (taskId: number): Promise<{ request_id: number; request_number: string }> => {
    const res = await apiClient.post(`/ppr/tasks/${taskId}/create-request`);
    return res.data;
  },
};
