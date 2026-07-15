import { apiClient } from "@/api/client";
import type { JobDescriptionResponse } from "@/types/api";

export async function submitJobDescription(
  text: string,
): Promise<JobDescriptionResponse> {
  const { data } = await apiClient.post<JobDescriptionResponse>(
    "/api/v1/jobs",
    { text },
  );
  return data;
}
