import { execSync } from "node:child_process";

const url = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
execSync(`pnpm exec openapi-typescript ${url}/openapi.json -o lib/api-schema.ts`, { stdio: "inherit" });
