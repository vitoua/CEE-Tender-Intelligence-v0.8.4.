from datetime import datetime,timedelta
import httpx,re
from app.core import Tender
URL='https://ezamowienia.gov.pl/mo-board/api/v1/notice'
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
def clean(v):return re.sub('<[^>]+>',' ',str(v or ''))
async def fetch(countries=None,limit=100):
 now=datetime.utcnow();params={'NoticeType':'ContractNotice','PublicationDateFrom':(now-timedelta(days=90)).strftime('%Y-%m-%dT00:00:00'),'PublicationDateTo':now.strftime('%Y-%m-%dT23:59:59'),'OrderType':'Delivery','PageSize':min(limit,500)};out=[];search_after=None
 async with httpx.AsyncClient(timeout=45,follow_redirects=True) as c:
  while len(out)<limit:
   q=dict(params)
   if search_after:q['SearchAfter']=search_after
   r=await c.get(URL,params=q)
   if r.status_code!=200:raise RuntimeError(f'BZP HTTP {r.status_code}: {r.text[:1000]}')
   rows=r.json() or []
   if not rows:break
   for x in rows:
    ddl=dt(x.get('submittingOffersDate'))
    if ddl and ddl<now:continue
    no=str(x.get('noticeNumber') or x.get('bzpNumber') or x.get('objectId'));url='https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/'+str(x.get('objectId') or no)
    out.append(Tender('pl:'+no,'poland','POL',x.get('orderObject') or no,x.get('organizationName') or '',deadline=ddl,url=url,description=clean(x.get('htmlBody')),procurement_id=no))
    if len(out)>=limit:break
   search_after=rows[-1].get('objectId')
   if not search_after or len(rows)<params['PageSize']:break
 return out
