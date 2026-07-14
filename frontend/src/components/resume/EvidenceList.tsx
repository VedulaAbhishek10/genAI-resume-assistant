import { useQuery } from "@tanstack/react-query";
import { getCandidateEvidence } from "@/api/evidence";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  isApiError,
  type CandidateEvidenceRead,
  type EvidenceType,
} from "@/types/api";

interface EvidenceListProps {
  candidateProfileId: string;
}

const EVIDENCE_TYPE_LABELS: Record<EvidenceType, string> = {
  experience_bullet: "Experience",
  project_bullet: "Project",
  achievement: "Achievement",
  skill: "Skill",
  certification: "Certification",
  education_item: "Education",
};

export function EvidenceList({ candidateProfileId }: EvidenceListProps) {
  const query = useQuery({
    queryKey: ["candidate-evidence", candidateProfileId],
    queryFn: () => getCandidateEvidence(candidateProfileId),
  });

  if (query.isPending) {
    return (
      <p className="text-sm text-muted-foreground">Loading evidence...</p>
    );
  }

  if (query.isError) {
    const message = isApiError(query.error)
      ? query.error.message
      : "Failed to load evidence.";
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load evidence</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
      </Alert>
    );
  }

  if (query.data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No evidence generated yet.
      </p>
    );
  }

  const grouped = groupByType(query.data);

  return (
    <div className="flex flex-col gap-4">
      {Object.entries(grouped).map(([type, items]) => (
        <Card key={type}>
          <CardHeader>
            <CardTitle>
              {EVIDENCE_TYPE_LABELS[type as EvidenceType]} ({items.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-2">
              {items.map((item) => (
                <li
                  key={item.id}
                  className="flex flex-col gap-1 border-b border-border pb-2 last:border-b-0 last:pb-0"
                >
                  <p className="text-sm text-foreground">{item.text}</p>
                  <Badge variant="outline" className="w-fit">
                    {item.source_entity_type}
                  </Badge>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function groupByType(
  evidence: CandidateEvidenceRead[],
): Partial<Record<EvidenceType, CandidateEvidenceRead[]>> {
  const grouped: Partial<Record<EvidenceType, CandidateEvidenceRead[]>> = {};
  for (const item of evidence) {
    const bucket = grouped[item.evidence_type] ?? [];
    bucket.push(item);
    grouped[item.evidence_type] = bucket;
  }
  return grouped;
}
