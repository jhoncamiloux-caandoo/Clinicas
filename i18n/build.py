# -*- coding: utf-8 -*-
"""Gera /es/index.html e /en/index.html a partir do index.html (português, fonte única).
Uso: python3 i18n/build.py   (rode sempre que mudar o index.html ou as traduções)
Também atualiza o bloco de SEO (canonical, hreflang, Open Graph) das 3 páginas."""
import re, os, sys
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(__file__))
from translations import T, SEO, WA_TEXT

SITE = 'https://clinicas.clint.digital'   # domínio final: ajuste aqui se for outro
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
WA_PT = 'Oi%21%20Gostaria%20de%20ver%20como%20a%20Clint%20ajuda%20cl%C3%ADnicas%20m%C3%A9dicas%20a%20confirmar%20consultas%2C%20recuperar%20pacientes%20e%20automatizar%20o%20atendimento%20com%20IA.'

def norm(x): return ' '.join(x.split())
KEYS = sorted(T, key=len, reverse=True)
# texto entre > < ou entre aspas; espaço interno flexível; uma passada só (não retraduz)
ALT = '|'.join(r'\s+'.join(re.escape(w) for w in k.split(' ')) if k.strip() else re.escape(k) for k in KEYS)
PAT = re.compile(r'(?<=[>\'"])(\s*)(' + ALT + r')(\s*)(?=[<\'"])')
LOOK = {norm(k) if k.strip() else k: v for k, v in T.items()}
for k in T:  # chaves com espaço nas pontas (ex.: 'Passo ', ' de 5')
    LOOK[k] = T[k]

def seo_block(lang):
    m = SEO[lang]; url = SITE + m['path']
    alts = ''.join('<link rel="alternate" hreflang="%s" href="%s%s" />' % (SEO[l]['lang'], SITE, SEO[l]['path']) for l in SEO)
    alts += '<link rel="alternate" hreflang="x-default" href="%s/" />' % SITE
    og = ('<meta property="og:type" content="website" /><meta property="og:url" content="%s" />'
          '<meta property="og:title" content="%s" /><meta property="og:description" content="%s" />'
          '<meta property="og:locale" content="%s" />' % (url, m['title'], m['desc'], m['locale']))
    og += ''.join('<meta property="og:locale:alternate" content="%s" />' % SEO[l]['locale'] for l in SEO if l != lang)
    return '<!-- i18n:seo --><link rel="canonical" href="%s" />%s%s<!-- /i18n:seo -->' % (url, alts, og)

def set_seo(html, lang):
    m = SEO[lang]
    html = re.sub(r'<html lang="[^"]*"', '<html lang="%s"' % m['lang'], html, 1)
    html = re.sub(r'<title>.*?</title>', '<title>%s</title>' % m['title'], html, 1, flags=re.S)
    html = re.sub(r'<meta name="description" content="[^"]*"', '<meta name="description" content="%s"' % m['desc'], html, 1)
    html = re.sub(r'<!-- i18n:seo -->.*?<!-- /i18n:seo -->', lambda _: seo_block(lang), html, 1, flags=re.S)
    html = html.replace('class="on" aria-current="true"', '')
    html = html.replace('data-lang="%s"' % lang, 'data-lang="%s" class="on" aria-current="true"' % lang)
    return html

def translate(html, lang):
    idx = 0 if lang == 'es' else 1
    def sub(m):
        key = m.group(2); v = LOOK.get(key) or LOOK.get(norm(key))
        return m.group(1) + (v[idx] if v else key) + m.group(3)
    parts = re.split(r'(<style>.*?</style>)', html, flags=re.S)   # nunca mexe no CSS
    html = ''.join(p if p.startswith('<style>') else PAT.sub(sub, p) for p in parts)
    return html.replace(WA_PT, quote(WA_TEXT[lang], safe=''))

out = set_seo(SRC, 'pt')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
for lang in ('es', 'en'):
    html = set_seo(translate(SRC, lang), lang)
    html = html.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- Gerado por i18n/build.py a partir do index.html. Não editar à mão. -->', 1)
    os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
    open(os.path.join(ROOT, lang, 'index.html'), 'w', encoding='utf-8').write(html)
    left = [k for k in T if len(k) > 3 and re.search(r'(?<=[>\'"])\s*' + re.escape(k) + r'\s*(?=[<\'"])', html) and T[k][0 if lang=='es' else 1] != k]
    print(lang, 'ok', '| sobrou sem traduzir:', left[:10])
