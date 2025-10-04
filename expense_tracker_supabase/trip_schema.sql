-- Trip schema for expense tracker application
-- This schema focuses specifically on the trips functionality

-- Enable required extensions
create extension if not exists "uuid-ossp";

-- Create trips table with proper structure
create table if not exists trips (
  id uuid default uuid_generate_v4() primary key,
  name varchar(100) not null,
  description text,
  start_date timestamp with time zone not null,
  end_date timestamp with time zone not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  admin_id uuid references auth.users on delete cascade not null,
  participants jsonb not null default '[]'
);

-- Enable Row Level Security for trips table
alter table trips enable row level security;

-- Create RLS policies for trips
-- Users can view trips they are part of (admin or participant)
create policy "Users can view trips they are part of" on trips
  for select using (
    auth.uid() = admin_id 
    or participants ? auth.uid()::text
  );

-- Users can create trips (must be the admin)
create policy "Users can create trips" on trips
  for insert with check (auth.uid() = admin_id);

-- Trip admins can update their trips
create policy "Trip admins can update their trips" on trips
  for update using (auth.uid() = admin_id);

-- Trip admins can delete their trips
create policy "Trip admins can delete their trips" on trips
  for delete using (auth.uid() = admin_id);

-- Grant necessary permissions
grant usage on schema public to anon, authenticated;
grant all on table trips to anon, authenticated;