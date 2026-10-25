#!/usr/bin/env python3
"""Gerador estático do site Nêspera Studio.

Uso:
  python3 build.py            -> gera dist/ com os dados reais (data/catalog.json)
  EXEMPLO=1 python3 build.py  -> gera dist/ usando data/catalog.example.json (só para teste local)

Sem dependências externas: só a biblioteca padrão do Python 3.
"""
import json, os, shutil, html, datetime, urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
SRC, DATA, DIST = ROOT / "src", ROOT / "data", ROOT / "dist"
HOJE = datetime.date.today().isoformat()

site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
cat_file = "catalog.example.json" if os.environ.get("EXEMPLO") == "1" else "catalog.json"
catalogo = json.loads((DATA / cat_file).read_text(encoding="utf-8"))
conteudos = json.loads((DATA / "conteudos.json").read_text(encoding="utf-8"))["itens"]

BASE = site["url"].rstrip("/")
IG = f"https://www.instagram.com/{site['instagram']}/"
IG_DM = f"https://ig.me/m/{site['instagram']}"
IG_ART = f"https://www.instagram.com/{site['instagram_artista']}/"
e = lambda s: html.escape(str(s), quote=True)
itens = [i for i in catalogo.get("itens", []) if i.get("slug")]
categorias = {c["slug"]: c["nome"] for c in catalogo.get("categorias", [])}
paginas_sitemap = []
if DIST.exists():
    shutil.rmtree(DIST)

BIRD = ('<svg class="bird" viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
        '<path d="M6 27c3-8 11-12 18-11 2-4 6-5 9-3l4 1-4 2c0 6-4 10-10 12l5 6h-3l-5-5c-5 1-10 0-14-2z"/>'
        '<path d="M19 33v5M23 32v6" stroke="currentColor" stroke-width="1.4" fill="none"/></svg>')
LOGO = f'<span class="wordmark">N&ecirc;spera{BIRD}<small>studio</small></span>'
NAV = [("/", "Início"), ("/vitrine/", "Vitrine"), ("/sobre/", "Sobre"),
       ("/conteudos/", "Conteúdos"), ("/contato/", "Contato")]


def preco_fmt(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def whatsapp_link(msg):
    num = "".join(ch for ch in site.get("whatsapp", "") if ch.isdigit())
    return f"https://wa.me/{num}?text={urllib.parse.quote(msg)}" if num else ""


def org_ld():
    same = [IG, IG_ART]
    d = {"@context": "https://schema.org", "@type": "Organization", "@id": BASE + "/#org",
         "name": site["nome"], "url": BASE + "/", "logo": BASE + "/assets/img/og.png",
         "description": site["descricao_curta"], "sameAs": same}
    if site.get("fundacao"):
        d["foundingDate"] = site["fundacao"]
    if site.get("email"):
        d["email"] = site["email"]
    return d


def page(path, title, desc, body, active="", ld=None, noindex=False, og_img="/assets/img/og.png",
         og_type="website"):
    full_title = title if title.startswith(site["nome"]) else f"{title} | {site['nome']}"
    canon = BASE + path
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
                  for x in (ld or []))
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>'
                  for h, t in NAV)
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    if not noindex and path != "/404.html":
        paginas_sitemap.append(path)
    ga = f' data-ga4="{e(site["ga4_id"])}"' if site.get("ga4_id") else ""
    year = datetime.date.today().year
    contato_extra = ""
    if site.get("email"):
        contato_extra += f'<a href="mailto:{e(site["email"])}">{e(site["email"])}</a>'
    if site.get("whatsapp"):
        contato_extra += f'<a href="{e(whatsapp_link("Olá! Vim pelo site do Nêspera Studio."))}" rel="noopener" target="_blank">WhatsApp</a>'
    return f"""<!doctype html>
<html lang="{site['idioma']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(site['nome'])}">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/InstrumentSerif-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/CourierPrime-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
{lds}
<script src="/assets/main.js" defer></script>
</head>
<body{ga}>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="site-header">
  <a class="brand" href="/" aria-label="{e(site['nome'])}, página inicial">{LOGO}</a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <nav id="nav" class="nav" aria-label="Principal">{nav}</nav>
</header>
<main id="conteudo">
{body}
</main>
<footer class="site-footer">
  <div class="foot-brand">{LOGO}<p>Artes visuais, desde dois mil e vinte seis.</p></div>
  <nav class="foot-col" aria-label="Rodapé">{''.join(f'<a href="{h}">{t}</a>' for h, t in NAV)}<a href="/privacidade/">Privacidade</a></nav>
  <div class="foot-col">
    <a href="{IG}" rel="noopener" target="_blank">Instagram @{e(site['instagram'])}</a>
    <a href="{IG_ART}" rel="noopener" target="_blank">Artista @{e(site['instagram_artista'])}</a>
    {contato_extra}
  </div>
  <p class="legal">&copy; {year} {e(site['nome'])}. Imagens e obras protegidas por direitos autorais.</p>
</footer>
<div class="consent" hidden role="dialog" aria-label="Preferências de cookies">
  <p>Usamos cookies de medição de audiência (Google Analytics) só com a sua permissão. <a href="/privacidade/">Saiba mais</a>.</p>
  <div><button type="button" data-consent="no" class="btn ghost">Recusar</button><button type="button" data-consent="yes" class="btn">Aceitar</button></div>
</div>
</body>
</html>
"""


def write(path, content):
    out = DIST / path.lstrip("/")
    if path.endswith("/"):
        out = out / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def form_lancamento(origem):
    return f"""
<form class="form form-inline" name="lista-lancamento" method="POST" action="/obrigado/" data-netlify="true" netlify-honeypot="empresa" novalidate>
  <input type="hidden" name="form-name" value="lista-lancamento">
  <input type="hidden" name="origem" value="{e(origem)}">
  <p class="hp"><label>Não preencha <input name="empresa" tabindex="-1" autocomplete="off"></label></p>
  <div class="field">
    <label for="lanc-email-{e(origem)}">Seu e-mail</label>
    <input id="lanc-email-{e(origem)}" type="email" name="email" autocomplete="email" required placeholder="voce@exemplo.com">
    <p class="err" aria-live="polite"></p>
  </div>
  <label class="check"><input type="checkbox" name="consentimento" value="sim" required><span>Aceito receber o aviso de lançamento e li a <a href="/privacidade/">política de privacidade</a>.</span></label>
  <p class="err err-check" aria-live="polite"></p>
  <button class="btn" type="submit">Avisar no lançamento</button>
</form>"""


def card(i):
    img = i["imagens"][0] if i.get("imagens") else None
    pic = (f'<img src="{e(img["src"])}" alt="{e(img["alt"])}" loading="lazy" width="600" height="750">'
           if img else '<div class="ph" aria-hidden="true"></div>')
    preco = f'<p class="price">{preco_fmt(i["preco"])}</p>' if i.get("preco") else ""
    cat = categorias.get(i.get("categoria"), "")
    return f"""<article class="item" data-cat="{e(i.get('categoria',''))}" data-busca="{e((i['nome']+' '+i.get('resumo','')+' '+cat).lower())}">
  <a href="/vitrine/{e(i['slug'])}/">
    <div class="item-img">{pic}</div>
    <p class="item-cat">{e(cat)}</p>
    <h3>{e(i['nome'])}</h3>
    <p>{e(i.get('resumo',''))}</p>
    {preco}
    <span class="link">Ver detalhes</span>
  </a>
</article>"""


def vitrine_vazia(origem):
    return f"""<div class="empty">
  <p class="type-line">em breve<br>produtos<br>na vitrine</p>
  <div>
    <p>As primeiras peças do Nêspera Studio ainda estão no ateliê. Deixe seu e-mail e avisamos quando a vitrine abrir.</p>
    {form_lancamento(origem)}
  </div>
</div>"""


# ---------- Início ----------
destaques = [i for i in itens if i.get("destaque")][:6] or itens[:6]
bloco_vitrine = (f'<div class="grid">{"".join(card(i) for i in destaques)}</div>'
                 f'<p class="more"><a class="btn" href="/vitrine/">Explorar a vitrine</a></p>'
                 if destaques else vitrine_vazia("inicio"))


def conteudo_card(c, n):
    if c["tipo"] == "imagem":
        visual = f'<img src="{e(c["imagem"])}" alt="{e(c["alt"])}" loading="lazy" width="245" height="325">'
    elif c["tipo"] == "texto":
        visual = f'<p class="post-type">{e(c["texto"])}</p>'
    else:
        visual = f'<div class="post-mark">{LOGO}</div>'
    return f"""<article class="post">
  <a href="{e(c['link'])}" rel="noopener" target="_blank">
    <div class="post-visual">{visual}</div>
    <h3>{e(c['titulo'])}</h3>
    <p>{e(c['contexto'])}</p>
    <span class="link">Ver no Instagram</span>
  </a>
</article>"""


posts_html = "".join(conteudo_card(c, n) for n, c in enumerate(conteudos))
home = f"""
<section class="hero">
  <h1 class="hero-title"><span class="sr-only">Nêspera Studio, artes visuais</span><span aria-hidden="true">N&ecirc;spera{BIRD}</span></h1>
  <div class="hero-side">
    <p class="type-line typing" data-text="artes visuais, desde dois mil e vinte seis">artes visuais, desde dois mil e vinte seis</p>
    <p class="lede">Estúdio de artes visuais. Ilustração, cor e pequenos encontros entre mãos, flores e pássaros.</p>
    <div class="actions"><a class="btn" href="/vitrine/">Explorar a vitrine</a><a class="btn ghost" href="/contato/">Entrar em contato</a></div>
  </div>
  <span class="ink ink-a" aria-hidden="true"></span><span class="ink ink-b" aria-hidden="true"></span><span class="ink ink-c" aria-hidden="true"></span>
</section>
<section class="band" aria-labelledby="h-vitrine">
  <h2 id="h-vitrine">A vitrine</h2>
  {bloco_vitrine}
</section>
<section class="band" aria-labelledby="h-ateli">
  <h2 id="h-ateli">Do ateliê</h2>
  <div class="posts">{posts_html}</div>
  <p class="more"><a class="btn ghost" href="/conteudos/">Todos os conteúdos</a></p>
</section>
<section class="band split" aria-labelledby="h-sobre">
  <h2 id="h-sobre">Sobre o estúdio</h2>
  <div class="prose">{''.join(f'<p>{e(p)}</p>' for p in site['sobre'])}<p><a class="link" href="/sobre/">Conhecer o estúdio</a></p></div>
</section>
<section class="band cta">
  <p class="cta-title">Quer conversar sobre uma obra ou encomenda?</p>
  <div class="actions"><a class="btn" href="/contato/">Falar com o estúdio</a><a class="btn ghost" href="{IG}" rel="noopener" target="_blank">Seguir no Instagram</a></div>
</section>"""
website_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": site["nome"],
              "url": BASE + "/", "inLanguage": "pt-BR", "publisher": {"@id": BASE + "/#org"}}
write("/", page("/", f"{site['nome']} | Artes visuais", site["descricao_curta"], home, "/",
                [org_ld(), website_ld]))

# ---------- Vitrine ----------
if itens:
    usados = [c for c in catalogo.get("categorias", []) if any(i.get("categoria") == c["slug"] for i in itens)]
    filtros = ""
    if len(itens) >= 6 and len(usados) > 1:
        filtros = ('<div class="filters" role="group" aria-label="Filtrar por categoria">'
                   '<button type="button" class="chip" aria-pressed="true" data-filter="">Tudo</button>'
                   + "".join(f'<button type="button" class="chip" aria-pressed="false" data-filter="{e(c["slug"])}">{e(c["nome"])}</button>' for c in usados)
                   + '</div>')
    busca = ('<label class="search"><span>Buscar na vitrine</span><input type="search" id="busca" placeholder="Nome, técnica, categoria"></label>'
             if len(itens) >= 9 else "")
    corpo_vitrine = (f'{filtros}{busca}<div class="grid" id="lista">{"".join(card(i) for i in itens)}</div>'
                     '<p class="none" id="nada" hidden>Nenhuma peça encontrada. Tente outro termo ou limpe o filtro.</p>')
else:
    corpo_vitrine = vitrine_vazia("vitrine")
vit = f"""<section class="page-head"><h1>Vitrine</h1><p class="lede">Obras e produtos do Nêspera Studio.</p></section>
<section class="band">{corpo_vitrine}</section>"""
ld_list = []
if itens:
    ld_list.append({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": n + 1, "url": f"{BASE}/vitrine/{i['slug']}/", "name": i["nome"]}
        for n, i in enumerate(itens)]})
write("/vitrine/", page("/vitrine/", "Vitrine", "Conheça as obras e produtos do Nêspera Studio, estúdio de artes visuais.",
                        vit, "/vitrine/", ld_list))

# ---------- Páginas de cada item ----------
for i in itens:
    path = f"/vitrine/{i['slug']}/"
    imgs = "".join(f'<img src="{e(m["src"])}" alt="{e(m["alt"])}" width="900" height="1125"{" loading=\"lazy\"" if n else ""}>'
                   for n, m in enumerate(i.get("imagens", []))) or '<div class="ph" aria-hidden="true"></div>'
    det = "".join(f'<div><dt>{e(d["rotulo"])}</dt><dd>{e(d["valor"])}</dd></div>' for d in i.get("detalhes", []))
    faq = "".join(f'<details><summary>{e(f["p"])}</summary><p>{e(f["r"])}</p></details>' for f in i.get("faq", []))
    if i.get("link_compra"):
        acao = f'<a class="btn" href="{e(i["link_compra"])}" rel="noopener" target="_blank">Comprar</a>'
    elif site.get("whatsapp"):
        acao = f'<a class="btn" href="{e(whatsapp_link("Olá! Tenho interesse em: " + i["nome"] + " (" + BASE + path + ")"))}" rel="noopener" target="_blank">Encomendar pelo WhatsApp</a>'
    else:
        acao = f'<a class="btn" href="{IG_DM}" rel="noopener" target="_blank">Encomendar pelo Instagram</a>'
    acao += '<a class="btn ghost" href="/contato/">Tirar uma dúvida</a>'
    preco = f'<p class="price big">{preco_fmt(i["preco"])}</p>' if i.get("preco") else ""
    cat = categorias.get(i.get("categoria"), "")
    relacionados = [r for r in itens if r is not i and r.get("categoria") == i.get("categoria")][:3]
    rel_html = (f'<section class="band"><h2>Da mesma série</h2><div class="grid">{"".join(card(r) for r in relacionados)}</div></section>'
                if relacionados else "")
    body = f"""<nav class="crumbs" aria-label="Você está em"><a href="/">Início</a> / <a href="/vitrine/">Vitrine</a> / <span aria-current="page">{e(i['nome'])}</span></nav>
<article class="product">
  <div class="gallery">{imgs}</div>
  <div class="product-info">
    <p class="item-cat">{e(cat)}</p>
    <h1>{e(i['nome'])}</h1>
    <p class="lede">{e(i.get('resumo',''))}</p>
    {preco}
    <div class="actions">{acao}</div>
    <div class="prose">{''.join(f'<p>{e(p)}</p>' for p in i.get('descricao', []))}</div>
    {f'<dl class="specs">{det}</dl>' if det else ''}
    {f'<section class="faq"><h2>Perguntas frequentes</h2>{faq}</section>' if faq else ''}
  </div>
</article>
{rel_html}"""
    lds = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Vitrine", "item": BASE + "/vitrine/"},
        {"@type": "ListItem", "position": 3, "name": i["nome"], "item": BASE + path}]}]
    if i.get("preco") and i.get("imagens"):  # Product só com dados reais e completos
        lds.append({"@context": "https://schema.org", "@type": "Product", "name": i["nome"],
                    "description": i.get("resumo", ""), "image": [BASE + m["src"] for m in i["imagens"]],
                    "brand": {"@type": "Brand", "name": site["nome"]},
                    "offers": {"@type": "Offer", "price": f'{i["preco"]:.2f}', "priceCurrency": "BRL",
                               "availability": "https://schema.org/" + i.get("disponibilidade", "InStock"),
                               "url": BASE + path}})
    if i.get("faq"):
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["p"], "acceptedAnswer": {"@type": "Answer", "text": f["r"]}} for f in i["faq"]]})
    og = i["imagens"][0]["src"] if i.get("imagens") else "/assets/img/og.png"
    write(path, page(path, f"{i['nome']} | {cat}" if cat else i["nome"], i.get("resumo") or site["descricao_curta"],
                     body, "/vitrine/", lds, og_img=og, og_type="product"))

# ---------- Sobre ----------
sobre = f"""<section class="page-head"><h1>Sobre o Nêspera Studio</h1></section>
<section class="band split">
  <h2>O estúdio</h2>
  <div class="prose">{''.join(f'<p>{e(p)}</p>' for p in site['sobre'])}
  <p>Acompanhe o estúdio em <a href="{IG}" rel="noopener" target="_blank">@{e(site['instagram'])}</a> e o artista em <a href="{IG_ART}" rel="noopener" target="_blank">@{e(site['instagram_artista'])}</a>.</p></div>
</section>
<section class="band cta"><p class="cta-title">Conheça o que está saindo do ateliê.</p><div class="actions"><a class="btn" href="/vitrine/">Explorar a vitrine</a></div></section>"""
write("/sobre/", page("/sobre/", "Sobre", "Conheça o Nêspera Studio, estúdio de artes visuais criado em 2026.", sobre, "/sobre/",
                      [org_ld()]))

# ---------- Conteúdos ----------
cont = f"""<section class="page-head"><h1>Conteúdos</h1><p class="lede">Publicações selecionadas do Instagram do estúdio.</p></section>
<section class="band"><div class="posts">{posts_html}</div>
<p class="more"><a class="btn" href="{IG}" rel="noopener" target="_blank">Ver o perfil completo</a></p></section>"""
write("/conteudos/", page("/conteudos/", "Conteúdos", "Publicações e trabalhos recentes do Nêspera Studio.", cont, "/conteudos/"))

# ---------- Contato ----------
canais = [f'<li><a href="{IG_DM}" rel="noopener" target="_blank">Mensagem no Instagram</a></li>']
if site.get("whatsapp"):
    canais.append(f'<li><a href="{e(whatsapp_link("Olá! Vim pelo site do Nêspera Studio."))}" rel="noopener" target="_blank">WhatsApp</a></li>')
if site.get("email"):
    canais.append(f'<li><a href="mailto:{e(site["email"])}">{e(site["email"])}</a></li>')
contato = f"""<section class="page-head"><h1>Contato</h1><p class="lede">Encomendas, dúvidas sobre obras ou parcerias.</p></section>
<section class="band contact">
  <div><h2>Canais</h2><ul class="channels">{''.join(canais)}</ul></div>
  <form class="form" name="contato" method="POST" action="/obrigado/" data-netlify="true" netlify-honeypot="empresa" novalidate>
    <input type="hidden" name="form-name" value="contato">
    <p class="hp"><label>Não preencha <input name="empresa" tabindex="-1" autocomplete="off"></label></p>
    <div class="field"><label for="c-nome">Nome</label><input id="c-nome" name="nome" autocomplete="name" required minlength="2"><p class="err" aria-live="polite"></p></div>
    <div class="field"><label for="c-email">E-mail</label><input id="c-email" type="email" name="email" autocomplete="email" required><p class="err" aria-live="polite"></p></div>
    <div class="field"><label for="c-assunto">Assunto</label>
      <select id="c-assunto" name="assunto" required><option value="">Escolha um assunto</option><option>Encomenda</option><option>Dúvida sobre uma obra</option><option>Parceria</option><option>Outro</option></select><p class="err" aria-live="polite"></p></div>
    <div class="field"><label for="c-msg">Mensagem</label><textarea id="c-msg" name="mensagem" rows="6" required minlength="10"></textarea><p class="err" aria-live="polite"></p></div>
    <label class="check"><input type="checkbox" name="consentimento" value="sim" required><span>Autorizo o uso destes dados para responder ao meu contato, conforme a <a href="/privacidade/">política de privacidade</a>.</span></label>
    <p class="err err-check" aria-live="polite"></p>
    <button class="btn" type="submit">Enviar mensagem</button>
  </form>
</section>"""
write("/contato/", page("/contato/", "Contato", "Fale com o Nêspera Studio sobre encomendas, obras e parcerias.", contato, "/contato/"))

# ---------- Obrigado ----------
write("/obrigado/", page("/obrigado/", "Mensagem enviada", "Confirmação de envio.", f"""<section class="page-head center">
<h1>Mensagem enviada</h1><p class="lede">Recebemos seus dados. O estúdio responde pelo e-mail informado.</p>
<div class="actions"><a class="btn" href="/">Voltar ao início</a><a class="btn ghost" href="{IG}" rel="noopener" target="_blank">Seguir no Instagram</a></div></section>""",
                         noindex=True))

# ---------- Privacidade ----------
priv_contato = site.get("email") or f"mensagem no Instagram @{site['instagram']}"
priv = f"""<section class="page-head"><h1>Política de privacidade</h1><p class="lede">Atualizada em {datetime.date.today().strftime('%d/%m/%Y')}.</p></section>
<section class="band"><div class="prose wide">
<h2>Quais dados coletamos</h2><p>Só os dados que você envia pelos formulários: nome, e-mail, assunto e mensagem (contato) ou e-mail (aviso de lançamento).</p>
<h2>Para que usamos</h2><p>Para responder ao seu contato e, se você autorizar, avisar sobre o lançamento de produtos. Não vendemos nem compartilhamos seus dados para publicidade.</p>
<h2>Onde ficam armazenados</h2><p>Os envios são processados pelo serviço de formulários da hospedagem do site (Netlify) e acessados apenas pelo estúdio.</p>
<h2>Cookies e medição</h2><p>O site não usa cookies de publicidade. A medição de audiência (Google Analytics), quando ativa, só é carregada depois do seu consentimento.</p>
<h2>Seus direitos (LGPD)</h2><p>Você pode pedir acesso, correção ou exclusão dos seus dados a qualquer momento pelo canal: {e(priv_contato)}.</p>
</div></section>"""
write("/privacidade/", page("/privacidade/", "Política de privacidade", "Como o Nêspera Studio trata os dados enviados pelo site.", priv))

# ---------- 404 ----------
write("/404.html", page("/404.html", "Página não encontrada", "Esta página não existe.", """<section class="page-head center">
<p class="type-line">404</p><h1>Página não encontrada</h1><p class="lede">O endereço pode ter mudado ou a peça saiu da vitrine.</p>
<div class="actions"><a class="btn" href="/">Ir para o início</a><a class="btn ghost" href="/vitrine/">Ver a vitrine</a></div></section>""",
                        noindex=True))

# ---------- Assets, sitemap, robots ----------
shutil.copytree(SRC / "assets", DIST / "assets", dirs_exist_ok=True)
sm = "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{HOJE}</lastmod></url>" for p in paginas_sitemap)
(DIST / "sitemap.xml").write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
(DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /obrigado/\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
print(f"OK: {len(paginas_sitemap)} páginas no sitemap, {len(itens)} itens na vitrine ({cat_file}).")
