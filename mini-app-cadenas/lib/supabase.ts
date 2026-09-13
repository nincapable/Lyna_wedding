const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

export function databaseConfigured() { return Boolean(url && key); }

export async function db(path: string, init: RequestInit = {}) {
  if (!url || !key) throw new Error('DATABASE_NOT_CONFIGURED');
  return fetch(`${url}/rest/v1/${path}`, {
    ...init,
    headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json', Prefer: 'return=representation', ...init.headers },
    cache: 'no-store',
  });
}
