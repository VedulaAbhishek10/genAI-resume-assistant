import { useQuery } from "@tanstack/react-query";
import { getApplications } from "@/api/applications";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import type { ApplicationStatus } from "@/types/api";

const statusVariantMap: Record<
  ApplicationStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  saved: "secondary",
  preparing: "default",
  applied: "default",
  interview: "default",
  offer: "default",
  rejected: "destructive",
  withdrawn: "outline",
};

export function DashboardPage() {
  const {
    data: applications,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["applications"],
    queryFn: getApplications,
  });

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">Loading applications...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load applications.{" "}
          {error instanceof Error ? error.message : "Please try again later."}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Application Dashboard</h1>
        <Button>New Application</Button>
      </div>

      {applications && applications.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No Applications Yet</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Start by uploading a resume and analyzing a job description to create your first tailored application.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {applications?.map((app) => (
            <Card key={app.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{app.role}</CardTitle>
                  <Badge variant={statusVariantMap[app.status]}>
                    {app.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <p className="font-medium">{app.company}</p>
                  <p className="text-muted-foreground">
                    Applied:{" "}
                    {app.applied_at
                      ? new Date(app.applied_at).toLocaleDateString()
                      : "Not applied yet"}
                  </p>
                  <p className="text-muted-foreground">
                    Resume Version:{" "}
                    {app.resume_version_id ? "Linked" : "Not linked"}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
