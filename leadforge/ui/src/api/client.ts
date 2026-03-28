import axios from "axios";

const API_BASE = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({ baseURL: API_BASE });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams({ username: email, password });
  const resp = await apiClient.post("/auth/token", form);
  return resp.data.access_token;
}

export async function getReviewQueue(campaignId: string) {
  const resp = await apiClient.get(`/review/${campaignId}`);
  return resp.data;
}

export async function approveEmail(emailId: string) {
  return apiClient.post(`/review/approve/${emailId}`);
}

export async function rejectEmail(emailId: string) {
  return apiClient.post(`/review/reject/${emailId}`);
}

export async function editAndApproveEmail(emailId: string, subject: string, body: string) {
  return apiClient.put(`/review/edit/${emailId}`, { subject, body });
}

export async function listCampaigns() {
  const resp = await apiClient.get("/campaigns/");
  return resp.data;
}
