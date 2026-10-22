import {requestApi} from './api-client.js';
export const adminState={active:false,token:''};
export function requireAdmin(){if(!adminState.active)throw Error('Admin sign-in required')}
export function mountAdmin({onChange}){
 const button=document.querySelector('#cloud-login');button.textContent='Admin sign-in · دخول المسؤول';
 const dialog=document.createElement('dialog');dialog.id='admin-dialog';dialog.innerHTML=`<form id="admin-form"><div class="section-head"><h2>Admin sign-in · دخول المسؤول</h2><button type="button" class="close" aria-label="Close admin sign-in">×</button></div><label>Username · اسم المستخدم<input name="username" autocomplete="username" required></label><label>Password · كلمة المرور<input name="password" type="password" autocomplete="current-password" required></label><p role="alert" id="admin-error"></p><button type="submit" class="primary">Sign in · دخول</button></form>`;document.body.append(dialog);
 const form=dialog.querySelector('form'),error=dialog.querySelector('#admin-error');
 const notify=()=>{document.body.classList.toggle('admin-mode',adminState.active);button.textContent=adminState.active?'Admin sign out · خروج المسؤول':'Admin sign-in · دخول المسؤول';onChange();window.dispatchEvent(new Event('admin-role-changed'))};
 const reset=()=>{adminState.active=false;adminState.token='';sessionStorage.removeItem('forma-admin-session');sessionStorage.removeItem('forma-admin-token');notify();document.querySelector('#editor')?.close();document.querySelector('#viewer')?.close()};
 dialog.querySelector('.close').onclick=()=>{form.reset();dialog.close()};
 button.onclick=async()=>{if(adminState.active){try{await requestApi('/api/admin',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${adminState.token}`},body:JSON.stringify({action:'logout'})});reset()}catch{error.textContent='Cannot confirm logout. Please retry.';dialog.showModal()}return}error.textContent='';form.reset();dialog.showModal()};
 form.onsubmit=async e=>{e.preventDefault();const submit=form.querySelector('[type=submit]');if(submit.disabled)return;submit.disabled=true;error.textContent='';try{const r=await requestApi('/api/admin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:form.elements.username.value,password:form.elements.password.value})});const data=await r.json();if(!r.ok||!data.admin||!data.token)throw Error(data.error||'Sign-in failed');adminState.active=true;adminState.token=data.token;sessionStorage.setItem('forma-admin-session',data.token);form.reset();dialog.close();notify()}catch(e){error.textContent=e.message+' · تعذر تسجيل الدخول';form.elements.password.value=''}finally{submit.disabled=false}};
 window.addEventListener('admin-session-expired',reset);
 try{const token=sessionStorage.getItem('forma-admin-session');if(token)requestApi('/api/admin',{headers:{Authorization:`Bearer ${token}`}}).then(async r=>{if(!r.ok){reset();return}const data=await r.json();if(data.admin){adminState.active=true;adminState.token=token;notify()}}).catch(()=>reset())}catch{}
 notify();
}
