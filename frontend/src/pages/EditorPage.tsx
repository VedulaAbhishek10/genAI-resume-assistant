import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { listSuggestions, updateSuggestion } from "@/api/suggestions";
import type { ResumeSuggestionRead, ReviewStatus } from "@/types/api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function EditorPage() {
  const { matchAnalysisId } = useParams<{ matchAnalysisId: string }>();
  const [suggestions, setSuggestions] = useState<ResumeSuggestionRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  useEffect(() => {
    if (!matchAnalysisId) {
      setError("No match analysis ID provided in URL.");
      setLoading(false);
      return;
    }

    setLoading(true);
    listSuggestions(matchAnalysisId)
      .then((data) => setSuggestions(data))
      .catch(() => setError("Failed to load suggestions."))
      .finally(() => setLoading(false));
  }, [matchAnalysisId]);

  const handleUpdate = async (
    id: string,
    status: ReviewStatus,
    text?: string,
  ) => {
    try {
      const updated = await updateSuggestion(id, {
        review_status: status,
        edited_text: text,
      });
      setSuggestions((prev) => prev.map((s) => (s.id === id ? updated : s)));
      if (editingId === id) setEditingId(null);
    } catch {
      setError("Failed to update suggestion.");
    }
  };

  const startEditing = (suggestion: ResumeSuggestionRead) => {
    setEditingId(suggestion.id);
    setEditText(suggestion.edited_text || suggestion.suggested_text);
  };

  if (loading) {
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
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold text-foreground">Editor</h1>
      <p className="text-muted-foreground">
        Review, accept, reject, or edit AI-generated resume suggestions.
      </p>

      {suggestions.length === 0 && (
        <p className="text-muted-foreground">No suggestions found for this analysis.</p>
      )}

      {suggestions.map((suggestion) => (
        <Card key={suggestion.id}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{suggestion.requirement_text}</CardTitle>
              <Badge>{suggestion.review_status}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <h3 className="text-sm font-medium text-foreground">Original</h3>
              <p className="text-muted-foreground">{suggestion.original_text}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-foreground">Suggested</h3>
              {editingId === suggestion.id ? (
                <textarea
                  className="w-full rounded-md border border-input bg-background p-2 text-foreground"
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  rows={4}
                />
              ) : (
                <p className="text-muted-foreground">
                  {suggestion.edited_text || suggestion.suggested_text}
                </p>
              )}
            </div>
          </CardContent>
          <CardFooter className="gap-2">
            {editingId === suggestion.id ? (
              <>
                <Button onClick={() => handleUpdate(suggestion.id, "edited", editText)}>
                  Save Edit
                </Button>
                <Button variant="outline" onClick={() => setEditingId(null)}>
                  Cancel
                </Button>
              </>
            ) : (
              <>
                <Button onClick={() => handleUpdate(suggestion.id, "accepted")}>
                  Accept
                </Button>
                <Button variant="outline" onClick={() => handleUpdate(suggestion.id, "rejected")}>
                  Reject
                </Button>
                <Button variant="secondary" onClick={() => startEditing(suggestion)}>
                  Edit
                </Button>
              </>
            )}
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
