/** Controlled error envelope returned by the backend (see docs/API.md). */
export interface ApiError {
  code: string;
  message: string;
}

export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === "object" &&
    value !== null &&
    "code" in value &&
    "message" in value
  );
}

export interface ExperienceExtraction {
  employer: string;
  job_title: string;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  achievements: string[];
}

export interface ProjectExtraction {
  name: string;
  description: string | null;
  technologies: string[];
  achievements: string[];
}

export interface SkillExtraction {
  name: string;
  category: string | null;
}

export interface EducationExtraction {
  institution: string;
  degree: string | null;
  field_of_study: string | null;
  dates: string | null;
  achievements: string[];
}

export interface CertificationExtraction {
  name: string;
  issuing_organization: string | null;
  issue_date: string | null;
}

/** Structured candidate profile produced by resume extraction (docs/API.md). */
export interface CandidateProfileExtraction {
  professional_summary: string | null;
  experiences: ExperienceExtraction[];
  projects: ProjectExtraction[];
  skills: SkillExtraction[];
  education: EducationExtraction[];
  certifications: CertificationExtraction[];
}

/** Response body of `POST /api/v1/resumes`. */
export interface ResumeUploadResponse {
  id: string;
  candidate_profile_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: "uploaded";
  extracted_text: string;
  candidate_profile: CandidateProfileExtraction;
}

export type EvidenceType =
  | "experience_bullet"
  | "project_bullet"
  | "achievement"
  | "skill"
  | "certification"
  | "education_item";

export type SourceEntityType =
  | "experience"
  | "project"
  | "skill"
  | "education"
  | "certification";

/** An item returned by `GET /api/v1/candidate-profiles/{id}/evidence`. */
export interface CandidateEvidenceRead {
  id: string;
  candidate_profile_id: string;
  evidence_type: EvidenceType;
  source_entity_type: SourceEntityType;
  source_entity_id: string;
  text: string;
  evidence_metadata: Record<string, string | null>;
  created_at: string;
}
