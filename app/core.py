from dataclasses import dataclass,field
from datetime import datetime
@dataclass
class Tender:
 id:str;source:str;country:str;title:str;buyer:str='';value:float|None=None;currency:str='';deadline:datetime|None=None;status:str='active';url:str='';description:str='';procurement_id:str='';source_links:dict=field(default_factory=dict)
class Store:
 def __init__(self):self.data={};self.runs=[];self.idx={}
 def key(self,x):return (x.country,(x.procurement_id or '').lower())
 def add(self,src,rows):
  from app.dedupe import fingerprint
  a=d=0
  for x in rows:
   x.source_links=x.source_links or ({x.source:x.url} if x.url else {});keys=[self.key(x),('fp',fingerprint(x))];hit=next((self.idx[k] for k in keys if k in self.idx),None)
   if hit is None:
    self.data[x.id]=x;a+=1
    for k in keys:self.idx[k]=x.id
   else:
    y=self.data[hit];p=x if x.source!='ted' and y.source=='ted' else y;p.source_links={**y.source_links,**x.source_links};self.data[hit]=p;d+=1
  self.runs.insert(0,{'source':src,'status':'ok','count':len(rows),'added':a,'duplicates':d,'error':''})
 def error(self,s,e):self.runs.insert(0,{'source':s,'status':'error','count':0,'added':0,'duplicates':0,'error':str(e)})
store=Store()
def active(x):return x.status.lower() not in {'complete','completed','awarded','cancelled','closed'} and (not x.deadline or x.deadline>=datetime.utcnow())
