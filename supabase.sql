-- =========================================================
-- КАДР / KADR
-- Database schema for the project marketplace
-- Run in Supabase SQL Editor.
-- =========================================================
begin;
-- 1. Marketplace projects table
create table if not exists public.projects (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null
        references auth.users(id)
        on delete cascade,
    title text not null
        check (char_length(trim(title)) between 3 and 120),
    category text not null
        check (
            category in (
                'film',
                'casting',
                'team',
                'job',
                'collaboration'
            )
        ),
    description text not null
        check (char_length(trim(description)) between 10 and 5000),
    contact text not null
        check (char_length(trim(contact)) between 3 and 300),
    status text not null default 'published'
        check (status in ('published', 'draft')),
    created_at timestamptz not null default now()
);
-- 2. Indexes for marketplace queries
create index if not exists projects_status_created_at_idx
    on public.projects (status, created_at desc);
create index if not exists projects_user_id_idx
    on public.projects (user_id);
create index if not exists projects_category_status_idx
    on public.projects (category, status);
-- 3. Enable Row Level Security
alter table public.projects enable row level security;
-- 4. Remove old versions of these policies before recreating them
drop policy if exists "Anyone can view published projects"
    on public.projects;
drop policy if exists "Authenticated users can publish their own projects"
    on public.projects;
drop policy if exists "Owners can update their own projects"
    on public.projects;
drop policy if exists "Owners can delete their own projects"
    on public.projects;
-- 5. Public read access for published listings only
create policy "Anyone can view published projects"
    on public.projects
    for select
    to anon, authenticated
    using (status = 'published');
-- 6. Authenticated users can create their own listings
-- New rows must belong to the logged-in user.
-- This policy permits only immediately published listings.
create policy "Authenticated users can publish their own projects"
    on public.projects
    for insert
    to authenticated
    with check (
        auth.uid() = user_id
        and status = 'published'
    );
-- 7. Owners may update their own rows.
-- Drafts remain private because the public SELECT policy
-- only exposes published rows.
create policy "Owners can update their own projects"
    on public.projects
    for update
    to authenticated
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);
-- 8. Owners may delete their own rows
create policy "Owners can delete their own projects"
    on public.projects
    for delete
    to authenticated
    using (auth.uid() = user_id);
-- 9. Grant only the required table operations.
-- RLS policies above still control which rows are accessible.
grant select on public.projects to anon, authenticated;
grant insert, update, delete on public.projects to authenticated;
commit;
-- =========================================================
-- IMPORTANT SECURITY NOTES
--
-- 1. Never put the Supabase service_role key in browser code.
--    Use only the publishable key or legacy anon key.
--
-- 2. Public visitors can read published listings, including
--    their contact field. Do not put private information
--    into a listing's contact field.
--
-- 3. The website currently inserts status = 'published'.
--    Draft creation is intentionally not enabled by this
--    INSERT policy.
--
-- 4. Configure email confirmation and allowed redirect URLs
--    in the Supabase Authentication settings as needed.
--
-- 5. RLS does not replace input validation, rate limiting,
--    abuse prevention, or CAPTCHA for public-facing forms.
-- =========================================================