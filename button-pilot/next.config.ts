import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // SVG mockups live in /public and are served directly; no remote image hosts
  // are needed for the pilot. Add `images.remotePatterns` here once photoreal
  // hero images are hosted on a CDN.
  reactStrictMode: true,
};

export default nextConfig;
