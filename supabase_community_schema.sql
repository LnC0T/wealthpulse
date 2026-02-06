-- Supabase Community Schema for WealthPulse
-- NOTE: Community tables include permissive policies for anon access.
-- The core app storage table (`wealthpulse_users`) is locked to service_role only.
-- Tighten policies further before production if using Supabase Auth.

create extension if not exists "pgcrypto";

create table if not exists community_users (
  id uuid primary key default gen_random_uuid(),
  username text unique not null,
  auth jsonb,
  recovery jsonb,
  auth_id uuid,
  email text,
  updated_at timestamptz default now()
);

create table if not exists community_posts (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  body text not null,
  category text,
  listing_type text,
  price numeric,
  currency text,
  location text,
  created_by text,
  owner_id uuid,
  created_at timestamptz default now(),
  status text,
  auction_starting_bid numeric,
  auction_min_increment numeric,
  reserve_amount numeric,
  buy_now_price numeric,
  images jsonb,
  grading_company text,
  grading_grade text,
  auction_end_date date,
  sold_price numeric,
  sold_at timestamptz
);

create table if not exists community_comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references community_posts(id) on delete cascade,
  "user" text,
  owner_id uuid,
  text text,
  created_at timestamptz default now()
);

create table if not exists community_bids (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references community_posts(id) on delete cascade,
  "user" text,
  owner_id uuid,
  amount numeric,
  created_at timestamptz default now()
);

create table if not exists community_offers (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references community_posts(id) on delete cascade,
  "user" text,
  owner_id uuid,
  amount numeric,
  created_at timestamptz default now()
);

create table if not exists community_messages (
  id uuid primary key default gen_random_uuid(),
  sender text,
  recipient text,
  sender_id uuid,
  recipient_id uuid,
  subject text,
  body text,
  created_at timestamptz default now(),
  read_at timestamptz
);

create table if not exists community_roles (
  username text primary key,
  role text,
  created_at timestamptz default now()
);

create table if not exists community_bans (
  username text primary key,
  reason text,
  created_at timestamptz default now()
);

create table if not exists community_reports (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references community_posts(id) on delete cascade,
  reported_by text,
  reported_user text,
  owner_id uuid,
  reason text,
  created_at timestamptz default now()
);

-- Core app storage (server-side use)
create table if not exists wealthpulse_users (
  username text primary key,
  data jsonb,
  updated_at timestamptz default now()
);

create index if not exists idx_community_posts_created_at on community_posts(created_at desc);
create index if not exists idx_community_posts_created_by on community_posts(created_by);
create index if not exists idx_community_comments_post_id on community_comments(post_id);
create index if not exists idx_community_bids_post_id on community_bids(post_id);
create index if not exists idx_community_offers_post_id on community_offers(post_id);
create index if not exists idx_community_messages_recipient on community_messages(recipient);
create index if not exists idx_community_reports_post_id on community_reports(post_id);
create index if not exists idx_community_posts_owner_id on community_posts(owner_id);
create index if not exists idx_community_comments_owner_id on community_comments(owner_id);
create index if not exists idx_community_bids_owner_id on community_bids(owner_id);
create index if not exists idx_community_offers_owner_id on community_offers(owner_id);
create index if not exists idx_community_messages_sender_id on community_messages(sender_id);
create index if not exists idx_community_messages_recipient_id on community_messages(recipient_id);
create index if not exists idx_community_users_auth_id on community_users(auth_id);

-- Migrations for existing installations
alter table community_users add column if not exists auth_id uuid;
alter table community_users add column if not exists email text;
alter table community_posts add column if not exists owner_id uuid;
alter table community_posts add column if not exists grading_company text;
alter table community_posts add column if not exists grading_grade text;
alter table community_comments add column if not exists owner_id uuid;
alter table community_bids add column if not exists owner_id uuid;
alter table community_offers add column if not exists owner_id uuid;
alter table community_messages add column if not exists sender_id uuid;
alter table community_messages add column if not exists recipient_id uuid;
alter table community_reports add column if not exists owner_id uuid;

alter table community_users enable row level security;
alter table community_posts enable row level security;
alter table community_comments enable row level security;
alter table community_bids enable row level security;
alter table community_offers enable row level security;
alter table community_messages enable row level security;
alter table community_roles enable row level security;
alter table community_bans enable row level security;
alter table community_reports enable row level security;
alter table wealthpulse_users enable row level security;

create policy "community_users_select" on community_users
  for select using (auth.role() = 'authenticated');
create policy "community_users_insert" on community_users
  for insert with check (auth_id = auth.uid());
create policy "community_users_update" on community_users
  for update using (auth_id = auth.uid()) with check (auth_id = auth.uid());

create policy "community_posts_select" on community_posts
  for select using (auth.role() = 'authenticated');
create policy "community_posts_insert" on community_posts
  for insert with check (owner_id = auth.uid());
create policy "community_posts_update" on community_posts
  for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "community_posts_delete" on community_posts
  for delete using (owner_id = auth.uid());

create policy "community_comments_select" on community_comments
  for select using (auth.role() = 'authenticated');
create policy "community_comments_insert" on community_comments
  for insert with check (owner_id = auth.uid());
create policy "community_comments_update" on community_comments
  for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "community_comments_delete" on community_comments
  for delete using (owner_id = auth.uid());

create policy "community_bids_select" on community_bids
  for select using (auth.role() = 'authenticated');
create policy "community_bids_insert" on community_bids
  for insert with check (owner_id = auth.uid());
create policy "community_bids_update" on community_bids
  for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "community_bids_delete" on community_bids
  for delete using (owner_id = auth.uid());

create policy "community_offers_select" on community_offers
  for select using (auth.role() = 'authenticated');
create policy "community_offers_insert" on community_offers
  for insert with check (owner_id = auth.uid());
create policy "community_offers_update" on community_offers
  for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "community_offers_delete" on community_offers
  for delete using (owner_id = auth.uid());

create policy "community_messages_select" on community_messages
  for select using (sender_id = auth.uid() or recipient_id = auth.uid());
create policy "community_messages_insert" on community_messages
  for insert with check (sender_id = auth.uid());
create policy "community_messages_update" on community_messages
  for update using (sender_id = auth.uid() or recipient_id = auth.uid()) with check (sender_id = auth.uid() or recipient_id = auth.uid());
create policy "community_messages_delete" on community_messages
  for delete using (sender_id = auth.uid() or recipient_id = auth.uid());

create policy "community_roles_select" on community_roles
  for select using (auth.role() = 'authenticated');
create policy "community_roles_manage" on community_roles
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy "community_bans_select" on community_bans
  for select using (auth.role() = 'authenticated');
create policy "community_bans_manage" on community_bans
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy "community_reports_insert" on community_reports
  for insert with check (auth.role() = 'authenticated');
create policy "community_reports_select" on community_reports
  for select using (auth.role() = 'service_role');
create policy "community_reports_manage" on community_reports
  for update using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "community_reports_delete" on community_reports
  for delete using (auth.role() = 'service_role');

create policy "service role only users" on wealthpulse_users for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

-- OPTIONAL: Legacy fallback (service_role only for all community tables).
-- Uncomment the block below if you want to disable end-user access entirely.
/*
drop policy if exists "community_users_select" on community_users;
drop policy if exists "community_users_insert" on community_users;
drop policy if exists "community_users_update" on community_users;
drop policy if exists "community_posts_select" on community_posts;
drop policy if exists "community_posts_insert" on community_posts;
drop policy if exists "community_posts_update" on community_posts;
drop policy if exists "community_posts_delete" on community_posts;
drop policy if exists "community_comments_select" on community_comments;
drop policy if exists "community_comments_insert" on community_comments;
drop policy if exists "community_comments_update" on community_comments;
drop policy if exists "community_comments_delete" on community_comments;
drop policy if exists "community_bids_select" on community_bids;
drop policy if exists "community_bids_insert" on community_bids;
drop policy if exists "community_bids_update" on community_bids;
drop policy if exists "community_bids_delete" on community_bids;
drop policy if exists "community_offers_select" on community_offers;
drop policy if exists "community_offers_insert" on community_offers;
drop policy if exists "community_offers_update" on community_offers;
drop policy if exists "community_offers_delete" on community_offers;
drop policy if exists "community_messages_select" on community_messages;
drop policy if exists "community_messages_insert" on community_messages;
drop policy if exists "community_messages_update" on community_messages;
drop policy if exists "community_messages_delete" on community_messages;
drop policy if exists "community_roles_select" on community_roles;
drop policy if exists "community_roles_manage" on community_roles;
drop policy if exists "community_bans_select" on community_bans;
drop policy if exists "community_bans_manage" on community_bans;
drop policy if exists "community_reports_insert" on community_reports;
drop policy if exists "community_reports_select" on community_reports;
drop policy if exists "community_reports_manage" on community_reports;
drop policy if exists "community_reports_delete" on community_reports;

create policy "service role users" on community_users for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role posts" on community_posts for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role comments" on community_comments for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role bids" on community_bids for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role offers" on community_offers for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role messages" on community_messages for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role roles" on community_roles for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role bans" on community_bans for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy "service role reports" on community_reports for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
*/

-- OPTIONAL: Open community access (anon + authenticated).
-- Use this if you want anyone with the app to read/write Community data without signing in.
-- NOTE: Roles/Bans stay locked to service_role for safety.
/*
drop policy if exists "community_users_select" on community_users;
drop policy if exists "community_users_insert" on community_users;
drop policy if exists "community_users_update" on community_users;
drop policy if exists "community_posts_select" on community_posts;
drop policy if exists "community_posts_insert" on community_posts;
drop policy if exists "community_posts_update" on community_posts;
drop policy if exists "community_posts_delete" on community_posts;
drop policy if exists "community_comments_select" on community_comments;
drop policy if exists "community_comments_insert" on community_comments;
drop policy if exists "community_comments_update" on community_comments;
drop policy if exists "community_comments_delete" on community_comments;
drop policy if exists "community_bids_select" on community_bids;
drop policy if exists "community_bids_insert" on community_bids;
drop policy if exists "community_bids_update" on community_bids;
drop policy if exists "community_bids_delete" on community_bids;
drop policy if exists "community_offers_select" on community_offers;
drop policy if exists "community_offers_insert" on community_offers;
drop policy if exists "community_offers_update" on community_offers;
drop policy if exists "community_offers_delete" on community_offers;
drop policy if exists "community_messages_select" on community_messages;
drop policy if exists "community_messages_insert" on community_messages;
drop policy if exists "community_messages_update" on community_messages;
drop policy if exists "community_messages_delete" on community_messages;
drop policy if exists "community_reports_insert" on community_reports;
drop policy if exists "community_reports_select" on community_reports;
drop policy if exists "community_reports_manage" on community_reports;
drop policy if exists "community_reports_delete" on community_reports;

create policy "public_users_read" on community_users for select to anon, authenticated using (true);
create policy "public_users_insert" on community_users for insert to anon, authenticated with check (true);
create policy "public_users_update" on community_users for update to anon, authenticated using (true) with check (true);

create policy "public_posts_read" on community_posts for select to anon, authenticated using (true);
create policy "public_posts_insert" on community_posts for insert to anon, authenticated with check (true);
create policy "public_posts_update" on community_posts for update to anon, authenticated using (true) with check (true);
create policy "public_posts_delete" on community_posts for delete to anon, authenticated using (true);

create policy "public_comments_read" on community_comments for select to anon, authenticated using (true);
create policy "public_comments_insert" on community_comments for insert to anon, authenticated with check (true);
create policy "public_comments_update" on community_comments for update to anon, authenticated using (true) with check (true);
create policy "public_comments_delete" on community_comments for delete to anon, authenticated using (true);

create policy "public_bids_read" on community_bids for select to anon, authenticated using (true);
create policy "public_bids_insert" on community_bids for insert to anon, authenticated with check (true);
create policy "public_bids_update" on community_bids for update to anon, authenticated using (true) with check (true);
create policy "public_bids_delete" on community_bids for delete to anon, authenticated using (true);

create policy "public_offers_read" on community_offers for select to anon, authenticated using (true);
create policy "public_offers_insert" on community_offers for insert to anon, authenticated with check (true);
create policy "public_offers_update" on community_offers for update to anon, authenticated using (true) with check (true);
create policy "public_offers_delete" on community_offers for delete to anon, authenticated using (true);

create policy "public_messages_read" on community_messages for select to anon, authenticated using (true);
create policy "public_messages_insert" on community_messages for insert to anon, authenticated with check (true);
create policy "public_messages_update" on community_messages for update to anon, authenticated using (true) with check (true);
create policy "public_messages_delete" on community_messages for delete to anon, authenticated using (true);

create policy "public_reports_insert" on community_reports for insert to anon, authenticated with check (true);
create policy "reports_admin_read" on community_reports for select to service_role using (true);
create policy "reports_admin_update" on community_reports for update to service_role using (true) with check (true);
create policy "reports_admin_delete" on community_reports for delete to service_role using (true);
*/
