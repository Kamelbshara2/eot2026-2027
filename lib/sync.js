import {upgradeQuestion} from './content-upgrades.js';
const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
// One durable envelope: cached server rows + pending writes + local question bank.
export class QuestionSync {
  key='forma-sync-v2';
  constructor({storage,request,onChange=()=>{},onStatus=()=>{},token=()=>'',canWrite=()=>Boolean(token())}){Object.assign(this,{storage,request,onChange,onStatus,token,canWrite});this.busy=false;this.state={questions:[],rows:{},pending:{}}}
  get questions(){return this.state.questions}
  persist(next){this.storage.setItem(this.key,JSON.stringify(next));this.state=next}
  init(seeds,legacyKey){const saved=this.storage.getItem(this.key);if(saved){const next=JSON.parse(saved);const known=new Set([...next.questions.map(q=>q.id),...Object.keys(next.rows),...Object.keys(next.pending)]);for(const q of seeds){if(known.has(q.id))continue;next.questions.push(q);next.pending[q.id]={data:q,revision:0}}this.persist(next);this.upgradeCached();return}const old=JSON.parse(this.storage.getItem(legacyKey)||'[]');const questions=[...new Map([...seeds,...old].map(q=>[q.id,q])).values()];this.persist({questions,rows:{},pending:Object.fromEntries(questions.map(q=>[q.id,{data:q,revision:0}]))});this.upgradeCached()}
  upgradeCached(){const next=structuredClone(this.state);next.questions=next.questions.map(q=>{const updated=upgradeQuestion(q);if(canonical(updated)!==canonical(q))next.pending[q.id]={data:updated,revision:next.pending[q.id]?.revision??next.rows[q.id]?.revision??0};return updated});this.persist(next)}
  save(questions){if(!this.canWrite())throw Error('Admin sign-in required');const pending={...this.state.pending};const before=new Map(this.questions.map(q=>[q.id,q])),after=new Map(questions.map(q=>[q.id,q]));for(const id of new Set([...before.keys(),...after.keys()])){if(canonical(before.get(id))===canonical(after.get(id)))continue;pending[id]={data:after.get(id)||null,revision:pending[id]?.revision??this.state.rows[id]?.revision??0}}
    this.persist({...this.state,questions,pending});void this.run()}
  apply(rows){const next=structuredClone(this.state);for(const row of rows){next.rows[row.id]=row;if(next.pending[row.id])continue;next.questions=next.questions.filter(q=>q.id!==row.id);if(!row.deleted)next.questions.push(row.data)}this.persist(next);this.upgradeCached();this.onChange(this.questions)}
  async run(){if(this.busy)return;this.busy=true;try{
    this.onStatus('Connecting to cloud…');const response=await this.request('/api/questions',{cache:'no-store'});if(!response.ok)throw Error(response.status===503?'Cloud database not configured · saved locally':'Offline · saved locally');const {rows}=await response.json();
    // First connection: existing server rows win over unchanged bundled/local migration data.
    // Identical pending creates are already acknowledged. Divergent creates become explicit conflicts.
    for(const row of rows){const pending=this.state.pending[row.id];if(pending&&!row.deleted&&pending.revision===0&&canonical(pending.data)===canonical(upgradeQuestion(row.data))&&canonical(row.data)!==canonical(pending.data)){const next=structuredClone(this.state);next.pending[row.id].revision=row.revision;this.persist(next)}if(pending&&canonical(pending.data)===canonical(row.deleted?null:row.data)){const next=structuredClone(this.state);delete next.pending[row.id];this.persist(next)}}
    this.apply(rows);if(!this.canWrite()){const current=structuredClone(this.state);current.questions=rows.filter(r=>!r.deleted).map(r=>r.data);current.pending={};this.persist(current);this.onChange(this.questions);this.onStatus('Practice mode · وضع التدريب');return}let conflict=false;
    for(const [id,change] of Object.entries({...this.state.pending})){
      if((this.state.rows[id]?.revision??0)!==change.revision){conflict=true;continue}
      if(!this.canWrite()||!this.token()){this.onStatus('Saved locally · enable cloud editing to upload');return}
      const result=await this.request('/api/questions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${this.token()}`},body:JSON.stringify({id,...change})});
      if(result.status===401){globalThis.dispatchEvent?.(new Event('admin-session-expired'));throw Error('Admin session expired')}if(result.status===409){conflict=true;continue}if(!result.ok)throw Error(result.status===401?'Editing key rejected · saved locally':'Cloud save failed · saved locally');
      const {row}=await result.json();const next=structuredClone(this.state);
      // A user may have edited again while the network write was in flight.
      if(canonical(next.pending[id])===canonical(change))delete next.pending[id];else if(next.pending[id])next.pending[id].revision=row.revision;
      this.persist(next);this.apply([row]);
    }
    this.onStatus(conflict?'Sync conflict · export local backup; export a backup or choose Use cloud version':'Cloud synced'+(Object.keys(this.state.pending).length?' · changes pending':''));
  }catch(error){this.onStatus(error.message||'Offline · saved locally')}finally{this.busy=false}}
}
