import { createClient } from "npm:@supabase/supabase-js@2";
const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, apikey, content-type, x-client-info","Access-Control-Allow-Methods":"GET, POST, PATCH, DELETE, OPTIONS"};
const json=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json"}});
const permissionKeys=["manage_products","edit_prices","manage_orders"];
const normalizePermissions=(value:Record<string,unknown>={})=>Object.fromEntries(permissionKeys.map(key=>[key,value[key]===true]));
Deno.serve(async(req:Request)=>{
 if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
 try{
  const url=Deno.env.get("SUPABASE_URL")!,anonKey=Deno.env.get("SUPABASE_ANON_KEY")!,serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const authHeader=req.headers.get("Authorization")||"",token=authHeader.replace(/^Bearer\s+/i,"");
  if(!token||token===authHeader)return json({error:"يلزم تسجيل الدخول."},401);
  const caller=createClient(url,anonKey,{auth:{persistSession:false,autoRefreshToken:false},global:{headers:{Authorization:"Bearer "+token}}});
  const {data:callerData,error:authError}=await caller.auth.getUser(token);
  if(authError||!callerData.user)return json({error:"جلسة الدخول غير صالحة."},401);
  const admin=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:ownerProfile,error:ownerError}=await admin.from("profiles").select("role").eq("id",callerData.user.id).maybeSingle();
  if(ownerError||ownerProfile?.role!=="owner")return json({error:"هذه العملية متاحة لمالك المتجر فقط."},403);
  const findUser=async(email:string)=>{for(let page=1;page<=10;page++){const {data,error}=await admin.auth.admin.listUsers({page,perPage:1000});if(error)throw error;const found=data.users.find(u=>(u.email||"").toLowerCase()===email);if(found)return found;if(data.users.length<1000)break;}return null;};
  if(req.method==="GET"){const {data,error}=await admin.from("store_staff").select("email,user_id,permissions,active,created_at").order("created_at",{ascending:false});if(error)throw error;return json({staff:data||[]});}
  const body=await req.json().catch(()=>({})),email=String(body.email||"").trim().toLowerCase();
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return json({error:"أدخل بريداً إلكترونياً صحيحاً."},400);
  if(email===(callerData.user.email||"").toLowerCase())return json({error:"لا يمكنك إضافة أو سحب صلاحيات حساب المالك."},400);
  if(req.method==="DELETE"){const {error}=await admin.from("store_staff").delete().eq("email",email);if(error)throw error;const user=await findUser(email);if(user)await admin.from("profiles").update({role:"customer"}).eq("id",user.id).neq("role","owner");return json({success:true});}
  if(req.method!=="POST"&&req.method!=="PATCH")return json({error:"طريقة الطلب غير مدعومة."},405);
  const permissions=normalizePermissions(body.permissions||{});let user=await findUser(email),invited=false;
  if(!user){const {data,error}=await admin.auth.admin.inviteUserByEmail(email);if(error)throw error;user=data.user;invited=true;}
  if(!user)throw new Error("تعذر إنشاء حساب الدعوة.");
  const {data:targetProfile}=await admin.from("profiles").select("role").eq("id",user.id).maybeSingle();
  if(targetProfile?.role==="owner")return json({error:"لا يمكن تحويل حساب مالك المتجر إلى أدمن."},400);
  const {error:profileError}=await admin.from("profiles").upsert({id:user.id,role:"manager"},{onConflict:"id"});if(profileError)throw profileError;
  const {error}=await admin.from("store_staff").upsert({email,user_id:user.id,permissions,active:true,created_by:callerData.user.id,updated_at:new Date().toISOString()},{onConflict:"email"});if(error)throw error;
  return json({success:true,email,user_id:user.id,invited});
 }catch(error){console.error("manage-store-staff:",error);return json({error:error instanceof Error?error.message:"حدث خطأ غير متوقع."},400);}
});