import apiClient from './client';
import type { Token, LoginRequest } from '../types';

export const authApi = {
  login: async (data: LoginRequest): Promise<Token> => {
    const res = await apiClient.post<Token>('/auth/login', data);
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
};
