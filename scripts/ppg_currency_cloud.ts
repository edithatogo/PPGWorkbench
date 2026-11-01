// Read-only Office Script. SharePoint writes are serial, conditional flow actions.
interface Policy { Id:number; DocumentUID:string; sourceDocumentId:string; sourceTitle:string; sourceCustodian:string }
interface Link {FromDocumentUID:string;ToDocumentUID:string;RelationshipType:string;ReviewState:string}
interface Lead {Id:number;Title:string;CurrencyMatch:string;CurrencyOwner:string;CurrencyEvidence:string;CurrencyDisposition:string;CurrencyPolicy:{Url:string};"odata.etag":string}
interface Input {leads:Lead[]; policies:Policy[]; relationships:Link[]; form:string; canvas:string; template:string}
function main(workbook: ExcelScript.Workbook, requestJson:string):string {
 const x=JSON.parse(requestJson) as Input;
 const norm=(s:string)=>" "+(s||"").toLowerCase().replace(/[^a-z0-9]+/g," ").trim()+" ";
 const stop="a an of at by from to the for and in on or with use using care policy procedure guideline management services service hospital health patient patients clinical medical safety update alerts report national program review treatment general adult adults children child during before after system information practice public quality new products product device devices local staff".split(" ");
 const phrases=(s:string):string[]=>{const w=norm(s).trim().split(" "),out:string[]=[];for(const n of [2,3])for(let i=0;i+n<=w.length;i++){const part=w.slice(i,i+n);if(part.filter(v=>v.length>=3&&/[a-z]/.test(v)&&stop.indexOf(v)<0).length>=2)out.push(part.join(" "))}return out};
 const idx=new Map<string,Policy[]>();for(const p of x.policies){for(const key of phrases(p.sourceTitle)){const group=idx.get(key)||[];if(group.indexOf(p)<0)group.push(p);idx.set(key,group)}}
 const writes:{id:number;etag:string;patch:{CurrencyMatch:string;CurrencyEvidence:string;CurrencyOwner:string|null;CurrencyPolicy:{Url:string;Description:string}|null}}[]=[];
 const describe=(p:Policy)=>[p.DocumentUID,p.sourceTitle,p.sourceCustodian||"Custodian unresolved",x.form+"?ID="+p.Id].join(" — ");
 for(const l of x.leads){if(l.CurrencyDisposition||l.CurrencyMatch||l.CurrencyPolicy||l.CurrencyEvidence||l.CurrencyOwner)continue;
 const t=norm(l.Title);let basis="Identifier in lead title";let hits=x.policies.filter(p=>[p.DocumentUID,p.sourceDocumentId].some(v=>!!v&&v.length>=6&&t.includes(norm(v))));
 if(!hits.length){basis="Exact catalogue title";hits=x.policies.filter(p=>!!p.sourceTitle&&norm(p.sourceTitle)===t)}
 if(!hits.length){const matches=new Map<Policy,string>();for(const key of phrases(l.Title)){const group=idx.get(key);if(group&&group.length===1)matches.set(group[0],key)}hits=Array.from(matches.keys());basis="Shared catalogue phrase: "+Array.from(new Set(Array.from(matches.values()))).join("; ")}
 const p=hits.length===1?hits[0]:null;const notes=hits.map(v=>describe(v));for(const rel of x.relationships){if(!hits.some(v=>v.DocumentUID===rel.ToDocumentUID)||["Accepted","Proposed"].indexOf(rel.ReviewState)<0)continue;const from=x.policies.find(v=>v.DocumentUID===rel.FromDocumentUID);if(from)notes.push(rel.ReviewState+" "+rel.RelationshipType+" (review only): "+describe(from))}
 if(!/^"\d+"$/.test(l["odata.etag"]))throw Error("Missing lead version");
 writes.push({id:l.Id,etag:l["odata.etag"],patch:{CurrencyMatch:!hits.length?"Unresolved":p?"Candidate — review":"Multiple candidates",CurrencyEvidence:hits.length?basis+" | "+notes.join("\n"):"No identifier, exact title or distinctive shared title phrase",CurrencyOwner:p?p.sourceCustodian||null:null,CurrencyPolicy:p?{Url:x.form+"?ID="+p.Id,Description:"Open candidate policy"}:null}})}
 const done=x.leads.filter(v=>(v.CurrencyDisposition||"").trim().length>0).length,total=x.leads.length;
 const skeleton=(s:string)=>s.replace(/\d+ of \d+ leads have a recorded disposition(?: \(\d+(?:\.\d+)?%\))?\./,"{coverage}").replace(/\d+ await triage\./,"{pending}");
 if(skeleton(x.canvas)!==skeleton(x.template)||!skeleton(x.canvas).includes("{coverage}")||!skeleton(x.canvas).includes("{pending}"))throw Error("Report page changed; reconcile owner edits");
 const summary=done+" of "+total+" leads have a recorded disposition"+(total?" ("+(100*done/total).toFixed(1)+"%).":".");
 const canvas=skeleton(x.canvas).replace("{coverage}",summary).replace("{pending}",(total-done)+" await triage.");
 return JSON.stringify({writes,summary,total,done,canvas,changed:canvas!==x.canvas})
}
