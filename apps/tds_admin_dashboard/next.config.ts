import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',

  // Optimize for production
  reactStrictMode: true,
  poweredByHeader: false,

  // Configure allowed image domains (if needed)
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'erp.tsh.sale',
      },
    ],
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_SOCKET_URL: process.env.NEXT_PUBLIC_SOCKET_URL || 'ws://localhost:8000',
  },
};

export default nextConfig;
