import { type FormEvent, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AlertCircle, UploadCloud } from "lucide-react";
import { uploadResume } from "@/api/resumes";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { isApiError, type ResumeUploadResponse } from "@/types/api";

const ACCEPTED_EXTENSIONS = ".pdf,.docx";

interface ResumeUploadCardProps {
  onUploaded: (result: ResumeUploadResponse) => void;
}

export function ResumeUploadCard({ onUploaded }: ResumeUploadCardProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const mutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: (result) => {
      onUploaded(result);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (selectedFile) {
      mutation.mutate(selectedFile);
    }
  }

  const errorMessage = mutation.isError
    ? isApiError(mutation.error)
      ? mutation.error.message
      : "Upload failed. Please try again."
    : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload resume</CardTitle>
        <CardDescription>
          PDF or DOCX. We&apos;ll extract a structured candidate profile and
          evidence from it.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_EXTENSIONS}
            onChange={(event) =>
              setSelectedFile(event.target.files?.[0] ?? null)
            }
            className="text-sm text-foreground file:mr-3 file:rounded-lg file:border-0 file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-secondary-foreground"
          />
          <div className="flex items-center gap-3">
            <Button
              type="submit"
              disabled={!selectedFile || mutation.isPending}
            >
              <UploadCloud />
              {mutation.isPending ? "Uploading..." : "Upload"}
            </Button>
            {selectedFile && (
              <span className="text-sm text-muted-foreground">
                {selectedFile.name}
              </span>
            )}
          </div>
          {errorMessage && (
            <Alert variant="destructive">
              <AlertCircle />
              <AlertTitle>Upload failed</AlertTitle>
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}
          {mutation.isSuccess && (
            <Alert>
              <AlertTitle>Resume uploaded</AlertTitle>
              <AlertDescription>
                Candidate profile extracted from {mutation.data.filename}.
              </AlertDescription>
            </Alert>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
