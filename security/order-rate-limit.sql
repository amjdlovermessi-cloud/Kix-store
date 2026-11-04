-- Kix Store: database-backed checkout rate limit.
-- Run once in Supabase SQL Editor before deploying the updated Edge Function.

create table if not exists public.order_rate_limits (
  key_hash text primary key,
  window_started_at timestamptz not null,
  request_count integer not null check (request_count >= 1),
  updated_at timestamptz not null default now()
);

create index if not exists order_rate_limits_updated_at_idx
  on public.order_rate_limits (updated_at);

alter table public.order_rate_limits enable row level security;
revoke all on public.order_rate_limits from anon, authenticated, public;
grant all on public.order_rate_limits to service_role;

create or replace function public.consume_order_rate_limit(
  p_key_hash text,
  p_max_requests integer default 8,
  p_window_seconds integer default 600
)
returns boolean
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_now timestamptz := clock_timestamp();
  v_count integer;
begin
  if p_key_hash is null or length(p_key_hash) <> 64
     or p_max_requests < 1 or p_max_requests > 100
     or p_window_seconds < 30 or p_window_seconds > 86400 then
    raise exception 'Invalid rate-limit parameters';
  end if;

  insert into public.order_rate_limits (key_hash, window_started_at, request_count, updated_at)
  values (p_key_hash, v_now, 1, v_now)
  on conflict (key_hash) do update
    set window_started_at = case
          when public.order_rate_limits.window_started_at
               <= v_now - make_interval(secs => p_window_seconds)
          then v_now
          else public.order_rate_limits.window_started_at
        end,
        request_count = case
          when public.order_rate_limits.window_started_at
               <= v_now - make_interval(secs => p_window_seconds)
          then 1
          else public.order_rate_limits.request_count + 1
        end,
        updated_at = v_now
  returning request_count into v_count;

  -- Opportunistically discard old hashes to keep the table small.
  delete from public.order_rate_limits
  where updated_at < v_now - interval '2 days';

  return v_count <= p_max_requests;
end;
$$;

revoke all on function public.consume_order_rate_limit(text, integer, integer) from public, anon, authenticated;
grant execute on function public.consume_order_rate_limit(text, integer, integer) to service_role;
