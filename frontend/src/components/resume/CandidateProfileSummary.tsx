import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { CandidateProfileExtraction } from "@/types/api";

interface CandidateProfileSummaryProps {
  profile: CandidateProfileExtraction;
}

export function CandidateProfileSummary({
  profile,
}: CandidateProfileSummaryProps) {
  return (
    <div className="flex flex-col gap-4">
      {profile.professional_summary && (
        <Card>
          <CardHeader>
            <CardTitle>Professional summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-foreground">
              {profile.professional_summary}
            </p>
          </CardContent>
        </Card>
      )}

      <ProfileSection
        title="Experience"
        isEmpty={profile.experiences.length === 0}
        emptyMessage="No experience extracted."
      >
        {profile.experiences.map((experience, index) => (
          <div key={index} className="flex flex-col gap-1">
            <div className="flex flex-wrap items-baseline justify-between gap-x-3">
              <span className="font-medium text-foreground">
                {experience.job_title} · {experience.employer}
              </span>
              <span className="text-xs text-muted-foreground">
                {[experience.start_date, experience.end_date]
                  .filter(Boolean)
                  .join(" – ")}
              </span>
            </div>
            {experience.description && (
              <p className="text-sm text-muted-foreground">
                {experience.description}
              </p>
            )}
            {experience.achievements.length > 0 && (
              <ul className="ml-4 list-disc text-sm text-foreground">
                {experience.achievements.map((achievement, achIndex) => (
                  <li key={achIndex}>{achievement}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </ProfileSection>

      <ProfileSection
        title="Projects"
        isEmpty={profile.projects.length === 0}
        emptyMessage="No projects extracted."
      >
        {profile.projects.map((project, index) => (
          <div key={index} className="flex flex-col gap-1">
            <span className="font-medium text-foreground">
              {project.name}
            </span>
            {project.description && (
              <p className="text-sm text-muted-foreground">
                {project.description}
              </p>
            )}
            {project.technologies.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {project.technologies.map((technology) => (
                  <Badge key={technology} variant="outline">
                    {technology}
                  </Badge>
                ))}
              </div>
            )}
            {project.achievements.length > 0 && (
              <ul className="ml-4 list-disc text-sm text-foreground">
                {project.achievements.map((achievement, achIndex) => (
                  <li key={achIndex}>{achievement}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </ProfileSection>

      <ProfileSection
        title="Skills"
        isEmpty={profile.skills.length === 0}
        emptyMessage="No skills extracted."
      >
        <div className="flex flex-wrap gap-1.5">
          {profile.skills.map((skill, index) => (
            <Badge key={index} variant="secondary">
              {skill.name}
              {skill.category ? ` · ${skill.category}` : ""}
            </Badge>
          ))}
        </div>
      </ProfileSection>

      <ProfileSection
        title="Education"
        isEmpty={profile.education.length === 0}
        emptyMessage="No education extracted."
      >
        {profile.education.map((education, index) => (
          <div key={index} className="flex flex-col gap-1">
            <div className="flex flex-wrap items-baseline justify-between gap-x-3">
              <span className="font-medium text-foreground">
                {education.degree ? `${education.degree}, ` : ""}
                {education.institution}
              </span>
              {education.dates && (
                <span className="text-xs text-muted-foreground">
                  {education.dates}
                </span>
              )}
            </div>
            {education.field_of_study && (
              <p className="text-sm text-muted-foreground">
                {education.field_of_study}
              </p>
            )}
            {education.achievements.length > 0 && (
              <ul className="ml-4 list-disc text-sm text-foreground">
                {education.achievements.map((achievement, achIndex) => (
                  <li key={achIndex}>{achievement}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </ProfileSection>

      <ProfileSection
        title="Certifications"
        isEmpty={profile.certifications.length === 0}
        emptyMessage="No certifications extracted."
      >
        {profile.certifications.map((certification, index) => (
          <div
            key={index}
            className="flex flex-wrap items-baseline justify-between gap-x-3"
          >
            <span className="font-medium text-foreground">
              {certification.name}
            </span>
            <span className="text-xs text-muted-foreground">
              {[certification.issuing_organization, certification.issue_date]
                .filter(Boolean)
                .join(" · ")}
            </span>
          </div>
        ))}
      </ProfileSection>
    </div>
  );
}

interface ProfileSectionProps {
  title: string;
  isEmpty: boolean;
  emptyMessage: string;
  children: ReactNode;
}

function ProfileSection({
  title,
  isEmpty,
  emptyMessage,
  children,
}: ProfileSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <p className="text-sm text-muted-foreground">{emptyMessage}</p>
        ) : (
          <div className="flex flex-col gap-3">{children}</div>
        )}
      </CardContent>
    </Card>
  );
}
