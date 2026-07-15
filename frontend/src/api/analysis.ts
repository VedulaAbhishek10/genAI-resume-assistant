import { apiClient } from "@/api/client";
import type { MatchAnalysisResponse } from "@/types/api";

export async function runMatchAnalysis(
  candidateProfileId: string,
  jobDescriptionId: string,
): Promise<MatchAnalysisResponse> {
  const { data } = await apiClient.post<MatchAnalysisResponse>(
    "/api/v1/match-analyses",
    {
      candidate_profile_id: candidateProfileId,
      job_description_id: jobDescriptionId,
    },
  );
  return data;
}
