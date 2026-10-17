'use strict';
const config=window.CAMPUSFIX_CONFIG;
const api=config.apiBase.replace(/\/$/,'');
let accessToken='';
const $=s=>document.querySelector(s);
function message(target,text,error=false){target.hidden=false;target.textContent=text;target.className='message '+(error?'error':'success');}
async function cognitoLogin(email,password){
  const url=`https://cognito-idp.${config.region}.amazonaws.com/`;
  const res=await fetch(url,{method:'POST',headers:{'Content-Type':'application/x-amz-json-1.1',
    'X-Amz-Target':'AWSCognitoIdentityProviderService.InitiateAuth'},body:JSON.stringify({AuthFlow:'USER_PASSWORD_AUTH',ClientId:config.cognitoClientId,AuthParameters:{USERNAME:email,PASSWORD:password}})});
  const data=await res.json();
  if(!res.ok) throw Error(data.message || 'Sign-in failed');
  if(data.ChallengeName) throw Error('This account requires a password update or other challenge. Complete that in Cognito before signing in.');
  if(!data.AuthenticationResult?.AccessToken) throw Error('No access token was issued');
  return data.AuthenticationResult.AccessToken;
}
async function req(path,options={}){
  const res=await fetch(api+path,{...options,headers:{'Content-Type':'application/json',Authorization:'Bearer '+accessToken,...(options.headers||{})}});
  const data=await res.json().catch(()=>({error:'Invalid response'}));
  if(!res.ok)throw Error(data.error || `HTTP ${res.status}`);
  return data;
}
$('#loginForm').addEventListener('submit',async event=>{
  event.preventDefault();$('#loginMessage').hidden=true;
  try {
    accessToken=await cognitoLogin($('#staffEmail').value.trim(),$('#staffPassword').value);
    $('#staffPassword').value='';
    $('#loginPanel').hidden=true;$('#dashboard').hidden=false;
    await loadIssues();
  }catch(err){accessToken='';$('#dashboard').hidden=true;$('#loginPanel').hidden=false;message($('#loginMessage'),err.message,true);}
});
$('#logoutBtn').addEventListener('click',()=>{accessToken='';$('#dashboard').hidden=true;$('#loginPanel').hidden=false;$('#issuesBody').replaceChildren();});
$('#refreshBtn').addEventListener('click',loadIssues);
$('#statusFilter').addEventListener('change',loadIssues);
async function loadIssues(){
  const target=$('#dashboardMessage');target.hidden=true;
  try{
    const status=$('#statusFilter').value;
    const query=status?('?status='+encodeURIComponent(status)):'';
    const data=await req('/admin/issues'+query);
    const counts={open:0,in_progress:0,resolved:0};
    for(const issue of data.items){counts[issue.status]=(counts[issue.status]||0)+1;}
    $('#openCount').textContent=counts.open;$('#progressCount').textContent=counts.in_progress;$('#resolvedCount').textContent=counts.resolved;
    const body=$('#issuesBody');body.replaceChildren();
    if(!data.items.length){const row=document.createElement('tr');const cell=document.createElement('td');cell.colSpan=5;cell.textContent='No maintenance issues found.';row.append(cell);body.append(row);}
    for(const issue of data.items){
      const tr=document.createElement('tr');
      const a=document.createElement('td');const short=document.createElement('strong');short.textContent=issue.issue_id.slice(0,14)+'…';
      const date=document.createElement('small');date.textContent=new Date(issue.created_at).toLocaleDateString();a.append(short,document.createElement('br'),date);a.title=issue.issue_id;
      const b=document.createElement('td');const title=document.createElement('strong');title.textContent=issue.title;const loc=document.createElement('small');loc.textContent=issue.location;b.append(title,document.createElement('br'),loc);
      const c=document.createElement('td');c.textContent=issue.priority;
      const d=document.createElement('td');const select=document.createElement('select');select.setAttribute('aria-label','Status for '+issue.issue_id);
      for(const [value,label] of [['open','Open'],['in_progress','In progress'],['resolved','Resolved']]){const opt=document.createElement('option');opt.value=value;opt.textContent=label;select.append(opt);}select.value=issue.status;d.append(select);
      const e=document.createElement('td');const button=document.createElement('button');button.className='button small';button.textContent='Save';
      button.addEventListener('click',async()=>{button.disabled=true;try{await req('/admin/issues/'+issue.issue_id,{method:'PATCH',body:JSON.stringify({status:select.value})});message(target,'Status updated for '+issue.issue_id);await loadIssues();}catch(err){message(target,err.message,true);}finally{button.disabled=false;}});
      e.append(button);
      if(issue.photo_key){const view=document.createElement('button');view.className='button link';view.textContent='View photo';view.addEventListener('click',async()=>{try{const data=await req('/admin/issues/'+issue.issue_id+'/photo');window.open(data.url,'_blank','noopener,noreferrer');}catch(err){message(target,err.message,true);}});e.append(view);}
      tr.append(a,b,c,d,e);body.append(tr);
    }
  }catch(err){message(target,err.message,true);}
}
