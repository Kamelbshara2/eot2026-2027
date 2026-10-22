import updates from './content-updates.json' with {type:'json'};
const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
// Upgrade only exact original exercises; preserve custom edits and deletions.
export function upgradeQuestion(q){if(!q)return q;let current=q;for(let i=0;i<updates.length;i++){const update=updates.find(u=>u.before.id===current.id&&canonical(u.before)===canonical(current));if(!update)break;current=structuredClone(update.after)}return current}
