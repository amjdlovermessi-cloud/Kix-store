(() => {
  const $ = (s, root=document) => root.querySelector(s);
  const notice = $("#notice"), dashboard = $("#dashboard");
  const config = window.KIX_CONFIG || {};
  if (!window.supabase || !config.supabaseUrl || !config.supabaseAnonKey) {
    notice.classList.add("error"); notice.textContent = "تعذر تحميل إعدادات المتجر. ارجع إلى لوحة المالك وحاول مرة أخرى."; return;
  }
  const client = window.supabase.createClient(config.supabaseUrl, config.supabaseAnonKey);
  let session = null, products = [], categories = [], offset = 0, limit = 50, nextOffset = null, imported = new Set();

  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const money = value => Number(value || 0).toFixed(2) + " USD";
  const inputLabel = p => {
    const t = p.input?.type || "none";
    const labels = {none:"لا يحتاج",quantity:"كمية",activation_identifier:"معرّف تفعيل",email:"بريد إلكتروني"};
    const req = Array.isArray(p.input?.required) ? p.input.required.join("، ") : "";
    return (labels[t] || t) + (req ? " · مطلوب: " + req : "");
  };
  function availability(p) {
    if (p.available === true) return ["متوفر", "yes"];
    if (p.available === false) return ["غير متوفر", "no"];
    return ["غير مؤكد", ""];
  }
  function fillCategories(select) {
    select.innerHTML = '<option value="">اختر القسم</option>' + categories.map(c => '<option value="'+esc(c.id)+'">'+esc(c.name)+'</option>').join("");
  }
  function render() {
    const root = $("#products"), template = $("#productTemplate");
    root.innerHTML = "";
    const query = $("#search").value.trim().toLowerCase();
    const shown = products.filter(p => [p.name,p.description,p.category?.name,p.id].join(" ").toLowerCase().includes(query));
    if (!shown.length) { root.innerHTML = '<div class="empty">ماكو منتجات تطابق البحث ضمن هذه الصفحة.</div>'; return; }
    shown.forEach(p => {
      const node = template.content.firstElementChild.cloneNode(true);
      const [status, cls] = availability(p);
      $(".category",node).textContent = p.category?.name || p.category?.key || "بدون تصنيف";
      $(".name",node).textContent = p.name || "منتج بدون اسم";
      $(".description",node).textContent = p.description || "لا يوجد وصف من المورد.";
      $(".availability",node).textContent = status;
      if (cls) $(".availability",node).classList.add(cls);
      $(".cost",node).textContent = money(p.price);
      $(".warranty",node).textContent = Number(p.warranty_days || 0) + " يوم";
      $(".inputType",node).textContent = inputLabel(p);
      $(".inputNote",node).textContent = p.input?.type === "activation_identifier" ? "سيحتاج الزبون إدخال معرّف اللاعب أو الحساب عند الطلب." : p.input?.type === "email" ? "سيحتاج الزبون إدخال بريد إلكتروني." : p.input?.type === "quantity" ? "الكمية: " + (p.input.min_quantity || 1) + " إلى " + (p.input.max_quantity || 1) : "";
      $(".supplierId",node).textContent = p.id;
      fillCategories($(".categorySelect",node));
      if (imported.has(p.id)) { $(".importButton",node).disabled=true; $(".importButton",node).textContent="تم الاستيراد"; }
      $(".importButton",node).addEventListener("click", () => importProduct(p,node));
      root.appendChild(node);
    });
  }
  async function callCatalog() {
    const res = await fetch(config.supabaseUrl + "/functions/v1/jrk-catalog?offset="+offset+"&limit="+limit, {
      method:"GET", headers:{apikey:config.supabaseAnonKey, Authorization:"Bearer "+session.access_token}
    });
    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data.error || "تعذر تحميل كتالوج المورد.");
    const wallet = data.me?.wallet || {};
    $("#walletBalance").textContent = wallet.balance ?? "—";
    $("#walletHeld").textContent = wallet.held ?? "—";
    $("#walletCurrency").textContent = wallet.currency || "USD";
    $("#accountStatus").textContent = "حالة الحساب: " + (data.me?.reseller?.status || "—");
    products = Array.isArray(data.products?.data) ? data.products.data : [];
    categories = Array.isArray(data.categories) ? data.categories : [];
    const pagination = data.products?.pagination || {};
    $("#totalProducts").textContent = pagination.total ?? products.length;
    nextOffset = pagination.next_offset ?? null;
    $("#prev").disabled = offset <= 0;
    $("#next").disabled = nextOffset === null;
    $("#pageInfo").textContent = "عرض " + (products.length ? offset+1 : 0) + " - " + (offset+products.length) + " من " + (pagination.total ?? products.length);
    render();
  }
  async function importProduct(p,node) {
    const button = $(".importButton",node), result = $(".result",node);
    const category_id = $(".categorySelect",node).value;
    const price_iqd = Number($(".retail",node).value);
    const custom = $(".customDescription",node).value.trim();
    if (!category_id || !Number.isSafeInteger(price_iqd) || price_iqd < 1) {
      result.className="result error"; result.textContent="اختر قسم المتجر وأدخل سعر البيع بالدينار أولاً."; return;
    }
    if (!confirm("تأكيد استيراد «"+p.name+"» إلى كتالوج KIX؟\nلن يتم شراء المنتج من المورد. المنتجات غير المؤكدة ستُحفظ كمسودة غير منشورة.")) return;
    button.disabled=true; button.textContent="جارٍ الاستيراد...";
    result.className="result"; result.textContent="";
    try {
      const res = await fetch(config.supabaseUrl + "/functions/v1/jrk-import", {
        method:"POST",
        headers:{apikey:config.supabaseAnonKey, Authorization:"Bearer "+session.access_token, "Content-Type":"application/json"},
        body:JSON.stringify({
          supplier_product_id:p.id, name:p.name, description:custom || p.description || "",
          category_id, price_iqd, image_url:""
        })
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data.error || "فشل الاستيراد.");
      imported.add(p.id);
      button.textContent=data.published ? "تم الاستيراد والنشر" : "تم الحفظ كمسودة";
      result.textContent=data.published ? "تمت إضافة المنتج إلى المتجر وهو مفعّل لأن المورد أكد توفره." : "تمت إضافته كمسودة غير منشورة لأن التوفر غير مؤكد.";
    } catch(e) {
      button.disabled=false; button.textContent="استيراد إلى المتجر";
      result.className="result error"; result.textContent=e.message;
    }
  }
  async function init() {
    const {data,error}=await client.auth.getSession();
    session=data?.session;
    if (error || !session) {
      notice.classList.add("error");
      notice.innerHTML='سجّل دخولك أولاً من <a href="owner.html" style="color:#ff7b86">لوحة المالك</a> ثم ارجع لهذه الصفحة.';
      return;
    }
    const {data:userData}=await client.auth.getUser();
    const {data:profile}=await client.from("profiles").select("role").eq("id",userData.user.id).maybeSingle();
    if (profile?.role !== "owner") {
      notice.classList.add("error"); notice.textContent="هذه الصفحة مخصصة لحساب مالك المتجر فقط."; return;
    }
    notice.hidden=true; dashboard.hidden=false;
    await callCatalog();
  }
  async function importAllProducts() {
    const button=$("#importAll"), result=$("#bulkResult");
    if(!confirm("تأكيد استيراد جميع منتجات Jrk AI إلى KIX Store؟\\nسيتم تطبيق هامش الربح المتفق عليه وتحويل الأسعار إلى الدينار. المنتجات غير المتوفرة ستُحفظ كمسودات. لن يتم شراء أي منتج من المورد.")) return;
    button.disabled=true; button.textContent="جارٍ استيراد جميع المنتجات...";
    result.hidden=false; result.className="notice"; result.textContent="يتم جلب كتالوج المورد واستيراد المنتجات على دفعات. لا تغلق الصفحة.";
    try {
      const res=await fetch(config.supabaseUrl+"/functions/v1/jrk-import-all",{
        method:"POST",
        headers:{apikey:config.supabaseAnonKey,Authorization:"Bearer "+session.access_token,"Content-Type":"application/json"},
        body:"{}"
      });
      const data=await res.json();
      if(!res.ok||!data.ok) throw new Error(data.error||"تعذر استيراد الكتالوج.");
      const s=data.summary||{};
      result.textContent="اكتمل الاستيراد: "+s.imported+" منتج جديد. المنشور: "+s.active+". المسودات غير المنشورة: "+s.drafts+". موجود مسبقاً: "+s.skipped_existing+". غير صالح: "+s.invalid+". أخطاء: "+(s.errors?.length||0)+".";
      if(s.errors?.length) result.textContent+=" أول الأخطاء: "+s.errors.slice(0,3).join(" | ");
      await callCatalog();
    } catch(e) {
      result.className="notice error"; result.textContent="فشل الاستيراد: "+e.message;
    } finally {
      button.disabled=false; button.textContent="إعادة فحص واستيراد المنتجات غير المستوردة";
    }
  }
  $("#refresh").addEventListener("click",async()=>{ $("#refresh").disabled=true; try{await callCatalog()}catch(e){notice.hidden=false;notice.classList.add("error");notice.textContent=e.message} finally{$("#refresh").disabled=false} });
  $("#search").addEventListener("input",render);\n  $("#importAll").addEventListener("click",importAllProducts);
  $("#prev").addEventListener("click",async()=>{offset=Math.max(0,offset-limit);try{await callCatalog()}catch(e){notice.hidden=false;notice.classList.add("error");notice.textContent=e.message}});
  $("#next").addEventListener("click",async()=>{if(nextOffset===null)return;offset=nextOffset;try{await callCatalog()}catch(e){notice.hidden=false;notice.classList.add("error");notice.textContent=e.message}});
  init().catch(e=>{notice.classList.add("error");notice.textContent=e.message});
})();