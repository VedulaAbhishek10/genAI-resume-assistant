import { apiClient } from "@/api/client";
import type {
  ResumeSuggestionRead,
  ResumeSuggestionUpdateRequest,
} from "@/types/api";

export async function generateSuggestions(
  matchAnalysisId: string,
): Promise<ResumeSuggestionRead[]> {
  const { data } = await apiClient.post<ResumeSuggestionRead[]>(
    `/api/v1/match-analyses/${matchAnalysisId}/suggestions`,
  );
  return data;
}

export async function listSuggestions(
  matchAnalysisId: string,
): Promise<ResumeSuggestionRead[]> {
  const { data } = await apiClient.get<ResumeSuggestionRead[]>(
    `/api/v1/match-analyses/${matchAnalysisId}/suggestions`,
  );
  return data;
}

export async function updateSuggestion(
  suggestionId: string,
  payload: ResumeSuggestionUpdateRequest,
): Promise<ResumeSuggestionRead> {
  const { data } = await apiClient.patch<ResumeSuggestionRead>(
    `/api/v1/suggestions/${suggestionId}`,
    payload,
  );
  return data;
}
