import apiClient from './client';
import type { Equipment, EquipmentNorm } from '../types';

export const equipmentApi = {
  list: async (params?: { status?: string; department?: string }): Promise<Equipment[]> => {
    const res = await apiClient.get('/equipment', { params });
    return res.data;
  },

  get: async (id: number): Promise<Equipment> => {
    const res = await apiClient.get(`/equipment/${id}`);
    return res.data;
  },

  create: async (data: Partial<Equipment>): Promise<Equipment> => {
    const res = await apiClient.post('/equipment', data);
    return res.data;
  },

  update: async (id: number, data: Partial<Equipment>): Promise<Equipment> => {
    const res = await apiClient.patch(`/equipment/${id}`, data);
    return res.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/equipment/${id}`);
  },

  // Norms
  listNorms: async (equipmentId: number): Promise<EquipmentNorm[]> => {
    const res = await apiClient.get(`/equipment/${equipmentId}/norms`);
    return res.data;
  },

  createNorm: async (equipmentId: number, data: Partial<EquipmentNorm>): Promise<EquipmentNorm> => {
    const res = await apiClient.post(`/equipment/${equipmentId}/norms`, data);
    return res.data;
  },

  updateNorm: async (equipmentId: number, normId: number, data: Partial<EquipmentNorm>): Promise<EquipmentNorm> => {
    const res = await apiClient.patch(`/equipment/${equipmentId}/norms/${normId}`, data);
    return res.data;
  },
};
