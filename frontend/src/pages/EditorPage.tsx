import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listSuggestions,
  updateSuggestion,
  generateSuggestions,
} from "@/api/suggestions";
import type { ResumeSuggestionRead, ReviewStatus } from "@/types/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function EditorPage() {
  const { matchAnalysisId } = useParams<{ matchAnalysisId: string }>();
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  const { data: suggestions, isLoading, error } = useQuery({
    queryKey: ["suggestions", matchAnalysisId],
    queryFn: () => listSuggestions(matchAnalysisId!),
    enabled: !!matchAnalysisId,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateSuggestions(matchAnalysisId!),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["suggestions", matchAnalysisId],
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (variables: {
      id: string;
      status: ReviewStatus;
      text?: string;
    }) =>
      updateSuggestion(variables.id, {
        review_status: variables.status,
        edited_text: variables.text,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["suggestions", matchAnalysisId],
      });
      setEditingId(null);
    },
  });

  const startEditing = (suggestion: ResumeSuggestionRead) => {
    setEditingId(suggestion.id);
    setEditText(suggestion.edited_text || suggestion.suggested_text);
  };

  if (!matchAnalysisId) {
    return (
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-foreground">Editor</h1>
        <p className="text-red-500">No match analysis ID provided in URL.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-foreground">Editor</h1>
        <p className="text-muted-foreground">Loading suggestions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-foreground">Editor</h1>
        <p className="text-red-500">Failed to load suggestions.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold text-foreground">Editor</h1>
      <p className="text-muted-foreground">
        Review, accept, reject, or edit AI-generated resume suggestions.
      </p>

      {suggestions && suggestions.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              No suggestions found for this analysis.
            </p>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
            >
              {generateMutation.isPending ? "Generating..." : "Generate Suggestions"}
            </Button>
          </CardFooter>
        </Card>
      )}

      {suggestions?.map((suggestion) => (
        <Card key={suggestion.id}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{suggestion.requirement_text}</CardTitle>
              <Badge>{suggestion.review_status}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-foreground">Original</h3>
                <p className="text-muted-foreground">
                  {suggestion.original_text}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-foreground">Suggested</h3>
                {editingId === suggestion.id ? (
                  <textarea
                    className="w-full rounded-md border border-input bg-background p-2 text-foreground"
                    value={editText}
                    onChange={(e