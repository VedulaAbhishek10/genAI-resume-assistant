import { apiClient } from "@/api/client";
import type { ResumeUploadResponse } from "@/types/api";

export async function uploadResume(
  file: File,
): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post<ResumeUploadResponse>(
    "/api/v1/resumes",
    formData,
  );
  return response.data;
}
