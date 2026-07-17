import { apiClient } from "@/api/client";
import type { ApplicationRead } from "@/types/api";

export async function getApplications(): Promise<ApplicationRead[]> {
  const { data } = await apiClient.get<ApplicationRead[]>("/api/v1/applications");
  return data;
}
