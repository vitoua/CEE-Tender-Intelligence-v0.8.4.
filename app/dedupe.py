import hashlib,re,unicodedata
def n(v):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(v or '')).encode('ascii','ignore').decode().lower()).strip()
def fingerprint(x):return hashlib.sha256('|'.join([x.country,n(x.buyer),n(x.title)[:180],x.deadline.date().isoformat() if x.deadline else '',str(round(x.value or 0,2)),x.currency]).encode()).hexdigest()
