import { AppShell } from "@/components/app-shell";
import { DemoShowcase } from "@/components/demo-showcase";
import { PageHeader } from "@/components/page-header";

export default function DemoPage() {
  return (
    <AppShell>
      <PageHeader
        title="Hackathon Demo"
        description="A polished walkthrough of GrantPilot's autonomous agent pipeline — from discovery to outreach."
      />
      <DemoShowcase />
    </AppShell>
  );
}
