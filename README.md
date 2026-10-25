# Site Nêspera Studio

Site estático (HTML gerado por Python, sem dependências). Hospedagem recomendada: **Netlify** (HTTPS grátis, formulários prontos, deploy automático).

## Estrutura

```
build.py                 gerador: lê data/ e cria dist/
data/site.json           nome, domínio, Instagram, WhatsApp, e-mail, GA4, texto "Sobre"
data/catalog.json        produtos da vitrine (vazio = mostra "em breve" + lista de lançamento)
data/catalog.example.json  modelo de produto (não é publicado)
data/conteudos.json      cartões da seção Conteúdos
src/assets/              CSS, JS, fontes (auto-hospedadas) e imagens
netlify.toml             build, cabeçalhos de segurança, redirecionamento
```

Testar localmente:
```
python3 build.py && cd dist && python3 -m http.server 8000
EXEMPLO=1 python3 build.py   # pré-visualiza a vitrine com um produto de exemplo
```

## 1. Publicar no Netlify

1. Suba esta pasta para um repositório no GitHub.
2. Netlify > Add new site > Import from Git > escolha o repositório. Build e pasta já vêm do `netlify.toml`.
3. Netlify > Forms: ative a detecção de formulários e, em *Form notifications*, adicione o e-mail que deve receber os envios. Os formulários "contato" e "lista-lancamento" aparecem após o primeiro deploy.

## 2. Domínio próprio

O site está configurado para `https://nespera.studio` (em `data/site.json` > `url`). **Confirme a disponibilidade antes** (registro.br para `.com.br`; Namecheap, Cloudflare ou Porkbun para `.studio`). Alternativas: `nesperastudio.com.br`, `nespera.art.br`, `nesperastudio.com`.

1. Registre o domínio e troque `url` em `site.json` se escolher outro.
2. Netlify > Domain management > Add domain.
3. No registrador: use os nameservers do Netlify (mais simples) **ou** crie `A @ 75.2.60.5` e `CNAME www <seu-site>.netlify.app`.
4. Ative HTTPS (Let's Encrypt, automático) e defina o domínio sem `www` como principal.
5. Descomente o bloco de redirecionamento no `netlify.toml`, trocando `SEU-SITE`.

## 3. Google Search Console

1. search.google.com/search-console > Adicionar propriedade > **Domínio** > digite o domínio.
2. Copie o registro TXT e crie no DNS (Netlify DNS ou registrador). Clique em Verificar.
3. Sitemaps > envie `sitemap.xml`.
4. Inspeção de URL > cole a página inicial > *Solicitar indexação*. Repita para /vitrine/ e para cada produto novo.
5. Acompanhe em *Páginas* e *Desempenho*. Indexação costuma levar de dias a semanas; não há garantia de posição.

## 4. Google Analytics 4 (opcional)

Crie a propriedade GA4, copie o ID `G-XXXXXXX` para `ga4_id` em `site.json`. O script só carrega depois que o visitante aceita no aviso de cookies.

## 5. Atualizar a vitrine

Edite `data/catalog.json` seguindo o `catalog.example.json`, coloque as fotos em `src/assets/img/` (WebP, ~1200px no lado maior) e faça commit. O Netlify gera tudo de novo: páginas `/vitrine/<slug>/`, sitemap e dados estruturados.

- `preco`: número ou `null` (sem preço, o item não recebe dados de Produto no Google).
- `link_compra`: link de loja/checkout. Sem ele, o botão abre WhatsApp (se configurado) ou mensagem no Instagram.
- Filtros aparecem com 6+ itens em 2+ categorias; busca com 9+ itens.
- `destaque: true` coloca o item na página inicial.

## Checklist

**Concluído**
- Páginas: Início, Vitrine (estado "em breve" + lista de lançamento), páginas de produto automáticas, Sobre, Conteúdos, Contato, Privacidade (LGPD), Obrigado, 404.
- Identidade: preto e branco do perfil, wordmark com pássaro, tipografia de máquina de escrever, cores da ilustração como acento.
- SEO: títulos e descriptions únicos, canonical, Open Graph, Organization/WebSite, BreadcrumbList, ItemList, Product e FAQPage (só com dados reais), sitemap.xml, robots.txt, hierarquia de títulos, textos alternativos.
- Formulários com validação, honeypot anti-spam e envio real via Netlify Forms.
- Menu móvel, foco visível por teclado, movimento reduzido respeitado, fontes auto-hospedadas, CSP e cabeçalhos de segurança, nenhuma chave exposta.
- Testado: sem erros de console, validação e menu funcionando em 390px e 1366px.

**Depende de você**
- [ ] Logotipo oficial em SVG (hoje é uma recriação tipográfica).
- [ ] Imagens em alta resolução (a ilustração atual veio de um print e está em baixa).
- [ ] Produtos reais: nomes, descrições, fotos, preços, forma de compra.
- [ ] Texto "Sobre" completo (história, técnica, quem cria).
- [ ] WhatsApp e e-mail comercial em `site.json`.
- [ ] Links diretos de cada post em `conteudos.json` (hoje apontam para o perfil).
- [ ] Registrar domínio, configurar DNS e HTTPS.
- [ ] Ativar notificações de e-mail do Netlify Forms.
- [ ] Search Console (e GA4, se quiser).
- [ ] Colocar o link do site na bio do Instagram.
