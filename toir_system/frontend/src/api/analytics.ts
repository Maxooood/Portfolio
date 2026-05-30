import apiClient from './client';
import type { DashboardStats, AnalyticsReport } from '../types';

export const analyticsApi = {
  getDashboard: async (): Promise<DashboardStats> => {
    const res = await apiClient.get('/analytics/dashboard');
    return res.data;
  },

  getReport: async (): Promise<AnalyticsReport> => {
    const res = await apiClient.get('/analytics/report');
    return res.data;
  },
};
