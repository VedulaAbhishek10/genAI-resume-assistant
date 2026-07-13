import { Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { HomePage } from "@/pages/HomePage";
import { ResumePage } from "@/pages/ResumePage";
import { JobsPage } from "@/pages/JobsPage";
import { AnalysisPage } from "@/pages/AnalysisPage";
import { EditorPage } from "@/pages/EditorPage";

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomePage />} />
        <Route path="resume" element={<ResumePage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route path="analysis" element={<AnalysisPage />} />
        <Route path="editor" element={<EditorPage />} />
      </Route>
    </Routes>
  );
}

export default App;
