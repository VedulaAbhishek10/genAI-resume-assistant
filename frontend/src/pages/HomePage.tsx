import { Link } from "react-router-dom";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function HomePage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold text-foreground">
        GenAI Resume Assistant
      </h1>
      <p className="text-muted-foreground">
        Upload a resume, analyze it against a target job description, and generate
        an evidence-grounded, tailored resume version.
      </p>
      <Link to="/resume" className={cn(buttonVariants({ variant: "default" }), "w-fit")}>
        Start with your resume
      </Link>
    </div>
  );
}
