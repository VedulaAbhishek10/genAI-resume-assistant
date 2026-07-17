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

export type JobRequirementCategory =
  | "skill"
  | "experience"
  | "responsibility"
  | "education"
  | "certification"
  | "domain_knowledge";

export type JobRequirementImportance =
  | "required"
  | "preferred"
  | "optional";

export interface JobRequirementRead {
  id: string;
  text: string;
  category: JobRequirementCategory;
  importance: JobRequirementImportance;
}

/** Response body of `POST /api/v1/jobs`. */
export interface JobDescriptionResponse {
  id: string;
  source_text: string;
  role_title: string | null;
  company: string | null;
  seniority: string | null;
  requirements: JobRequirementRead[];
  created_at: string;
}

export type MatchClassification =
  | "STRONG_MATCH"
  | "PARTIAL_MATCH"
  | "NO_EVIDENCE";

export interface RequirementMatchRead {
  id: string;
  job_requirement_id: string;
  requirement_text: string;
  category: JobRequirementCategory;
  importance: JobRequirementImportance;
  classification: MatchClassification;
  explanation: string;
  confidence: number;
  evidence: CandidateEvidenceRead[];
}

export interface GapItem {
  requirement_text: string;
  category: JobRequirementCategory;
  importance: JobRequirementImportance;
  classification: MatchClassification;
}

/** Response body of `POST /api/v1/match-analyses`. */
export interface MatchAnalysisResponse {
  id: string;
  candidate_profile_id: string;
  job_description_id: string;
  overall_score: number;
  component_scores: Record<string, number>;
  requirement_matches: RequirementMatchRead[];
  gaps: GapItem[];
  created_at: string;
}

export type ReviewStatus = "pending" | "accepted" | "rejected" | "edited";

export interface ResumeSuggestionRead {
  id: string;
  match_analysis_id: string;
  requirement_text: string;
  original_text: string;
  suggested_text: string;
  reason: string | null;
  evidence_ids: string[];
  confidence: number | null;
  is_grounded: boolean;
  review_status: ReviewStatus;
  edited_text: string | null;
  created_at: string;
}

export interface ResumeSuggestionUpdateRequest {
  review_status: ReviewStatus;
  edited_text?: string | null;
}

export type ApplicationStatus =
  | "saved"
  | "preparing"
  | "applied"
  | "interview"
  | "rejected"
  | "offer"
  | "withdrawn";

export interface ApplicationRead {
  id: string;
  candidate_profile_id: string;
  job_description_id: string;
  resume_version_id: string | null;
  company: string;
  role: string;
  status: ApplicationStatus;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeVersionRead {
  id: string;
  resume_id: string;
  job_description_id: string;
  match_analysis_id: string;
  applied_suggestion_ids: string[];
  generated_content: Record<string, unknown>;
  created_at: string;
}
