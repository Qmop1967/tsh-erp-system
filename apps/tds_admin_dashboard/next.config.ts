import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',

  // Configure base path for proxy routing through /tds-admin
  basePath: '/tds-admin',

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
