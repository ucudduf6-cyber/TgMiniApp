-- =========================================================
-- КАДР — БАЗА ДАННЫХ
-- Регистрация пользователей и биржа кинопроектов
-- =========================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------
-- 1. ПРОФИЛИ ПОЛЬЗОВАТЕЛЕЙ
-- ---------------------------------------------------------

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    display_name text not null default '',
    avatar_url text,
    bio text not null default '',
    city text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint profiles_display_name_length
        check (char_length(display_name) <= 80),

    constraint profiles_bio_length
        check (char_length(bio) <= 1000),

    constraint profiles_city_length
        check (char_length(city) <= 100)
);

-- ---------------------------------------------------------
-- 2. КИНОПРОЕКТЫ И ОБЪЯВЛЕНИЯ
-- ---------------------------------------------------------

create table if not exists public.projects (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    title text not null,
    description text not null,

    category text not null default 'other'
        check (
            category in (
                'short',
                'feature',
                'music',
                'crew',
                'other'
            )
        ),

    city text not null default '',
    contact text not null default '',
    budget text not null default '',

    status text not null default 'published'
        check (
            status in (
                'draft',
                'published',
                'archived'
            )
        ),

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint projects_title_length
        check (
            char_length(trim(title)) between 1 and 100
        ),

    constraint projects_description_length
        check (
            char_length(trim(description)) between 1 and 3000
        ),

    constraint projects_city_length
        check (char_length(city) <= 100),

    constraint projects_contact_length
        check (char_length(contact) <= 200),

    constraint projects_budget_length
        check (char_length(budget) <= 100)
);

create index if not exists projects_status_created_at_idx
    on public.projects (status, created_at desc);

create index if not exists projects_user_id_idx
    on public.projects (user_id);

-- ---------------------------------------------------------
-- 3. ОБНОВЛЕНИЕ ДАТЫ ИЗМЕНЕНИЯ
-- ---------------------------------------------------------

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists profiles_updated_at
    on public.profiles;

create trigger profiles_updated_at
before update on public.profiles
for each row
execute function public.set_updated_at();

drop trigger if exists projects_updated_at
    on public.projects;

create trigger projects_updated_at
before update on public.projects
for each row
execute function public.set_updated_at();

-- ---------------------------------------------------------
-- 4. АВТОМАТИЧЕСКОЕ СОЗДАНИЕ ПРОФИЛЯ
-- ---------------------------------------------------------

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
    insert into public.profiles (id, display_name)
    values (
        new.id,
        coalesce(
            new.raw_user_meta_data ->> 'full_name',
            ''
        )
    )
    on conflict (id) do nothing;

    return new;
end;
$$;

drop trigger if exists on_auth_user_created
    on auth.users;

create trigger on_auth_user_created
after insert on auth.users
for each row
execute function public.handle_new_user();

-- ---------------------------------------------------------
-- 5. ВКЛЮЧЕНИЕ ЗАЩИТЫ RLS
-- ---------------------------------------------------------

alter table public.profiles enable row level security;
alter table public.projects enable row level security;

-- ---------------------------------------------------------
-- 6. ПРАВА ДОСТУПА К ПРОФИЛЯМ
-- Каждый пользователь работает только со своим профилем.
-- ---------------------------------------------------------

drop policy if exists "Users can read own profile"
    on public.profiles;

create policy "Users can read own profile"
on public.profiles
for select
to authenticated
using (id = (select auth.uid()));

drop policy if exists "Users can insert own profile"
    on public.profiles;

create policy "Users can insert own profile"
on public.profiles
for insert
to authenticated
with check (id = (select auth.uid()));

drop policy if exists "Users can update own profile"
    on public.profiles;

create policy "Users can update own profile"
on public.profiles
for update
to authenticated
using (id = (select auth.uid()))
with check (id = (select auth.uid()));

-- ---------------------------------------------------------
-- 7. ПРАВА ДОСТУПА К ОБЪЯВЛЕНИЯМ
-- Просмотр опубликованных объявлений доступен всем.
-- Создание, изменение и удаление — только владельцу.
-- ---------------------------------------------------------

drop policy if exists "Anyone can read published projects"
    on public.projects;

create policy "Anyone can read published projects"
on public.projects
for select
to anon, authenticated
using (status = 'published');

drop policy if exists "Users can insert own projects"
    on public.projects;

create policy "Users can insert own projects"
on public.projects
for insert
to authenticated
with check (
    user_id = (select auth.uid())
);

drop policy if exists "Users can update own projects"
    on public.projects;

create policy "Users can update own projects"
on public.projects
for update
to authenticated
using (
    user_id = (select auth.uid())
)
with check (
    user_id = (select auth.uid())
);

drop policy if exists "Users can delete own projects"
    on public.projects;

create policy "Users can delete own projects"
on public.projects
for delete
to authenticated
using (
    user_id = (select auth.uid())
);

-- ---------------------------------------------------------
-- 8. ПРАВА НА УРОВНЕ ТАБЛИЦ
-- RLS-политики выше дополнительно ограничивают доступ.
-- ---------------------------------------------------------

revoke all on public.profiles from anon;
revoke all on public.profiles from authenticated;

grant select, insert, update
on public.profiles to authenticated;

revoke all on public.projects from anon;
revoke all on public.projects from authenticated;

grant select on public.projects to anon, authenticated;
grant insert, update, delete
on public.projects to authenticated;

-- ---------------------------------------------------------
-- 9. ЗАВЕРШЕНО
-- Объявления автоматически не создаются.
-- Таблицы готовы к подключению сайта.
-- ---------------------------------------------------------