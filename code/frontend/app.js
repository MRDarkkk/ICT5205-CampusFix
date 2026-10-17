'use strict';
const api = (window.CAMPUSFIX_CONFIG.apiBase || '').replace(/\/$/, '');
const form = document.querySelector('#issueForm');
const track = document.querySelector('#trackForm');
const msg = document.querySelector('#reportMessage');
const result = document.querySelector('#trackingResult');
const submitBtn = document.querySelector('#submitBtn');
function show(target, text, isError=false) { target.hidden = false; target.textContent = text; target.className = 'message ' + (isError ? 'error' : 'success'); }
async function apiJson(path, opts={}) {
  const resp = await fetch(api + path, {headers: {'Content-Type':'application/json'}, ...opts});
  const data = await resp.json().catch(()=>({error:'Unexpected server response'}));
  if (!resp.ok) throw new Error(data.error || `Request failed (${resp.status})`);
  return data;
}
async function uploadPhoto(file) {
  if (file.size > 5 * 1024 * 1024 || file.size < 1) throw Error('Photo must be between 1 byte and 5 MB');
  if (!['image/jpeg','image/png','image/webp'].includes(file.type)) throw Error('Use JPEG, PNG or WebP images');
  const presign = await apiJson('/uploads/presign', {method:'POST',body:JSON.stringify({content_type:file.type})});
  const uploadForm = new FormData();
  for (const [key,value] of Object.entries(presign.fields)) uploadForm.append(key,value);
  uploadForm.append('file',file);
  const response = await fetch(presign.upload_url,{method:'POST',body:uploadForm});
  if (!response.ok && response.status !== 204) throw Error('Photo upload to S3 failed');
  return presign.photo_key;
}
form.addEventListener('submit',async event=>{
  event.preventDefault(); submitBtn.disabled = true; submitBtn.textContent = 'Submitting…'; msg.hidden=true;
  try {
    const body = {title:document.querySelector('#title').value,description:document.querySelector('#description').value,
      location:document.querySelector('#location').value,category:document.querySelector('#category').value,
      priority:document.querySelector('#priority').value};
    const file = document.querySelector('#photo').files[0];
    if (file) body.photo_key = await uploadPhoto(file);
    const created = await apiJson('/issues',{method:'POST',body:JSON.stringify(body)});
    show(msg, `Report submitted! Save tracking ID: ${created.issue_id}. Current status: Open.`);
    document.querySelector('#trackingId').value=created.issue_id;
    form.reset();
  } catch (err) {show(msg, err.message, true);} finally {submitBtn.disabled=false;submitBtn.textContent='Submit maintenance report';}
});
track.addEventListener('submit',async event=>{
  event.preventDefault(); result.hidden=true;
  try {
    const id=document.querySelector('#trackingId').value.trim();
    const record=await apiJson('/issues/'+encodeURIComponent(id));
    const status=record.status.replaceAll('_',' ');
    result.hidden=false;result.className='result';result.replaceChildren();
    const heading=document.createElement('h3');heading.textContent=record.title;
    const summary=document.createElement('p');summary.textContent=`${record.location} · ${record.category} · ${status.toUpperCase()}`;
    const date=document.createElement('p');date.className='hint';date.textContent=`Submitted: ${new Date(record.created_at).toLocaleString()}`;
    result.append(heading,summary,date);
  } catch(err){result.hidden=false;result.className='message error';result.textContent=err.message;}
});
