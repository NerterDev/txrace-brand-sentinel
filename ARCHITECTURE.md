# Architecture Proposal — TX RACE Brand Sentinel

**Status:** PROPOSED — not yet human approved.

## Principle
This document is a proposal, not a statement of truth. The project Harness must distinguish facts from assumptions and hypotheses.

## Project idea
PROMPT TÉCNICO MESTRE: TX RACE BRAND SENTINEL & ADVANCED RADAR SPA (GITOPS & HARNESS TIER-S)

Atua como Arquiteto de Software Sénior e Especialista em Dashboards de Telemetria e Intelligence. Inicializa e desenvolve de raiz o projeto TX RACE Brand Sentinel para a organização NerterDev, governado integralmente pelo AI Harness (Tier-S).

O projeto é focado em transformar o repositório num Radar de Inteligência de Marca Global 360º executado pelo GitHub Actions e servido visualmente em https://nerterdev.github.io/txrace-brand-sentinel/
 com o mais alto nível de informação, detalhe forense e capacidade analítica possível (sem recurso a bots de Telegram).

1. VISÃO DO ENTORNO GRÁFICO (WEB SPA NO GITHUB PAGES)

O painel deve ser uma Single Page Application (SPA) em Dark Theme de alto contraste, inspirada no layout técnico do Sentinel Observability (nerterdev.github.io/sentinel-observability/), mas desenhada para visualização densa de inteligência competitiva e escuta social:

text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🌐 TX RACE BRAND SENTINEL                     ● Radar Ativo (GitHub Runner)  Última ronda: 06/11, 22:50  [ 🔄 Forçar Varredura ] │
│    Plataforma Global de Inteligência de Marca & Social Listening                                [ 📥 Exportar CSV/JSON ] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ VISUALIZAÇÃO: [ ▦ Cartões Detalhados ]  [ ☰ Tabela Densa ]  [ 📈 Gráficos & Analytics ]  [ 🗺️ Mapa de Menções ]         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FILTROS:                                                                                                               │
│ Plataforma: [Todas (10) ▼]  Modelo: [Todos ▼]  Geração: [Todas ▼]  Intenção: [Todas ▼]  País: [Todos ▼]  Data: [Últimos 30D ▼] │
│ Pesquisa: [ 🔍 Pesquisar em tempo real por palavra, autor ou fórum...                       ]  [ 184 MENÇÕES FILTRADAS ] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KPI METRICS:                                                                                                           │
│ ┌────────────────────────┐ ┌────────────────────────┐ ┌────────────────────────┐ ┌────────────────────────┐ ┌────────┐│
│ │ TOTAL MENÇÕES (30D)    │ │ ALCANCE ESTIMADO       │ │ VÍDEOS VIRAIS (>10K)   │ │ LEADS DE COMPRA ATIVAS │ │ SENT.  ││
│ │ 1.842 (+18% vs mês ant)│ │ 428.500 visualizações  │ │ 16 conteúdos virais    │ │ 42 pessoas a perguntar │ │ 94% +  ││
│ └────────────────────────┘ └────────────────────────┘ └────────────────────────┘ └────────────────────────┘ └────────┘│
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FEED DE MENÇÕES DE ALTA DENSIDADE (GRID RESPONSIVO 3 COLUNAS):                                                         │
│ ┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐ ┌──────────────────────────────────┐ │
│ │ [YouTube] Chase Builds Bikes         │ │ [ThumperTalk] MotoGuy_SoCal          │ │ [Facebook] KX 2-Stroke Gang      │ │
│ │ "CR125 Transformation with TXRACE!"  │ │ "New TX Race Restyle Kit for CRF250X"│ │ "Anyone tried TX Race on 97 KX?" │ │
│ │ 🏷️ HONDA CR125 · GEN25  [ 🔥 VIRAL ]  │ │ 🏷️ HONDA CRF250X · GEN2 [ 🛒 COMPRA ] │ │ 🏷️ KAWASAKI KX250  [ 💬 TÉCNICA ]  │ │
│ │ 📍 San Diego, Califórnia, EUA        │ │ 📍 Ontário, Canadá                   │ │ 📍 Texas, EUA                    │ │
│ │ 👁️ 54.2K views  💬 182 com.  👍 2.8K │ │ 👁️ 2.4K views  💬 28 com.           │ │ 💬 42 com.  ↗️ 8 partilhas       │ │
│ │ 🕒 Publicado: Há 3 dias (03/11)      │ │ 🕒 Publicado: Ontem às 19:40         │ │ 🕒 Publicado: Há 5 horas         │ │
│ │ Excerto: "...fitment on the 2003 CR  │ │ Excerto: "...where can I order the   │ │ Excerto: "...is the seat foam    │ │
│ │ was dead simple, seat is amazing..." │ │ restyle kit in Canada? Is shipping.."│ │ comfortable for long motos?..."  │ │
│ │ [ Mini-Gráfico Série 30 Dias ]       │ │ [ Mini-Gráfico Série 30 Dias ]       │ │ [ Mini-Gráfico Série 30 Dias ]   │ │
│ │ [ 📑 Dossiê Forense ] [ 🔗 Abrir Post ]│ │ [ 📑 Dossiê Forense ] [ 🔗 Abrir Post ]│ │ [ 📑 Dossiê Forense ] [ 🔗 Abrir ]│ │
│ └──────────────────────────────────────┘ └──────────────────────────────────────┘ └──────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
2. MÓDULOS DE INFORMAÇÃO MÁXIMA DO DASHBOARD

O entorno gráfico deve disponibilizar 4 modos de visualização acessíveis por abas:

A. Vista de Cartões Ricos (Cards View)

Cada cartão de menção deve exibir a totalidade dos metadados extraídos:

Identificação de Plataforma e Autor: Logótipo SVG da rede, nome da conta/canal e link para o perfil do autor.
Modelo e Geração Detetados: Badges com cores distintas por marca:
Honda (Vermelho): CR125, CR250, CR500, CRF450R, CRF250X
Kawasaki (Verde): KX125, KX250
Suzuki (Amarelo) / Yamaha (Azul): RM125/250, YZ125/250
Geração do Kit: Gen2, Gen24, Gen25.
Classificação de Intenção:
🛒 COMPRA ATIVA: Utilizadores a perguntar onde comprar, preços, tempos de envio ou stock.
🔥 VIRAL: Conteúdos com mais de 10.000 visualizações.
🛠️ PROJETO / BUILD: Transformações e instalações passo a passo.
❓ DÚVIDA / TÉCNICA: Perguntas sobre assento, montagem de plásticos ou compatibilidade de gráficos.
Métricas de Engajamento: Contador de visualizações, comentários, reações (gostos/upvotes) e partilhas.
Geolocalização / Origem Estimada: Identificação do país ou cidade de onde partiu o conteúdo.
Mini-Gráfico de Série Temporal: Histograma SVG dos últimos 30 dias mostrando a evolução das menções.
B. Vista de Tabela Densa (Data Table View)
Tabela estilo folha de cálculo corporativa com ordenação por qualquer coluna (Data, Relevância, Plataforma, Engajamento).
Exportação com um clique para ficheiro CSV ou JSON contendo todas as linhas filtradas.
C. Vista de Gráficos e Analytics (Analytics View)
Gráficos em SVG nativo de alto rendimento (sem bibliotecas pesadas externas):
Evolução Diária: Gráfico de linhas/barras com o volume de menções por dia.
Share de Modelos: Gráfico circular com os modelos mais procurados (ex: 60% CR250, 25% KX250, 15% CRF).
Distribuição por Canal: Gráfico de barras comparativo (YouTube vs Fóruns vs Facebook vs Instagram vs Reddit).
D. Gaveta Lateral de Investigação Forense (ForensicDrawer)

Ao clicar em "Dossiê Forense", uma gaveta lateral desliza suavemente exibindo:

Texto Completo Original: Leitura integral da publicação ou transcrição do vídeo.
Tradução Automática: Botão para traduzir o texto instantaneamente para Português (útil para fóruns em inglês, francês ou italiano).
Análise de Intenção da IA: Resumo curto do que o cliente pretende (ex: "Piloto à procura de kit para CR250 de 2001, tem dúvidas sobre o conforto do assento").
Resposta Recomendada (Copy-Paste): Mensagem pronta e personalizada em inglês/espanhol para a equipa da TX RACE comentar na publicação com o link correto da loja.
3. ARQUITETURA DE DADOS (10 CONECTORES EXTENSÍVEIS)

A aplicação executa em Python 3.12 com uma arquitetura modular de plugins:

text
src/connectors/
├── base.py              # Interface abstrata BaseConnector
├── registry.py          # Loader dinâmico que instancia conectores registados
├── youtube.py           # YouTube Data API v3 (Vídeos e Shorts)
├── tiktok.py            # Coletor de transformações virais no TikTok
├── instagram.py         # Rastreio de hashtags (#txrace, #cr250restyle) e @txrace
├── facebook.py          # Grupos públicos e Facebook Marketplace
├── reddit.py            # PRAW (r/Dirtbikes, r/Motocross, r/supercross)
├── twitter.py           # X / Twitter API v2 / Nitter RSS
├── forums.py            # ThumperTalk, VitalMX, DirtRider, MotoVerte
├── marketplaces.py      # eBay Motors, Craigslist, Wallapop, Leboncoin
└── rss_web.py           # Google Alerts RSS e Bing News
4. GITOPS ENGINE & DEPLOY NO GITHUB PAGES

Cria o ficheiro .github/workflows/sentinel_radar.yml:

Agendamento: Cron a cada 4 horas (0 */4 * * *) + workflow_dispatch com inputs manuais.
Execução:
Instala dependências em ubuntu-latest.
Executa python -m src.main, que recolhe as 10 fontes, processa o motor semântico com filtros negativos, calcula scores de prioridade e gera a base consolidada.
Exporta os ficheiros para dashboard/data/:
current_mentions.json (todas as menções normalizadas e enriquecidas)
kpis.json (totais consolidados, deltas e métricas de topo)
analytics.json (séries temporais de 30 dias e distribuições por modelo/canal)
Commit GitOps: Realiza o commit automático de dashboard/data/ com o utilizador github-actions[bot].
Deploy Automático: Publica a pasta dashboard/ diretamente no GitHub Pages (https://nerterdev.github.io/txrace-brand-sentinel/).
5. ESTRUTURA DO REPOSITÓRIO HARNESS
text
txrace-brand-sentinel/
├── .github/
│   └── workflows/
│       └── sentinel_radar.yml
├── .harness/
│   ├── contract.yaml
│   ├── policy.yaml
│   ├── verification.yaml
│   ├── state.json
│   └── invariants/
│       ├── ux_contract.yaml         # Contrato visual Dark Theme, escala 4/8pt e 7 estados
│       └── connector_contract.yaml
├── config/
│   ├── settings.yaml
│   ├── sources.yaml                 # Catálogo extensível de fontes
│   └── keywords.yaml                # Motor de keywords, modelos e filtros negativos
├── dashboard/                       # WEB SPA SERVIDO NO GITHUB PAGES
│   ├── index.html                   # Estrutura semântica e acessível
│   ├── styles.css                   # Tokens Dark Theme Sentinel (#0B0F17, #111827, #1F2937)
│   ├── app.js                       # Reatividade pura, modais, filtros instantâneos e paginação
│   └── data/
│       ├── current_mentions.json
│       ├── kpis.json
│       └── analytics.json
├── src/
│   ├── connectors/
│   ├── engine/
│   │   ├── matcher.py               # Lógica booleana de keywords e exclusão
│   │   ├── deduplicator.py          # Hash SHA-256 e base SQLite local
│   │   ├── prioritizer.py           # Cálculo do score de relevância e intenção de compra
│   │   └── ddos_guard.py            # Rate limiter com exponential backoff
│   ├── dispatchers/
│   │   ├── json_exporter.py         # Gerador dos dados para o dashboard
│   │   └── sheets_dispatcher.py     # Sincronização Google Sheets (opcional)
│   ├── models/
│   │   └── mention.py               # MentionDTO imutável
│   └── main.py                      # Orquestrador CLI
├── tests/
│   ├── test_connectors.py
│   ├── test_matcher.py
│   └── test_dashboard_contract.py   # Testes determinísticos dos estados da UI
├── receipts/
├── AGENTS.md
└── PROJECT.md
6. PLANO DE TAREFAS HARNESS

Inicia o desenvolvimento respeitando rigorosamente o ciclo:

TASK-001: Bootstrap do repositório, configuração do .harness/, MentionDTO e carregador dinâmico de conectores (registry.py).
TASK-002: Implementação do Motor de Keywords (matcher.py), filtros negativos e deduplicador SQLite.
TASK-003: Conectores de Vídeo e Redes (YouTube v3, TikTok, Instagram, Reddit PRAW, Facebook Groups).
TASK-004: Conectores de Fóruns (ThumperTalk, VitalMX, RSS) e Marketplaces (eBay, Wallapop).
TASK-005: Desenvolvimento do Painel Web SPA de Alta Densidade (dashboard/index.html, styles.css, app.js) com Dark Theme, KPIs, 4 vistas (Cards, Tabela, Analytics, Dossiê Forense) e filtros em tempo real.
TASK-006: Workflow GitOps (sentinel_radar.yml) para execução agendada a cada 4 horas e deploy contínuo no GitHub Pages (nerterdev.github.io/txrace-brand-sentinel/).
TASK-007: Suíte completa de testes determinísticos e encerramento com receipt-TASK-FINAL.json.

Inicia imediatamente pelo Bootstrap (TASK-001).

O que ganha com este ecossistema:
Zero Distrações por Telegram: Sem mensagens chatas no telemóvel a toda a hora. O Luís abre o link nerterdev.github.io/txrace-brand-sentinel/ quando quiser e tem um painel executivo e operacional completo.
Inteligência Prática de Vendas: O painel não mostra apenas links — categoriza automaticamente quem tem dinheiro na mão para comprar (COMPRA ATIVA) e sugere a resposta oficial para a equipa da TX RACE comentar no post.
Padrão Idêntico ao Sentinel Observability: O mesmo tema escuro, os mesmos botões de ação e a mesma fluidez rápida que já utiliza no projeto das lojas.

## Candidate architecture
The Architect should document components, interfaces, data flow, deployment, failure modes, and verification boundaries here.

## Alternatives
At least one alternative should be recorded whenever a structural decision is consequential.

## Assumptions
See `.harness/assumptions.yaml`. Do not silently promote assumptions to facts.

## Open questions
See `.harness/assumptions.yaml` and `.harness/architecture-options.yaml`.

## Architecture challenge
See `.harness/architecture-review.yaml`. The architecture is not approved until the challenge findings have been reviewed.

## Human decision
See `DECISIONS.md`.


## V6 Cost Control and Antigravity

Model selection is a human-controlled boundary. Context Optimizer and deterministic tooling reduce token consumption without selecting a model. Antigravity remains the execution environment; the Harness supplies contracts, task context, worktrees and evidence gates.
