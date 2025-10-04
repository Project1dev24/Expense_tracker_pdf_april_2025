-- Enable extension
create extension if not exists "uuid-ossp";

-- Profiles table
create table if not exists profiles (
  id uuid references auth.users on delete cascade not null primary key,
  email text unique not null,
  name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  last_seen timestamp with time zone default timezone('utc'::text, now()) not null,
  linked_unregistered_names text not null default '[]'
);

-- Trips table
create table if not exists trips (
  id uuid default uuid_generate_v4() primary key,
  name varchar(100) not null,
  description text,
  start_date timestamp with time zone not null,
  end_date timestamp with time zone not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  admin_id uuid references auth.users on delete cascade not null,
  participants jsonb not null default '[]',
  advances jsonb not null default '{}',
  general_payments jsonb not null default '[]'
);

-- Expenses table
create table if not exists expenses (
  id uuid default uuid_generate_v4() primary key,
  description varchar(200) not null,
  amount double precision not null,
  currency varchar(3) default 'INR',
  category varchar(50),
  date timestamp with time zone default timezone('utc'::text, now()) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  split_method varchar(20) default 'equal',
  payer_id text not null,
  trip_id uuid references trips on delete cascade not null,
  participants jsonb not null default '[]',
  shares jsonb not null default '{}',
  items jsonb
);

-- Unregistered participants
create table if not exists unregistered_participants (
  id uuid default uuid_generate_v4() primary key,
  name varchar(100) not null,
  trip_id uuid references trips on delete cascade not null,
  linked_user_id uuid references auth.users on delete set null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table profiles enable row level security;
alter table trips enable row level security;
alter table expenses enable row level security;
alter table unregistered_participants enable row level security;

-- Policies for profiles
create policy "Users can view their own profile" on profiles
  for select using (auth.uid() = id);

create policy "Users can update their own profile" on profiles
  for update using (auth.uid() = id);

create policy "Users can insert their own profile" on profiles
  for insert with check (auth.uid() = id);

-- Policies for trips
create policy "Users can view trips they are part of" on trips
  for select using (
    auth.uid() = admin_id 
    or participants ? auth.uid()::text
  );

create policy "Users can create trips" on trips
  for insert with check (auth.uid() = admin_id);

create policy "Trip admins can update their trips" on trips
  for update using (auth.uid() = admin_id);

create policy "Trip admins can delete their trips" on trips
  for delete using (auth.uid() = admin_id);

-- Policies for expenses
create policy "Users can view expenses for trips they are part of" on expenses
  for select using (
    exists (
      select 1 from trips 
      where trips.id = expenses.trip_id 
      and (trips.admin_id = auth.uid() or trips.participants ? auth.uid()::text)
    )
  );

create policy "Trip admins can create expenses" on expenses
  for insert with check (
    exists (
      select 1 from trips 
      where trips.id = expenses.trip_id 
      and trips.admin_id = auth.uid()
    )
  );

create policy "Trip admins can update expenses" on expenses
  for update using (
    exists (
      select 1 from trips 
      where trips.id = expenses.trip_id 
      and trips.admin_id = auth.uid()
    )
  );

create policy "Trip admins can delete expenses" on expenses
  for delete using (
    exists (
      select 1 from trips 
      where trips.id = expenses.trip_id 
      and trips.admin_id = auth.uid()
    )
  );

-- Policies for unregistered participants
create policy "Users can view unregistered participants for trips they are part of" on unregistered_participants
  for select using (
    exists (
      select 1 from trips 
      where trips.id = unregistered_participants.trip_id 
      and (trips.admin_id = auth.uid() or trips.participants ? auth.uid()::text)
    )
  );

create policy "Trip admins can manage unregistered participants" on unregistered_participants
  for all using (
    exists (
      select 1 from trips 
      where trips.id = unregistered_participants.trip_id 
      and trips.admin_id = auth.uid()
    )
  );

-- Function to handle new user creation
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'name', new.email)
  );
  return new;
end;
$$;

-- Trigger for new user creation
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();