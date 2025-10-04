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