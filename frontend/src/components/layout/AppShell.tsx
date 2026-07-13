import { Outlet } from "react-router-dom";
import { NavBar } from "@/components/layout/NavBar";

export function AppShell() {
  return (
    <div className="flex min-h-screen flex-col">
      <NavBar />
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
