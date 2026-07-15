import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";

import { runMatchAnalysis } from "@/api/analysis";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  isApiError,
  type MatchAnalysisResponse,
  type MatchClassification,
} from "@/types/api";

interface AnalysisFormInputs {
  candidateProfileId: string;
  jobDescriptionId: string;
}

const CLASSIFICATION_ORDER: MatchClassification[] = [
  "STRONG_MATCH",
  "PARTIAL_MATCH",
  "NO_EVIDENCE",
];

export function AnalysisPage() {
  const [analysis, setAnalysis] = useState<MatchAnalysisResponse | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AnalysisFormInputs>();

  const mutation = useMutation({
    mutationFn: (data: AnalysisFormInputs) =>
      runMatchAnalysis(data.candidateProfileId, data.jobDescriptionId),
    onSuccess: (data) => setAnalysis(data),
    onError: () => setAnalysis(null),
  });

  const onSubmit = (data: AnalysisFormInputs) => {
    mutation.mutate(data);
  };

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Run Match Analysis</CardTitle>
          <CardDescription>
            Enter the IDs to run a match analysis between a candidate profile and
            a job description.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="flex flex-col gap-4"
          >
            <div className="flex flex-col gap-2">
              <label
                htmlFor="candidateProfileId"
                className="text-sm font-medium"
              >
                Candidate Profile ID
              </label>
              <input
                id="candidateProfileId"
                {...register("candidateProfileId", {
                  required: "Candidate Profile ID is required",
                })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000"
              />
              {errors.candidateProfileId && (
                <p className="text-sm text-destructive">
                  {errors.candidateProfileId.message}
                </p>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <label
                htmlFor="jobDescriptionId"
                className="text-sm font-medium"
              >
                Job Description ID
              </label>
              <input
                id="jobDescriptionId"
                {...register("jobDescriptionId", {
                  required: "Job Description ID is required",
                })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000"
              />
              {errors.jobDescriptionId && (
                <p className="text-sm text-destructive">
                  {errors.jobDescriptionId.message}
                </p>
              )}
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Analyzing..." : "Run Analysis"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {mutation.isError && isApiError(mutation.error) && (
        <Alert variant="destructive">
          <AlertTitle>Error {mutation.error.code}</AlertTitle>
          <AlertDescription>{mutation.error.message}</AlertDescription>
        </Alert>
      )}

      {analysis && (
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Match Score</CardTitle>
              <CardDescription>
                Overall match score and component breakdown.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <div className="text-4xl font-bold">
                  {(analysis.overall_score * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-muted-foreground">
                  Overall Match Score
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(analysis.component_scores).map(
                  ([key, value]) => (
                    <div key={key} className="rounded-md border p-3">
                      <div className="text-sm font-medium capitalize">
                        {key.replace(/_/g, " ")}
                      </div>
                      <div className="text-lg font-semibold">
                        {(value * 100).toFixed(1)}%
                      </div>
                    </div>
                  ),
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Requirement Matches</CardTitle>
              <CardDescription>
                Detailed breakdown of requirement matches.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {analysis.requirement_matches.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No requirement matches found.
                </p>
              ) : (
                CLASSIFICATION_ORDER.map((classification) => {
                  const matches = analysis.requirement_matches.filter(
                    (m) => m.classification === classification,
                  );
                  if (matches.length === 0) return null;
                  return (
                    <div key={classification}>
                      <h4 className="mb-2 text-sm font-medium capitalize">
                        {classification.replace(/_/g, " ")}
                      </h4>
                      <ul className="flex flex-col gap-2">
                        {matches.map((match) => (
                          <li
                            key={match.id}
                            className="rounded-md border p-3 text-sm"
                          >
                            <div className="font-medium">
                              {match.requirement_text}
                            </div>
                            <div className="mt-1 text-muted-foreground">
                              {match.explanation}
                            </div>
                            {match.evidence.length > 0 && (
                              <div className="mt-2">
                                <span className="text-xs font-semibold uppercase text-muted-foreground">
                                  Evidence:
                                </span>
                                <ul className="ml-4 list-disc">
                                  {match.evidence.map((ev) => (
                                    <li
                                      key={ev.id}
                                      className="text-xs text-muted-foreground"
                                    >
                                      {ev.text}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Gaps</CardTitle>
              <CardDescription>
                Requirements with missing or partial evidence.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis.gaps.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No gaps identified.
                </p>
              ) : (
                <ul className="flex flex-col gap-2">
                  {analysis.gaps.map((gap, idx) => (
                    <li
                      key={idx}
                      className="rounded-md border p-3 text-sm"
                    >
                      <div className="font-medium">
                        {gap.requirement_text}
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {gap.classification.replace(/_/g, " ")} •{" "}
                        {gap.importance}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
