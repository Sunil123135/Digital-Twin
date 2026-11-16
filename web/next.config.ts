import type { NextConfig } from "next";

const localModules = process.env.PHARMATWIN_NODE_MODULES;

const nextConfig: NextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    if (localModules) {
      config.resolve.modules = [localModules, ...(config.resolve.modules ?? ["node_modules"])];
    }
    return config;
  },
};

export default nextConfig;
