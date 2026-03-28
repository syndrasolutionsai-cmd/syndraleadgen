import axios from "axios";

const API_BASE = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({ baseURL: API_BASE });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams({ username: email, password });
  const resp = await apiClient.post("/auth/token", form);
  return resp.data.access_token;
}

// Clients
export async function getCurrentUser() {
  const resp = await apiClient.get("/clients/me");
  return resp.data;
}

export async function updateCurrentUser(data: { instantly_api_key?: string }) {
  const resp = await apiClient.patch("/clients/me", data);
  return resp.data;
}

export async function getAllClients() {
  const resp = await apiClient.get("/clients/all");
  return resp.data;
}

export async function createClient(data: {
  name: string; email: string; password: string; instantly_api_key?: string;
}) {
  const resp = await apiClient.post("/clients/", data);
  return resp.data;
}

// Campaigns
export async function listCampaigns() {
  const resp = await apiClient.get("/campaigns/");
  return resp.data;
}

export async function getCampaign(id: string) {
  const resp = await apiClient.get(`/campaigns/${id}`);
  return resp.data;
}

export async function createCampaign(data: {
  name: string;
  niche: string;
  value_prop: string;
  language: string;
  batch_size: number;
  review_pct: number;
  icp_config: object;
}) {
  const resp = await apiClient.post("/campaigns/", data);
  return resp.data;
}

export async function launchCampaign(id: string) {
  const resp = await apiClient.post(`/campaigns/${id}/launch`, {});
  return resp.data;
}

// Review
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

// Analytics
export async function getAnalyticsSummary() {
  const resp = await apiClient.get("/analytics/summary");
  return resp.data;
}

export async function getCampaignAnalytics(campaignId: string) {
  const resp = await apiClient.get(`/analytics/${campaignId}`);
  return resp.data;
}
