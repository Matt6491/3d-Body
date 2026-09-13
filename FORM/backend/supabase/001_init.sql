
-- FORM production schema sketch. Apply in a Supabase project after review.
create extension if not exists pgcrypto;

create table if not exists public.body_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  age_at_capture integer not null check (age_at_capture >= 18),
  biological_sex text not null check (biological_sex in ('male','female')),
  height_cm numeric not null,
  weight_kg numeric not null,
  experience text not null check (experience in ('beginner','intermediate','advanced')),
  body_model jsonb not null,
  body_fat_mode text not null default 'CONSTANT'
);
create table if not exists public.body_analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  body_profile_id uuid references public.body_profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  method text not null,
  derived_measurements jsonb not null,
  quality jsonb not null
);
create table if not exists public.photo_assets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  body_profile_id uuid references public.body_profiles(id) on delete cascade,
  storage_key text not null,
  view text not null check (view in ('front','side','back')),
  delete_after timestamptz,
  created_at timestamptz not null default now()
);

alter table public.body_profiles enable row level security;
alter table public.body_analyses enable row level security;
alter table public.photo_assets enable row level security;

create policy "own body profiles" on public.body_profiles for all using (auth.uid()=user_id) with check (auth.uid()=user_id);
create policy "own body analyses" on public.body_analyses for all using (auth.uid()=user_id) with check (auth.uid()=user_id);
create policy "own photo metadata" on public.photo_assets for all using (auth.uid()=user_id) with check (auth.uid()=user_id);

-- Storage bucket must be PRIVATE. Do not create public read policies.
