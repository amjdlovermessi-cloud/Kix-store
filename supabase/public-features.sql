-- KIX public visit counter and moderated customer reviews.
-- Safe to run once in the Supabase SQL Editor; all statements are repeatable.

create table if not exists public.store_visit_events (
  visitor_token uuid not null,
  visit_day date not null default current_date,
  created_at timestamptz not null default now(),
  primary key (visitor_token, visit_day)
);

create table if not exists public.store_reviews (
  id uuid primary key default gen_random_uuid(),
  visitor_token uuid not null,
  display_name varchar(60) not null,
  rating integer not null check (rating between 1 and 5),
  comment varchar(700) not null,
  approved boolean not null default false,
  created_at timestamptz not null default now(),
  constraint store_reviews_name_length check (char_length(trim(display_name)) between 2 and 60),
  constraint store_reviews_comment_length check (char_length(trim(comment)) between 8 and 700)
);

create table if not exists public.store_review_limits (
  visitor_token uuid primary key,
  last_submitted_at timestamptz not null default now()
);

alter table public.store_visit_events enable row level security;
alter table public.store_reviews enable row level security;
alter table public.store_review_limits enable row level security;

drop policy if exists "public read approved store reviews" on public.store_reviews;
create policy "public read approved store reviews"
  on public.store_reviews for select to anon, authenticated
  using (approved = true or public.is_staff());

drop policy if exists "staff update store reviews" on public.store_reviews;
create policy "staff update store reviews"
  on public.store_reviews for update to authenticated
  using (public.is_staff()) with check (public.is_staff());

drop policy if exists "staff delete store reviews" on public.store_reviews;
create policy "staff delete store reviews"
  on public.store_reviews for delete to authenticated
  using (public.is_staff());

revoke all on public.store_visit_events from anon, authenticated;
revoke all on public.store_review_limits from anon, authenticated;
revoke insert on public.store_reviews from anon, authenticated;
grant select on public.store_reviews to anon, authenticated;
grant update, delete on public.store_reviews to authenticated;

create or replace function public.increment_store_visit(p_visitor_token uuid)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_visitor_token is null then return; end if;
  insert into public.store_visit_events(visitor_token, visit_day)
  values (p_visitor_token, current_date)
  on conflict (visitor_token, visit_day) do nothing;
end;
$$;

create or replace function public.get_public_store_stats()
returns table(visits bigint, orders bigint, ratings bigint, average_rating numeric)
language sql
stable
security definer
set search_path = public
as $$
  select
    (select count(*) from public.store_visit_events)::bigint,
    (select count(*) from public.orders where status in ('paid','processing','completed'))::bigint,
    (select count(*) from public.store_reviews where approved = true)::bigint,
    coalesce((select round(avg(rating)::numeric, 1) from public.store_reviews where approved = true), 0)::numeric;
$$;

create or replace function public.submit_store_review(
  p_visitor_token uuid,
  p_display_name text,
  p_rating integer,
  p_comment text
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_name text := trim(coalesce(p_display_name, ''));
  v_comment text := trim(coalesce(p_comment, ''));
  v_review_id uuid;
  v_allowed uuid;
begin
  if p_visitor_token is null then
    raise exception 'تعذر التحقق من المتصفح. حدّث الصفحة وحاول مجدداً.';
  end if;
  if char_length(v_name) < 2 or char_length(v_name) > 60 then
    raise exception 'الاسم يجب أن يكون بين حرفين و60 حرفاً.';
  end if;
  if p_rating is null or p_rating < 1 or p_rating > 5 then
    raise exception 'اختر تقييماً من نجمة إلى خمس نجوم.';
  end if;
  if char_length(v_comment) < 8 or char_length(v_comment) > 700 then
    raise exception 'التعليق يجب أن يكون بين 8 و700 حرف.';
  end if;

  insert into public.store_review_limits(visitor_token, last_submitted_at)
  values (p_visitor_token, now())
  on conflict (visitor_token) do update
    set last_submitted_at = now()
    where public.store_review_limits.last_submitted_at < now() - interval '24 hours'
  returning visitor_token into v_allowed;

  if v_allowed is null then
    raise exception 'يمكنك إرسال تقييم واحد كل 24 ساعة من هذا المتصفح.';
  end if;

  insert into public.store_reviews(visitor_token, display_name, rating, comment)
  values (p_visitor_token, v_name, p_rating, v_comment)
  returning id into v_review_id;

  return v_review_id;
end;
$$;

revoke all on function public.increment_store_visit(uuid) from public;
revoke all on function public.get_public_store_stats() from public;
revoke all on function public.submit_store_review(uuid, text, integer, text) from public;
grant execute on function public.increment_store_visit(uuid) to anon, authenticated;
grant execute on function public.get_public_store_stats() to anon, authenticated;
grant execute on function public.submit_store_review(uuid, text, integer, text) to anon, authenticated;
