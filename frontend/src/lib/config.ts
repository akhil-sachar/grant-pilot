export const appConfig = {
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "GrantPilot",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  demoMode: process.env.NEXT_PUBLIC_DEMO_MODE !== "false",
};

