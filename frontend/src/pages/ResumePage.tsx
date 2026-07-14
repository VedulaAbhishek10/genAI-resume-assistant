import { useState } from "react";
import { CandidateProfileSummary } from "@/components/resume/CandidateProfileSummary";
import { EvidenceList } from "@/components/resume/EvidenceList";
import { ResumeUploadCard } from "@/components/resume/ResumeUploadCard";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import type { ResumeUploadResponse } from "@/types/api";

export function ResumePage() {
  const [uploadResult, setUploadResult] = useState<ResumeUploadResponse | null>(
    null,
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-foreground">Resume</h1>
        <p className="text-muted-foreground">
          Upload a resume and review your structured candidate profile and
          evidence.
        </p>
      </div>

      <ResumeUploadCard onUploaded={setUploadResult} />

      {uploadResult && (
        <Tabs defaultValue="profile">
          <TabsList>
            <TabsTrigger value="profile">Candidate profile</TabsTrigger>
            <TabsTrigger value="evidence">Evidence</TabsTrigger>
          </TabsList>
          <TabsContent value="profile">
            <CandidateProfileSummary profile={uploadResult.candidate_profile} />
          </TabsContent>
          <TabsContent value="evidence">
            <EvidenceList
              candidateProfileId={uploadResult.candidate_profile_id}
            />
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
