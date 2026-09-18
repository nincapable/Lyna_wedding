import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    '/api/games/*/documents/*': ['./enquete-documents/*.pdf'],
  },
};

export default nextConfig;
