# Kix Store

متجر Kix Store مستقل بواجهة GitHub Pages وخلفية Supabase.

## تحديث حماية الطلبات

يتضمن هذا التحديث:
- تحديد معدل إنشاء الطلبات إلى 8 محاولات لكل عنوان IP خلال 10 دقائق.
- تخزين بصمة HMAC لعنوان IP بدلاً من تخزين عنوان IP نفسه.
- حقل honeypot مخفي لالتقاط بعض الطلبات الآلية.
- تحديد حجم الطلب والتحقق من البريد الإلكتروني والكميات المجمعة.

### خطوات التفعيل المطلوبة في Supabase

1. افتح مشروع Supabase ثم SQL Editor.
2. نفّذ كامل الملف `security/order-rate-limit.sql` مرة واحدة.
3. انشر الدالة المحدّثة من جذر المستودع بعد ربط Supabase CLI بالمشروع:

```bash
supabase link --project-ref xtewgkfwivdonaaozbkc
supabase functions deploy create-order --no-verify-jwt
```

الدالة تستخدم `SUPABASE_SERVICE_ROLE_KEY` من بيئة Supabase على الخادم فقط. لا تضع هذا المفتاح في GitHub أو ملفات الواجهة.

### النشر

كل دفع إلى فرع `main` يشغّل GitHub Actions لنشر GitHub Pages. خطوة النشر تطبق تعديل honeypot على ملفات الموقع المستخرجة من ZIP.

## الروابط

- المتجر: https://amjdlovermessi-cloud.github.io/Kix-store/
- لوحة الإدارة: https://amjdlovermessi-cloud.github.io/Kix-store/owner.html


## Customer experience additions (redesign branch)

- Optional customer accounts using Supabase Auth email/password; browsing and guest checkout remain available.
- Signed-in customers can view purchase count, purchased units, spend, membership age, and their order history.
- Daily visit tracking attributes registered visits to the account and keeps guest visits anonymous.
- Owner-only Top dashboards rank registered visitors, buyers, spenders, and best-selling products.
- Owner-managed announcement ticker messages, enabled state, and movement speed.

The additive database migration is applied to the connected Supabase project. The storefront UI is added by the GitHub Pages deployment patch and remains isolated on `redesign-foundation` until reviewed and merged.
