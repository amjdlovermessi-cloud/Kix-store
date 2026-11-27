-- Owner-managed granular staff access for KIX Store.
create table if not exists public.store_staff (
 email text primary key check (email=lower(email)),
 user_id uuid unique references auth.users(id) on delete cascade,
 permissions jsonb not null default '{"manage_products":false,"edit_prices":false,"manage_orders":false}'::jsonb check(jsonb_typeof(permissions)='object'),
 active boolean not null default true,
 created_by uuid references auth.users(id) on delete set null,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
alter table public.store_staff enable row level security;
revoke all on public.store_staff from anon,authenticated;
grant select on public.store_staff to authenticated;
drop policy if exists "staff read own assignment" on public.store_staff;
create policy "staff read own assignment" on public.store_staff for select to authenticated using(user_id=(select auth.uid()) or public.is_owner());

create or replace function public.has_staff_permission(p_permission text)
returns boolean language sql stable set search_path=public as $
 select public.is_owner() or exists(select 1 from public.store_staff s where s.user_id=(select auth.uid()) and s.active and coalesce((s.permissions->>p_permission)::boolean,false));
$$;
revoke all on function public.has_staff_permission(text) from public;
grant execute on function public.has_staff_permission(text) to authenticated;

create or replace function public.is_staff()
returns boolean language sql stable security definer set search_path=public as $$
 select public.is_owner() or exists(select 1 from public.store_staff s where s.user_id=(select auth.uid()) and s.active);
$$;
revoke all on function public.is_staff() from public;
grant execute on function public.is_staff() to anon,authenticated;

drop policy if exists "staff manage categories" on public.categories;
create policy "staff manage categories" on public.categories for all to authenticated using(public.has_staff_permission('manage_products')) with check(public.has_staff_permission('manage_products'));

drop policy if exists "staff manage products" on public.products;
create policy "staff add products" on public.products for insert to authenticated with check(public.has_staff_permission('manage_products'));
create policy "staff delete products" on public.products for delete to authenticated using(public.has_staff_permission('manage_products'));
create policy "staff update products" on public.products for update to authenticated using(public.has_staff_permission('manage_products') or public.has_staff_permission('edit_prices')) with check(public.has_staff_permission('manage_products') or public.has_staff_permission('edit_prices'));

create or replace function public.enforce_staff_product_fields()
returns trigger language plpgsql set search_path=public as $$
begin
 if not public.is_owner() and public.has_staff_permission('edit_prices') and not public.has_staff_permission('manage_products') then
  if (to_jsonb(new)-'price_iqd'-'updated_at') is distinct from (to_jsonb(old)-'price_iqd'-'updated_at') then
   raise exception 'ليس لديك صلاحية تعديل بيانات المنتج، يمكنك تعديل السعر فقط.';
  end if;
 end if;
 return new;
end; $$;
drop trigger if exists enforce_staff_product_fields on public.products;
create trigger enforce_staff_product_fields before update on public.products for each row execute function public.enforce_staff_product_fields();

drop policy if exists "staff read orders" on public.orders;
create policy "staff read orders" on public.orders for select to authenticated using(public.has_staff_permission('manage_orders'));
drop policy if exists "staff update orders" on public.orders;
create policy "staff update orders" on public.orders for update to authenticated using(public.has_staff_permission('manage_orders')) with check(public.has_staff_permission('manage_orders'));
drop policy if exists "staff read order items" on public.order_items;
create policy "staff read order items" on public.order_items for select to authenticated using(public.has_staff_permission('manage_orders'));

create or replace function public.enforce_staff_order_fields()
returns trigger language plpgsql set search_path=public as $$
begin
 if not public.is_owner() and (to_jsonb(new)-'status'-'updated_at') is distinct from (to_jsonb(old)-'status'-'updated_at') then
  raise exception 'يمكن للأدمن تعديل حالة الطلب فقط.';
 end if;
 return new;
end; $$;
drop trigger if exists enforce_staff_order_fields on public.orders;
create trigger enforce_staff_order_fields before update on public.orders for each row execute function public.enforce_staff_order_fields();

drop policy if exists "staff upload product images" on storage.objects;
create policy "staff upload product images" on storage.objects for insert to authenticated with check(bucket_id='product-images' and public.has_staff_permission('manage_products'));
drop policy if exists "staff update product images" on storage.objects;
create policy "staff update product images" on storage.objects for update to authenticated using(bucket_id='product-images' and public.has_staff_permission('manage_products')) with check(bucket_id='product-images' and public.has_staff_permission('manage_products'));
drop policy if exists "staff delete product images" on storage.objects;
create policy "staff delete product images" on storage.objects for delete to authenticated using(bucket_id='product-images' and public.has_staff_permission('manage_products'));
