create table if not exists public.game_sessions (
  code text primary key check (char_length(code) = 6),
  gm_token uuid not null,
  stage smallint not null default 1 check (stage between 1 and 3),
  attempts integer not null default 0,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

alter table public.game_sessions enable row level security;

-- Aucun accès public : seule l’API serveur utilise la service role.
