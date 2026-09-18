import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    '/api/games/*/documents/*': ['./enquete-documents/*.pdf'],
    '/api/games/*/scan': ['./scan-reference/dragon.png'],
    '/api/games/*/report': ['./resolution-documents/*.pdf'],
  },
};

export default nextConfig;
