from pathlib import Path
from pypdf import PdfReader
from docx import Document
root = Path(__file__).resolve().parents[1]
out = root / 'docs' / 'source-extracts'
out.mkdir(exist_ok=True)
for path in (root/'brief'/'source-materials').glob('*.pdf'):
    reader = PdfReader(path)
    text = '\n\n'.join(f'PAGE {i+1}\n{p.extract_text()}' for i,p in enumerate(reader.pages))
    (out/(path.stem+'.txt')).write_text(text,encoding='utf-8')
    print(path.name, len(reader.pages), 'pages')
    if 'requirements' in path.name.lower(): print(text)
    else:
        start=text.find('12.')
        print(text[max(0,start):start+2800])
doc=Document(root/'brief'/'source-materials'/'Report template.docx')
text='\n'.join(p.text for p in doc.paragraphs)
(out/'Report template.txt').write_text(text,encoding='utf-8')
print('REPORT TEMPLATE\n'+text)
