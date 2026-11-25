import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
const cors={
  'Access-Control-Allow-Origin':'*',
  'Access-Control-Allow-Headers':'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods':'POST, OPTIONS',
  'Content-Type':'application/json'
};
const reply=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers:cors});
function baghdadDay(){
  const parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Baghdad',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const get=(type:string)=>parts.find(p=>p.type===type)?.value||'';
  return `${get('year')}-${get('month')}-${get('day')}`;
}
Deno.serve(async(req)=>{
  if(req.method==='OPTIONS')return new Response('ok',{headers:cors});
  if(req.method!=='POST')return reply({error:'Method not allowed'},405);
  try{
    const body=await req.json();
    const visitorToken=String(body.visitor_token||'');
    if(!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(visitorToken))return reply({error:'Invalid visitor token'},400);
    const url=Deno.env.get('SUPABASE_URL'),service=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if(!url||!service)throw new Error('Server configuration is incomplete.');
    const admin=createClient(url,service,{auth:{persistSession:false,autoRefreshToken:false}});
    let userId:string|null=null;
    const authorization=req.headers.get('Authorization')||'';
    const token=authorization.replace(/^Bearer\\s+/i,'');
    if(token){
      const {data,error}=await admin.auth.getUser(token);
      if(!error&&data.user&&!data.user.is_anonymous)userId=data.user.id;
    }
    const row={visitor_token:visitorToken,visit_day:baghdadDay(),...(userId?{user_id:userId}:{})};
    const {error}=await admin.from('store_visit_events').insert(row);
    if(error&&error.code!=='23505')throw error;
    return reply({success:true,recorded:!error});
  }catch(error){
    console.error('track-store-visit failed:',error);
    return reply({error:'تعذر تسجيل الزيارة.'},500);
  }
});