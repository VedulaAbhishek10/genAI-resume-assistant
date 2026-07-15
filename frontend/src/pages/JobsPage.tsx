import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";

import { submitJobDescription } from "@/api/jobs";
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
  type JobDescriptionResponse,
  type JobRequirementImportance,
} from "@/types/api";

interface JobFormInputs {
  text: string;
}

const IMPORTANCE_ORDER: JobRequirementImportance[] = [
  "required",
  "preferred",
  "optional",
];

export function JobsPage() {
  const [job, setJob] = useState<JobDescriptionResponse | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<JobFormInputs>();

  const mutation = useMutation({
    mutationFn: submitJobDescription,
    onSuccess: (data) => setJob(data),
    onError: () => setJob(null),
  });

  const onSubmit = (data: JobFormInputs) => {
    mutation.mutate(data.text);
  };

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Submit Job Description</CardTitle>
          <CardDescription>
            Paste a target job description to extract structured requirements.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="flex flex-col gap-4"
          >
            <textarea
              {...register("text", { required: "Job description text is required" })}
              className="flex min-h-[200px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Paste job description here..."
            />
            {errors.text && (
              <p className="text-sm text-destructive">{errors.text.message}</p>
            )}
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Analyzing..." : "Submit & Extract"}
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

      {job && (
        <Card>
          <CardHeader>
            <CardTitle>{job.role_title || "Job Description"}</CardTitle>
            <CardDescription>
              {job.company && <span>{job.company} • </span>}
              {job.seniority && (
                <span className="capitalize">{job.seniority}</span>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div>
              <h3 className="mb-2 text-lg font-semibold">Requirements</h3>
              {job.requirements.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No requirements extracted.
                </p>
              ) : (
                <div className="flex flex-col gap-4">
                  {IMPORTANCE_ORDER.map((importance) => {
                    const reqs = job.requirements.filter(
                      (r) => r.importance === importance,
                    );
                    if (reqs.length === 0) return null;
                    return (
                      <div key={importance}>
                        <h4 className="mb-2 text-sm font-medium capitalize">
                          {importance}
                        </h4>
                        <ul className="flex flex-col gap-2">
                          {reqs.map((req) => (
                            <li
                              key={req.id}
                              className="rounded-md border p-3 text-sm"
                            >
                              <span className="font-medium capitalize">
                                {req.category.replace(/_/g, " ")}:
                              </span>{" "}
                              {req.text}
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
