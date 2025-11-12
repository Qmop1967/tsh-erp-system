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
};

export default nextConfig;
