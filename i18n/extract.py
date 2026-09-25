"""Lista todos os textos traduzíveis do index.html (texto visível, atributos e strings do JS)."""
import re, json, html
from html.parser import HTMLParser
SRC=open('index.html',encoding='utf-8').read()
ATTRS={'alt','aria-label','title','placeholder','content','data-label'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.stack=[]; s.out=[]; s.js=[]
    def handle_starttag(s,t,a):
        s.stack.append(t)
        for k,v in a:
            if k in ATTRS and v and re.search(r'[A-Za-zÀ-ú]{2}',v) and not v.startswith(('http','width=')): s.out.append(v.strip())
        if t in ('meta','img','input','br','link','source','path','circle','rect','line') : s.stack.pop()
    def handle_endtag(s,t):
        while s.stack and s.stack.pop()!=t: pass
    def handle_data(s,d):
        cur=s.stack[-1] if s.stack else ''
        if cur=='style': return
        if cur=='script':
            s.js.append(d); return
        t=' '.join(d.split())
        if t and re.search(r'[A-Za-zÀ-ú]',t): s.out.append(t)
p=P(); p.feed(SRC)
js=[]
for block in p.js:
    for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'",block):
        v=m.group(1)
        if re.search(r'[à-úÀ-Ú]|\b(Passo|de|do|da|Role|Um|Oi|Pode|Quinta|Obrigada|Prontinho|Super|Ah|Mas|Este|Consultas|Pacientes|Faltas|Voltaram|compareceram|agora|Indicadores|pacientes|Enviar|Retorno|Confirmou|Instagram|Site|meses|ano|online|digitando|Hoje|menos|mais|Todos|Escreva)\b',v) and ' ' in v or re.search(r'[à-úÀ-Ú]',v):
            if not re.match(r'^[\s\-\w]*\.(png|svg|webp|mp4)$',v): js.append(v)
seen=[];[seen.append(x) for x in p.out+js if x not in seen]
json.dump(seen,open('i18n/_strings.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(seen))
