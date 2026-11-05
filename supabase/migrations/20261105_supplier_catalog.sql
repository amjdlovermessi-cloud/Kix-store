-- KIX STORE supplier catalog import (reviewed 2026-11-05)
-- Prices include the agreed resale margin and are stored in IQD.
-- This migration is intentionally not auto-run by GitHub Pages deployment.
insert into public.products(name,description,price_iqd,image_url,badge,active,sort_order,category_id)
select v.name,v.description,v.price_iqd,v.image_url,v.badge,true,v.sort_order,c.id
from (values
('Minecraft Legends PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',34250,'assets/categories/ps5.webp','متوفر لدى المورد',101,'ps5'),
('Resonance: A Plague Tale Legacy PS5','نسخة رقمية لمنصة PS5. آلية التسليم عبر حساب المورد المشترك، ويُمنع استخدام الحساب على أكثر من جهاز وفق الشروط المنشورة.',60250,'assets/categories/ps5.webp','متوفر لدى المورد',102,'ps5'),
('Split Fiction PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',46250,'assets/categories/ps5.webp','متوفر لدى المورد',103,'ps5'),
('Slay the Spire PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',20500,'assets/categories/ps5.webp','متوفر لدى المورد',104,'ps5'),
('Black Myth: Wukong PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',60250,'assets/categories/ps5.webp','متوفر لدى المورد',105,'ps5'),
('First Light PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',52000,'assets/categories/ps5.webp','متوفر لدى المورد',106,'ps5'),
('ARK Raiders PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',34250,'assets/categories/ps5.webp','متوفر لدى المورد',107,'ps5'),
('Tekken 7 PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',12500,'assets/categories/ps5.webp','متوفر لدى المورد',108,'ps5'),
('Sea of Thieves PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',30250,'assets/categories/ps5.webp','متوفر لدى المورد',109,'ps5'),
('Hell is Us PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',26250,'assets/categories/ps5.webp','متوفر لدى المورد',110,'ps5'),
('SnowRunner PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',26000,'assets/categories/ps5.webp','متوفر لدى المورد',111,'ps5'),
('Ghost of Yōtei PS5','نسخة رقمية لمنصة PS5 عبر حساب مشترك بحسب شروط المورد. استخدام جهاز واحد، وضمان المورد المعلن 6 أشهر.',72250,'assets/categories/ps5.webp','متوفر لدى المورد',112,'ps5'),
('GTA 6 PS5','منتج رقمي لمنصة PS5. نوع التسليم والمنطقة والتوفر النهائي تُؤكد عند الشراء من المورد.',80250,'assets/categories/gta.webp','تحقق من التوفر عند الطلب',113,'gta'),
('EA SPORTS FC 27 PS5','منتج رقمي لمنصة PS5. نوع التسليم والمنطقة والتوفر النهائي تُؤكد عند الشراء من المورد.',64000,'assets/categories/fc.webp','تحقق من التوفر عند الطلب',114,'fc'),
('PC 200 Games Bundle','حزمة 200 لعبة PC أصلية. تعمل بنمط أوفلاين على جهاز واحد، ولا يجوز مشاركة الحساب، وفق شروط المورد.',4000,'assets/categories/steam.webp','PC · Offline',115,'steam'),
('PC Game Pass 1 Month','اشتراك PC Game Pass لمدة شهر. حساب مخصص يمكن تغيير بياناته بحسب وصف المورد، والتفعيل رقمي.',12450,'assets/categories/xbox.webp','PC · شهر',116,'xbox'),
('PC Simulation Games Bundle','حزمة ألعاب محاكاة PC تضم أكثر من 77 لعبة. أوفلاين لجهاز واحد، ولا تصلح لأجهزة PS أو Xbox وفق شروط المورد.',8000,'assets/categories/steam.webp','PC · Offline',117,'steam')
) as v(name,description,price_iqd,image_url,badge,sort_order,slug)
join public.categories c on c.slug=v.slug
where not exists(select 1 from public.products p where lower(p.name)=lower(v.name));
