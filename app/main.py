from fastapi import FastAPI,Form,Request,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core import store,active
from app.config import s
from app.i18n import tr
from app.sources import COUNTRIES,sources_for
app=FastAPI(version='0.8.4');app.mount('/static',StaticFiles(directory='app/static'),name='static');tp=Jinja2Templates(directory='app/templates')
def lg(r):return r.cookies.get('lang') or s.app_language
def ctx(r,x=None):return {'request':r,'t':tr(lg(r)),'lang':lg(r),**(x or {})}
@app.get('/health')
def health():return {'status':'ok','version':'0.8.4'}
@app.get('/lang/{code}')
def language(code,request:Request):
 r=RedirectResponse(request.headers.get('referer') or '/',303);r.set_cookie('lang',code if code in ('uk','pl','en','es') else 'uk');return r
@app.get('/')
def home(request:Request,q:str='',country:str='',active_only:int=1):
 rows=[x for x in store.data.values() if (not active_only or active(x)) and (not country or x.country==country) and (not q or q.lower() in (x.title+x.buyer+x.description).lower())];rows.sort(key=lambda x:x.deadline or __import__('datetime').datetime.max);return tp.TemplateResponse('index.html',ctx(request,{'rows':rows,'runs':store.runs,'available':COUNTRIES,'countries':sorted({x.country for x in store.data.values()}),'q':q,'country':country,'active_only':active_only}))
@app.post('/refresh')
async def refresh(request:Request,countries:list[str]=Form(default=[])):
 import asyncio
 async def one(src,scope):
  try:
   if src=='ted':from app.connectors.ted import fetch
   elif src=='prozorro':from app.connectors.prozorro import fetch
   elif src=='germany':from app.connectors.germany import fetch
   else:from app.connectors.poland import fetch
   return src,await asyncio.wait_for(fetch(scope),75),None
  except Exception as e:return src,[],e
 res=await asyncio.gather(*(one(a,b) for a,b in sources_for(countries or list(COUNTRIES))))
 for a,b,e in res:store.error(a,e) if e else store.add(a,b)
 return RedirectResponse('/',303)
@app.get('/tenders/{tid:path}')
def detail(tid,request:Request):
 x=store.data.get(tid)
 if not x:raise HTTPException(404)
 return tp.TemplateResponse('detail.html',ctx(request,{'x':x}))
