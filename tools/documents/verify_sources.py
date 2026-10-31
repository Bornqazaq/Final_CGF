"""Resolve bibliographic identities from the primary DOI registration metadata."""
import urllib.request,json,concurrent.futures,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOIS=['10.1145/360825.360839', '10.1145/357290.357293', '10.1111/1467-8659.1330233', '10.1145/1409625.1409627', '10.1111/j.1467-8659.2009.01602.x', '10.1145/2366145.2366218', '10.1109/2945.675649', '10.1016/S0097-8493(00)00130-8', '10.1109/TVCG.2003.1207447', '10.1145/566654.566575', '10.1109/2945.646233', '10.1111/j.1467-8659.2003.00722.x', '10.1111/j.1467-8659.2005.00829.x', '10.1145/360349.360353', '10.1145/1073204.1073261', '10.1145/1183287.1183294', '10.1145/882262.882308', '10.1145/1073204.1073206']

def fetch(doi):
 try:
  u='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'LaserVaultHeist academic bibliography verification'}),timeout=35) as f:m=json.load(f)['message']
  return {'doi':doi,'title':m.get('title',[''])[0],'journal':m.get('container-title',[''])[0],'type':m['type'],'authors':[a.get('given','')+' '+a.get('family','') for a in m.get('author',[])],'year':m.get('published',{}).get('date-parts',[[None]])[0][0],'volume':m.get('volume'),'issue':m.get('issue'),'pages':m.get('page'),'abstract':re.sub('<[^>]+>',' ',m.get('abstract','')),'url':m.get('URL'),'publisher':m.get('publisher')}
 except Exception as e:return {'doi':doi,'error':str(e)}
if __name__=='__main__':
 records=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,DOIS))
 (ROOT/'evidence/research-metadata-raw.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
 for a in records:print(a['doi'],a.get('type'),a.get('year'),a.get('title',a.get('error')),a.get('journal'))
