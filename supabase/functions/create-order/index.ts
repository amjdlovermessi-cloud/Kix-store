import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Content-Type': 'application/json'
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: cors });
}

async function hashClientIp(ip: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(ip));
  return Array.from(new Uint8Array(signature), byte => byte.toString(16).padStart(2, '0')).join('');
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'Method not allowed' }, 405);

  try {
    const contentLength = Number(req.headers.get('content-length') || 0);
    if (contentLength > 32 * 1024) return json({ error: 'حجم الطلب أكبر من المسموح.' }, 413);

    const rawIp = req.headers.get('cf-connecting-ip')
      || req.headers.get('x-real-ip')
      || req.headers.get('x-forwarded-for')?.split(',')[0]?.trim();

    if (!rawIp) return json({ error: 'تعذر التحقق من مصدر الطلب. حاول بعد قليل.' }, 503);

    const supabaseUrl = Deno.env.get('SUPABASE_URL');
    const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!supabaseUrl || !serviceRoleKey) throw new Error('Server configuration is incomplete.');

    const supabase = createClient(supabaseUrl, serviceRoleKey);
    const ipHash = await hashClientIp(rawIp, serviceRoleKey);
    const { data: allowed, error: rateError } = await supabase.rpc('consume_order_rate_limit', {
      p_key_hash: ipHash,
      p_max_requests: 8,
      p_window_seconds: 600
    });

    if (rateError) {
      console.error('Rate limit check failed:', rateError.message);
      return json({ error: 'تعذر التحقق من الطلب حالياً. حاول بعد قليل.' }, 503);
    }
    if (allowed !== true) return json({ error: 'وصلت إلى الحد المؤقت للطلبات. انتظر 10 دقائق ثم حاول مجدداً.' }, 429);

    const body = await req.json();
    // Honeypot field: legitimate storefront clients leave this empty.
    if (String(body.website || '').trim()) return json({ error: 'تعذر تسجيل الطلب.' }, 400);

    const name = String(body.customer_name || '').trim();
    const phone = String(body.phone || '').trim();
    const email = String(body.email || '').trim();
    const notes = String(body.notes || '').trim().slice(0, 1000);
    const payment = String(body.payment_method || '');
    const items = Array.isArray(body.items) ? body.items : [];

    if (name.length < 2 || name.length > 100 || phone.length < 7 || phone.length > 30) {
      return json({ error: 'يرجى إدخال الاسم ورقم الهاتف بصورة صحيحة.' }, 400);
    }
    if (email.length > 254 || (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))) {
      return json({ error: 'البريد الإلكتروني غير صحيح.' }, 400);
    }
    if (!['asiacell', 'superqi', 'dizly'].includes(payment)) {
      return json({ error: 'طريقة الدفع غير معتمدة.' }, 400);
    }
    if (!items.length || items.length > 30) {
      return json({ error: 'السلة فارغة أو تحتوي على عدد كبير من المنتجات.' }, 400);
    }

    const quantities = new Map<string, number>();
    for (const item of items) {
      const id = String(item.product_id || '');
      const qty = Number(item.quantity);
      if (!/^[0-9a-f-]{36}$/i.test(id) || !Number.isInteger(qty) || qty < 1 || qty > 20) {
        return json({ error: 'بيانات أحد المنتجات غير صحيحة.' }, 400);
      }
      const nextQty = (quantities.get(id) || 0) + qty;
      if (nextQty > 20) return json({ error: 'الكمية الإجمالية للمنتج الواحد لا يمكن أن تتجاوز 20.' }, 400);
      quantities.set(id, nextQty);
    }

    const ids = [...quantities.keys()];
    const { data: products, error: pErr } = await supabase
      .from('products')
      .select('id,name,price_iqd,active')
      .in('id', ids);

    if (pErr) throw pErr;
    if (!products || products.length !== ids.length || products.some(p => !p.active)) {
      return json({ error: 'أحد المنتجات لم يعد متوفراً. حدّث السلة وحاول مجدداً.' }, 400);
    }

    const rows = products.map(p => ({
      product_id: p.id,
      product_name: p.name,
      quantity: quantities.get(p.id)!,
      unit_price_iqd: Number(p.price_iqd)
    }));
    const total = rows.reduce((sum, row) => sum + row.quantity * row.unit_price_iqd, 0);
    if (!Number.isSafeInteger(total) || total <= 0) return json({ error: 'تعذر حساب قيمة الطلب.' }, 400);

    const suffix = crypto.randomUUID().replaceAll('-', '').slice(0, 7).toUpperCase();
    const orderNumber = `KIX-${new Date().toISOString().slice(2, 10).replaceAll('-', '')}-${suffix}`;
    const { data: order, error: oErr } = await supabase
      .from('orders')
      .insert({
        order_number: orderNumber,
        customer_name: name,
        phone,
        email,
        notes,
        payment_method: payment,
        total_iqd: total,
        status: 'pending'
      })
      .select('id,order_number,total_iqd,status')
      .single();

    if (oErr) throw oErr;

    const { error: iErr } = await supabase.from('order_items').insert(
      rows.map(row => ({ ...row, order_id: order.id }))
    );
    if (iErr) {
      await supabase.from('orders').delete().eq('id', order.id);
      throw iErr;
    }

    return json({ order });
  } catch (err) {
    console.error('create-order failed:', err);
    return json({ error: err instanceof Error ? err.message : 'تعذر تسجيل الطلب.' }, 500);
  }
});
