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