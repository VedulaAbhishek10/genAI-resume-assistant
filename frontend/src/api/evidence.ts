import { apiClient } from "@/api/client";
import type { CandidateEvidenceRead } from "@/types/api";

export async function getCandidateEvidence(
  candidateProfileId: string,
): Promise<CandidateEvidenceRead[]> {
  const response = await apiClient.get<CandidateEvidenceRead[]>(
    `/api/v1/candidate-profiles/${candidateProfileId}/evidence`,
  );
  return response.data;
}
