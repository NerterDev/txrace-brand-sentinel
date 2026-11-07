# UX/UI & DESIGN SYSTEM MASTER STANDARD (UX.md)

**Version:** 5.1  
**Status:** Production Master Standard  
**Scope:** WordPress + WooCommerce themes, plugins, admin interfaces, storefronts, Gutenberg blocks and checkout experiences.

---

## 1. Purpose

This document is the **Single Source of Truth (SSOT)** for UX, UI, visual design, interaction, accessibility, responsive behavior, ergonomics and conversion standards.

It defines **what the user should experience**.

Engineering architecture, PHP, JavaScript, database, security, performance budgets, testing and deployment rules belong to `rules.md`.

Canonical component implementation belongs to `UI_COMPONENTS.md`.

Acceptance, regression and release criteria belong to `QA.md`.

History belongs to `CHANGELOG.md`.

---

# 2. Document Authority

## 2.1 UX.md owns

- Visual hierarchy
- Design tokens
- Typography
- Colors
- Spacing
- Sizing
- Responsive behavior
- Components
- Interaction states
- Accessibility UX
- Ergonomics
- CRO/microcopy
- Loading/error/success experiences
- Admin visual system
- Storefront visual system

## 2.2 rules.md owns

- PHP architecture
- JavaScript architecture
- CSS architecture
- WordPress APIs
- WooCommerce APIs
- Security
- Database
- HPOS
- Performance engineering
- Asset loading
- Dependencies
- Compatibility
- Testing architecture
- Deployment
- Migrations
- Lifecycle

## 2.3 Conflict precedence

When requirements conflict, use:

1. Security
2. Legal/platform requirements
3. Accessibility
4. WordPress/WooCommerce compatibility
5. The applicable governing document
6. Existing public API/behavior compatibility
7. Implementer preference

UX.md must not redefine engineering architecture.  
rules.md must not redefine visual tokens without an explicit UX decision.

---

# 3. Fundamental Design Principles

## 3.1 Accessibility first

Target:

- WCAG 2.1 AA minimum
- Keyboard operability
- Visible focus
- Semantic HTML
- Screen-reader compatibility
- Logical focus order
- Sufficient contrast
- Reduced-motion support
- Accessible form errors
- Accessible loading states

Minimum normal text contrast:

**4.5:1**

Large text may use the WCAG-defined relaxed threshold where applicable.

Do not rely exclusively on:

- Color
- Animation
- Position
- Icons
- Hover
- Placeholder text

to communicate meaning.

---

# 4. Design Grid

Use an **8pt spacing grid**.

Preferred values:

```text
4   micro adjustment
8   base
16  standard
24  section
32  major section
40  large
48  touch / major spacing
64  major layout
80+
```

Avoid arbitrary values unless required by:

- Browser rendering
- Typography
- Existing platform dimensions
- Component geometry
- Third-party platform constraints

---

# 5. Interaction Targets

Minimum interactive target:

**48 × 48 px**

This applies especially to:

- Buttons
- Icon buttons
- Checkboxes
- Switches
- Radio controls
- Quantity controls
- Navigation controls
- Mobile controls

Visual glyphs may be smaller than 48px while their hit area remains >=48px.

---

# 6. Responsive Strategy

## Mobile first

Design and implement from the smallest practical viewport upward.

Baseline:

```text
Mobile
Tablet
Desktop
Large desktop
```

Never assume desktop hover exists.

Mobile must support:

- Touch
- One-handed interaction
- Large controls
- Clear hierarchy
- Minimal cognitive load
- No horizontal overflow
- No accidental taps

---

# 7. Ergonomics

Apply:

- Fitts's Law
- Hick-Hyman Law
- Gestalt principles
- Thumb-zone optimization
- Progressive disclosure
- Recognition over recall

Primary actions should be:

- Obvious
- Reachable
- Visually dominant
- Semantically explicit

Do not make users search for the next action.

---

# 8. Typography

Typography must prioritize:

1. Legibility
2. Hierarchy
3. Scanability
4. Consistency
5. Performance

Recommended characteristics:

- Clear sans-serif
- High x-height
- Good numeral distinction
- Adequate line height
- Limited font weights

Mobile form fields must use at least:

**16px**

to reduce browser zoom behavior on mobile platforms.

Use tabular numerals for:

- Prices
- Totals
- Quantities
- Financial values
- Statistics
- Dashboards

---

# 9. Color Tokens

## Storefront

```css
:root {
  --color-primary: #0066CC;
  --color-primary-hover: #0052A3;
  --color-dark: #111827;
  --color-surface: #FFFFFF;
  --color-subtle: #FAFAFA;
  --color-border: #E5E7EB;
  --radius-sm: 8px;
  --radius-md: 10px;
  --radius-lg: 12px;
}
```

Color must never be hard-coded repeatedly inside component CSS.

Dynamic values must be exposed as CSS custom properties.

Do not generate large dynamic CSS strings through PHP.

---

# 10. Icons

Preferred icon system:

- Inline SVG
- Monochromatic
- Black/white or `currentColor`
- Minimal geometry
- No unnecessary fills
- No icon font
- No heavy icon library

Canonical icon characteristics:

```text
24 × 24 viewBox
stroke="currentColor"
fill="none"
stroke-width="1.75"
```

Target average:

**<400 bytes/icon**

Icons must have:

- Accessible labels where meaningful
- `aria-hidden="true"` when decorative
- Adequate touch target when interactive

---

# 11. CSS Isolation

All plugin-owned storefront UI must be scoped.

Preferred wrappers:

```html
<div class="ao-scope">
```

or:

```html
<div id="checkoutoptima-root">
```

Rules:

- No global `button {}` from a plugin
- No global `input {}`
- No global `a {}`
- No global heading overrides
- No global body styling
- Avoid `!important`
- Avoid selectors that depend on a specific theme
- Never mutate the theme's global design system unintentionally

---

# 12. Buttons

## Product page

Desktop:

**52px height**

Mobile:

**56px height**

Primary mobile CTA:

**Full width**

## Checkout

Desktop:

**50–54px**

Mobile:

**56px**, preferably full width for the primary action.

Buttons must have states:

```text
idle
hover
focus
active
loading
success
disabled
error where applicable
```

Loading must:

- Preserve layout
- Prevent duplicate submission
- Communicate progress
- Preserve accessible state
- Restore state on failure

---

# 13. Button Microcopy

Avoid vague:

- Continuar
- Submeter
- Comprar
- OK

Prefer explicit action-oriented language where context allows:

- Finalizar compra
- Guardar alterações
- Aplicar cupão
- Confirmar pagamento
- Adicionar ao carrinho
- Ver detalhes

Microcopy should communicate:

**what happens next**.

---

# 14. Forms

Inputs:

**48–50px minimum**

Mobile:

**16px font minimum**

Use:

- Explicit labels
- Helpful descriptions
- Clear required indicators
- Inline validation
- Specific error messages
- Preserved values after errors
- Logical tab order

Never rely on placeholders as labels.

Errors should explain:

1. What is wrong
2. How to fix it

---

# 15. Loading States

Every asynchronous interaction must have an explicit loading state.

Requirements:

- No layout shift
- No duplicate requests
- `aria-busy="true"` where appropriate
- Disable repeated action while processing
- Restore control on completion/failure
- Prefer lightweight CSS spinner

Example:

```css
.spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-right-color: transparent;
  animation: spin .65s linear infinite;
}
```

Respect:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms;
    animation-iteration-count: 1;
    transition-duration: 0.01ms;
  }
}
```

---

# 16. Product Listing Page (PLP)

Preferred grid:

```text
Mobile: 2 columns
Desktop: 4 columns
```

Cards:

- 8–10px radius
- Square product imagery where appropriate
- Consistent image ratio
- Line-clamped titles
- Tabular prices
- Ratings using accessible SVG
- Bottom-aligned primary action
- Consistent vertical rhythm

Avoid variable card heights caused by uncontrolled content.

---

# 17. Product Detail Page (PDP)

Preferred desktop architecture:

**12-column layout**

Typical split:

```text
6 columns media
6 columns purchase information
```

The purchase decision area must prioritize:

1. Product identity
2. Price
3. Variations
4. Availability
5. Primary CTA
6. Trust
7. Supporting information

Use pill-style swatches for visual product variations where appropriate.

Avoid unnecessary dropdowns when visual selection is materially clearer.

---

# 18. Trust Block

Trust information should be:

- Close to the purchase action
- Scannable
- Concise
- Consistent

Examples:

- Secure payment
- Delivery estimate
- Returns
- Warranty
- Stock status
- Buyer protection where legitimately applicable

Never use fake urgency, fake scarcity or misleading trust claims.

---

# 19. Cart

Cart UX should make the following immediately clear:

- Product
- Variation
- Quantity
- Unit price
- Discounts
- Shipping
- Taxes where applicable
- Subtotal
- Total
- Primary checkout action

Keep titles and metadata compact.

Avoid visual distractions that compete with checkout.

---

# 20. Checkout

Checkout should minimize leakage.

Priorities:

1. Customer information
2. Delivery
3. Payment
4. Order review
5. Final action

Avoid unnecessary:

- Navigation
- Promotional banners
- External links
- Distracting recommendations
- Unrelated CTAs

Errors must appear close to the affected field or section.

---

# 21. WooCommerce Blocks

When Checkout/Cart Blocks are used:

- Follow the native block interaction model
- Do not assume classic checkout hooks exist
- Prefer official Store API / Blocks extension mechanisms
- Preserve native validation
- Preserve native accessibility
- Avoid replacing the entire checkout unnecessarily

Classic checkout and Blocks checkout are separate implementation contexts.

---

# 22. WordPress Admin UX (Padrão Canónico: EU VAT & VIES)

A interface administrativa do Kardeu WooCommerce segue um **Design System SaaS Unificado e Estrito**, cujo modelo canónico e obrigatório de referência (SSOT) é o submenu **EU VAT & VIES Compliance** (`subplugins/eu-vat-compliance`).

Todas as abas, submenus e módulos da suite têm a obrigação inegociável de partilhar a mesma identidade visual, paleta de cores, raio de curvatura, estados de botão com spinner e estrutura de abas.

### Proibições Estritas de Design Admin:
- **PROIBIDO** utilizar barras flutuantes escuras (`kardeu-admin-footer-bar` pretas ou opacas).
- **PROIBIDO** botões de submissão com cores divergentes (ex.: botões cor-de-laranja `#ff7a00` ou pretos no admin).
- **PROIBIDO** abas de navegação retangulares tipo caixa (`nav-tab-wrapper` padrão do WordPress).
- **PROIBIDO** inputs ou botões com `border-radius` desalinhados (ex.: inputs retos de 0px ou excessivamente redondos misturados na mesma tela).
- **PROIBIDO** botões sem suporte a feedback de carregamento (`.kardeu-spinner` / `.is-loading`).

---

# 23. Admin Layout & Estrutura Visual Canónica

O layout administrativo padrão é estruturado em três níveis:

### 1. Cabeçalho SaaS (`.kardeu-header`)
- **Fundo**: Branco (`#FFFFFF`), borda `1px solid #E2E8F0`, `border-radius: 8px 8px 0 0`.
- **Badge do Logótipo (`.kardeu-logo-badge`)**: Caixa quadrada 44x44px, fundo azul claro (`#EFF6FF`), ícone SVG stroke em azul canónico (`#0066CC`), raio 8px.
- **Títulos**:
  - Título Principal (`.kardeu-title`): 20px, font-weight 700, cor `#0F172A`, line-height 1.2.
  - Subtítulo (`.kardeu-subtitle`): 13px, cor `#64748B`, explicativo da funcionalidade do módulo.
- **Ações e Pílulas de Estado (`.kardeu-header-actions`)**:
  - Pílula de Status (`.kardeu-pill.kardeu-pill-success`): Fundo `#DCFCE7`, texto `#16A34A`, ponto verde pulsante de 7px (`.kardeu-pill-dot`), raio 20px.
  - Tag de Versão (`.kardeu-version-tag`): Fundo `#F8FAFC`, borda `1px solid #E2E8F0`, cor `#64748B`, fonte 12px, raio 4px.
  - Ação Primária Opcional: Botão `.kardeu-btn.kardeu-btn-primary` com spinner.

### 2. Faixa de Navegação por Abas (`.kardeu-nav-tabs`)
- **Fundo**: Branco (`#FFFFFF`), borda `1px solid #E2E8F0`, com sublinhado de base `border-bottom: 2px solid #E2E8F0`.
- **Links de Aba (`.kardeu-tab-link`)**:
  - `display: inline-flex; align-items: center; gap: 8px;`
  - Padding: `14px 16px`.
  - Cor normal: Cinzento suave `#64748B`, fonte 14px, weight 600, sem decorações ou caixas.
  - Ícone: SVG stroke 18x18px com `stroke-width: 1.75`.
  - Transição: `all 0.15s ease`.
- **Aba Ativa (`.kardeu-tab-link.is-active`)**:
  - Cor do texto e ícone: Azul canónico `#0066CC`.
  - Indicador ativo: `border-bottom: 3px solid #0066CC; margin-bottom: -2px;`.
  - Proibido qualquer estilo de caixa/botão em abas inativas ou ativas.

### 3. Grelha de Conteúdo & Cartões (`.kardeu-grid` & `.kardeu-card`)
- **Grelha**: Layout de 2 colunas **62% / 38%** (`.kardeu-col-main` e `.kardeu-col-side`) ou coluna única centrada (max-width 1180px).
- **Cartão (`.kardeu-card`)**:
  - Fundo: Branco (`#FFFFFF`).
  - Borda: `1px solid #E2E8F0`.
  - Raio de curvatura: `border-radius: 8px` (ou `0 0 8px 8px` se acoplado às abas).
  - Padding: `24px`.
  - Margem inferior: `24px`.
- **Cabeçalho do Cartão (`.kardeu-card-header`)**:
  - Título (`.kardeu-card-title`): 17px, font-weight 700, cor `#0F172A`.
  - Descrição (`.kardeu-card-desc`): 13px, cor `#64748B`.
  - Borda divisória inferior: `1px solid #E2E8F0`, padding-bottom 14px.
- **Rodapé do Cartão (`.kardeu-card-footer`)**:
  - Margem superior 24px, padding superior 16px, borda superior `1px solid #E2E8F0`.
  - Contém o botão de submissão primário alinhado à esquerda.

---

# 24. Admin Palette (Tokens Estritos SSOT)

A paleta de administração é estritamente fixada nos seguintes valores:

```css
:root {
    /* Cores Primárias de Ação */
    --kardeu-primary:       #0066CC;
    --kardeu-primary-hover: #0052A3;
    --kardeu-primary-light: #EFF6FF;

    /* Superfícies e Fundos */
    --kardeu-bg:            #F8FAFC;
    --kardeu-card-bg:       #FFFFFF;

    /* Bordas e Divisórias */
    --kardeu-border:             #E2E8F0;
    --kardeu-border-hover:       #CBD5E1;
    --kardeu-input-border:       #CBD5E1; /* Borda suave de alto contraste para inputs (Padrão Cart Checkout) */
    --kardeu-input-border-hover: #94A3B8;

    /* Tipografia */
    --kardeu-text:          #0F172A;
    --kardeu-text-muted:    #64748B;

    /* Estados Semânticos */
    --kardeu-success:       #16A34A;
    --kardeu-success-bg:    #DCFCE7;
    --kardeu-danger:        #DC2626;
    --kardeu-danger-bg:     #FEE2E2;

    /* Métrica de Raio Unificada */
    --kardeu-radius:        8px;
    --kardeu-input-radius:  6px;
    --kardeu-input-height:  40px;
    --kardeu-input-shadow:  0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
```

---

# 25. Componentes de Formulário & Botões

### 1. Campos de Entrada Unificados (`.kardeu-input`, `.kardeu-select`, `input[type="text"]`, `select`)
O estilo visual de todos os campos de formulário no backend segue rigorosamente a estética do **Cart & Checkout**, com cantos arredondados, elevação suave e borda de alto contraste:
- **Altura Canónica**: `40px` exatos para todos os inputs de texto, números, URLs, e-mails e selects (Zero inconsistência de altura).
- **Raio de Curvatura**: `6px` estrito (`border-radius: 6px;`). **PROIBIDOS cantos retos/quadrados** ou cantos desiguais entre abas.
- **Borda Suave de Alto Contraste**: `1px solid var(--kardeu-input-border, #CBD5E1);` (Slate-300 é ligeiramente mais escura que o `#E2E8F0` estrutural das caixas para conferir nitidez, separação e contraste superior em relação ao fundo branco).
- **Hover da Borda**: `border-color: var(--kardeu-input-border-hover, #94A3B8);`.
- **Sombra Suave (Elevation)**: `box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);` para criar profundidade refinada de produto SaaS.
- **Foco Canónico**: `border-color: var(--kardeu-primary, #0066CC); box-shadow: 0 0 0 3px var(--kardeu-primary-light, #EFF6FF); outline: none;`.
- **Selects com Chevron Customizado**:
  - `height: 40px !important; line-height: 38px !important;`
  - Padding direito reservado de `38px` para o chevron SVG integrado (`data:image/svg+xml...`), eliminando a seta nativa antiquada do sistema operativo.
  - `-webkit-appearance: none; appearance: none;`
- **Áreas de Texto (`textarea`, `.kardeu-textarea`)**:
  - `min-height: 80px; padding: 10px 12px; border: 1px solid var(--kardeu-input-border, #CBD5E1); border-radius: 6px;`.
- **Escopo de Aplicação**:
  - Aplica-se a classes dedicadas (`.kardeu-input`, `.kardeu-select`, `.kardeu-textarea`) e estende-se a **todos os inputs nativos gerados pelas Settings API do WordPress** (`.kardeu-admin-wrap input[type="text"]`, `.regular-text`, `.form-table input`, `.form-table select`), garantindo coerência absoluta de ponta a ponta.

### 2. Interruptores Switch Acessíveis (`.kardeu-switch-row`)
- Estrutura: Linha flex com texto informativo à esquerda (`.kardeu-switch-info`) e botão switch à direita (`.kardeu-switch`).
- Dimensão do Slider: Largura 44px, Altura 24px, Raio 24px.
- Cor inativa: `#CBD5E1`.
- Cor ativa (`:checked`): `#0066CC` (`var(--kardeu-primary)`).
- Polegar (Thumb): Círculo branco de 18px com sombra `0 1px 2px rgba(0,0,0,0.15)`, translação suave de 20px ao ativar.

### 3. Botões Canónicos de Administração (`.kardeu-btn`) & Barra Flutuante (`.kardeu-card-footer`)
Todos os botões no painel backend devem seguir estritamente o mesmo padrão estético e funcional:
- `display: inline-flex; align-items: center; justify-content: center; gap: 8px;`
- Altura: `40px` exatos.
- Padding horizontal: `20px` (ou `10px 24px` no rodapé flutuante).
- Raio de curvatura: `6px` estrito.
- Tipografia: `14px`, `font-weight: 600`, line-height normal, sem decorações.
- **PROIBIÇÃO DE ÍCONES ESTÁTICOS**:
  - Os botões normais de submissão e ação principal ("Guardar Alterações", etc.) **NÃO DEVEM** conter ícones estáticos (sem dashicons como `dashicons-saved`, sem SVGs inline).
  - O botão em repouso apresenta apenas o texto limpo da ação.
- **Botão Primário (`.kardeu-btn-primary`)**:
  - Fundo: `#0066CC` (`var(--kardeu-primary)`).
  - Texto: `#FFFFFF`.
  - Hover/Focus: `#0052A3` (`var(--kardeu-primary-hover)`).
  - Borda: `none` ou `1px solid transparent`.
- **Botão Secundário (`.kardeu-btn-secondary`)**:
  - Fundo: `#FFFFFF`.
  - Borda: `1px solid #CBD5E1`.
  - Texto: `#0F172A`.
  - Hover: Fundo `#F8FAFC`, borda `#94A3B8`, texto `#0F172A`.
- **Barra de Salvamento Flutuante Universal (Sticky Dock)**:
  - O botão de guardar alterações deve estar **sempre visível e acessível no fundo do ecrã** através de `.kardeu-card-footer` com `position: fixed; bottom: 0; left: 160px; right: 0; z-index: 9999;`.
  - Responde ao estado de colapso do menu WordPress (`body.folded` -> `left: 36px`) e a ecrãs móveis (`<= 782px` -> `left: 0`).
  - O contentor de página `.kardeu-admin-wrap` obriga a `padding-bottom: 90px !important;` para proteger todos os controlos finais contra sobreposição.

### 4. Spinner Universal & Ciclo de Carregamento (`.kardeu-spinner`)
- **TODOS OS BOTÕES DE SUBMISSÃO OU AÇÃO ASSÍNCRONA NO BACKEND TÊM DE FAZER SPINNER**:
  - Não é permitido que formulários guardem sem apresentar feedback visual de carregamento.
  - O spinner deve ser rigorosamente idêntico em todas as abas (`eu-vat-compliance`, `global-settings`, `single-product-grid`, `cart-checkout`, `currency-converter`).
- **Animação CSS Canónica**:
  ```css
  @keyframes kardeu-spin {
      0%   { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
  }

  .kardeu-spinner {
      display: inline-block;
      width: 15px;
      height: 15px;
      border: 2px solid rgba(255, 255, 255, 0.35);
      border-top-color: #FFFFFF;
      border-radius: 50%;
      animation: kardeu-spin 0.65s linear infinite;
      box-sizing: border-box;
      vertical-align: middle;
      flex-shrink: 0;
  }

  .kardeu-btn-secondary .kardeu-spinner {
      border-color: rgba(15, 23, 42, 0.2);
      border-top-color: var(--kardeu-primary, #0066CC);
  }
  ```
- **Ciclo Obrigatório `setButtonLoading(btn, loadingText)`**:
  1. Travar a largura do botão (`btn.style.minWidth = Math.ceil(rect.width) + 'px'`) para garantir **Zero CLS** (sem saltos de layout).
  2. Adicionar a classe `.is-loading` e o atributo `aria-busy="true"`.
  3. Prevenir cliques repetidos com `pointer-events: none !important; cursor: wait !important; opacity: 0.88;`.
  4. Injetar dinamicamente o spinner à esquerda do texto:
     ```html
     <span class="kardeu-spinner" aria-hidden="true"></span> <span>A guardar...</span>
     ```
  5. Se assíncrono (AJAX), restaurar via `resetButtonLoading(btn)`. Se submissão de página normal, o estado permanece ativo até ao recarregamento.

### 5. Banners Informativos e de Integração (`.kardeu-field-info-banner`)
- Fundo azul claro `#EFF6FF`, borda `1px solid #BFDBFE`, raio `8px`, padding `16px 18px`.
- Ícone informativo SVG à esquerda (`color: #0066CC;`).
- Chips de código em linha: Fundo `#F1F5F9`, borda `#CBD5E1`, cor `#0066CC`, fonte mono, raio 4px (`.kardeu-key-code`).

---

# 26. Gutenberg

Use native WordPress block patterns.

Preferred registration:

```php
register_block_pattern();
```

Do not introduce:

- Elementor
- Divi
- Proprietary page builders

unless explicitly required by an existing project.

---

# 27. Conditional Assets

Frontend assets should load only where required.

Use block detection such as:

```php
has_block();
```

Do not load every component's CSS/JS globally.

---

# 28. Tailwind

Tailwind may be used for implementation.

Design tokens must remain centralized.

Dynamic options should use:

```css
:root {
  --component-primary: #0066CC;
}
```

not PHP-generated CSS blobs.

---

# 29. Component State Matrix

Every interactive component should be evaluated for:

| State | Required |
|---|---|
| Idle | Yes |
| Hover | Desktop where applicable |
| Focus | Yes |
| Active | Yes |
| Loading | Async interactions |
| Success | Where applicable |
| Error | Where applicable |
| Disabled | Where applicable |
| Reduced motion | Yes |
| Keyboard | Yes |

---

# 30. Performance UX

UX must protect Core Web Vitals.

Avoid:

- Layout shifts
- Blocking JavaScript
- Heavy animation
- Large icon libraries
- Unnecessary web fonts
- Global CSS
- Render-blocking feature assets

Visual stability is part of UX quality.

---

# 31. 4-Axis UX Audit

Every major feature may be evaluated on:

### Axis 1 — Diagnosis

- Ergonomics
- Visual noise
- Hierarchy
- Contrast
- Cognitive load
- Core Web Vitals

### Axis 2 — UX solution

Define:

- Desktop
- Tablet
- Mobile
- States
- Error paths
- Loading paths

### Axis 3 — UI specification

Define:

- Tokens
- Spacing
- Dimensions
- Typography
- Components
- WCAG requirements

### Axis 4 — Implementation

Map to:

- Native WordPress/WooCommerce hooks
- Blocks
- Components
- Scoped CSS
- Modular JS
- Progressive enhancement

---

# 32. Design Review Checklist

Before release:

- [ ] WCAG AA checked
- [ ] Contrast checked
- [ ] Keyboard navigation checked
- [ ] Focus states visible
- [ ] Mobile layout checked
- [ ] 48px targets checked
- [ ] Loading states checked
- [ ] Error states checked
- [ ] Reduced motion considered
- [ ] No horizontal overflow
- [ ] No accidental global CSS
- [ ] Tokens used consistently
- [ ] UX.md and UI_COMPONENTS.md aligned

---

# 33.1. Arquitetura Plugin-Driven & Tema Passivo Kardeu Canvas (App-Shell)

Para garantir máxima velocidade (Google PageSpeed 95-100), zero conflitos de CSS com temas pesados de terceiros e soberania visual absoluta do plugin, a suite adota o modelo **Plugin-Driven App-Shell**:
- **Tema Passivo `kardeu-canvas`**:
  - Exclusivamente estrutural e semântico.
  - Zero ficheiros CSS opinativos, zero scripts legados, zero dependências de frameworks de Customizer externos (ex: Kirki).
  - Executa apenas a declaração de suportes (`title-tag`, `woocommerce`, `align-wide`) e disponibiliza os pontos de ancoragem canónicos:
    - `kardeu_before_header` (Barra de Notificação / Portes Grátis)
    - `kardeu_header` (Cabeçalho Central: Branding, Navegação, Pesquisa, Conta, Carrinho)
    - `kardeu_after_header`
    - `kardeu_before_footer`
    - `kardeu_footer` (Rodapé Modular, Métodos de Pagamento, Copyright)
    - `kardeu_after_footer` (Cart Drawer e Modais de Conversão)
- **Soberania Visual do Plugin Kardeu WooCommerce**:
  - **Identidade e Tipografia**: Governadas pelo subplugin `global-settings` (Google Fonts locais sem CDN, paleta de cores, dimensões de botões e bordas de formulário).
  - **Cabeçalho e Rodapé**: Governados pelo subplugin `site-layout`.
  - **Catálogo, Grelha e PDP**: Governados pelo subplugin `single-product-grid`.
  - **Carrinho e Checkout**: Governados pelo subplugin `cart-checkout` e `checkout-canvas.php`.

---

# 33.2. Soberania de Layout por Página/Post e Motor Tailwind Standalone

Para permitir personalização visual sem quebrar o layout global e sem depender de construtores pesados, a suite disponibiliza controlo de layout a nível de cada página individual:

1. **Meta Box de Layout Individual (`Kardeu_Site_Layout_Metabox`)**:
   - **Largura do Contentor**:
     - *Padrão da Loja (1200px boxed)*: Alinhamento consistente com o cabeçalho e rodapé.
     - *Ecrã Total (100% Full-Width)*: Essencial para landing pages com secções coloridas e grelhas de ponta a ponta.
     - *Leitura Estreita (800px)*: Excelente para artigos de blog, manifestos ou termos de serviço, maximizando a legibilidade.
   - **Supressão de Elementos para Conversão Focada**:
     - *Ocultar Cabeçalho*: Remove menus para páginas de destino / landing pages isoladas.
     - *Ocultar Rodapé*: Remove distrações em funis de venda diretos.
     - *Ocultar Título da Página*: Permite que o criador de conteúdo use o seu próprio Hero estilizado sem duplicação de `<h1>`.
     - *Sem Espaçamento Vertical (Zero Padding)*: Elimina margens topo/fundo para que blocos com fundo toquem perfeitamente no cabeçalho ou rodapé.

2. **Grelha Editorial e Cartão de Artigo (Padrão Shopify Dawn)**:
   - Em `home.php` e arquivos de blog, os artigos são renderizados em `.kd-blog-grid` e `.kd-blog-card`:
     - Imagens em proporção consistente com zoom suave no hover (`scale(1.04)`).
     - Metadados discretos (categoria em caixa alta e data formatada).
     - Título com ligação permanente e botão explícito "Ler artigo completo →".
     - Alinhamento ergonómico e touch-targets generosos (mínimo 48px).

3. **Motor Tailwind CSS Standalone Local**:
   - Compilador embutido `tailwind.min.js` operando localmente no browser.
   - Zero dependências de APIs remotas de terceiros (Tailpress desativado).
   - Permite estilização imediata com classes utilitárias em blocos HTML nativos do WordPress e no editor Gutenberg, mantendo 100% da velocidade e conformidade com o PageSpeed.

---

# 33.3. Kardeu Theme Studio & Canvas Inline Editing UX Standards

Para fornecer uma experiência de edição visual ágil, moderna e sem fricção (estilo Shopify Theme Editor e Webflow), o **Kardeu Theme Studio** e o seu motor de canvas em direto seguem os seguintes padrões de UX:

1. **Navegação Segura e Interativa no Canvas**:
   - O utilizador **nunca** deve ser ejetado da moldura de pré-visualização ao clicar num link (`<a>`) ou botão nativo do site.
   - Cliques em links de navegação com submenus (ex: "Catálogo v") não navegam: expandem e recolhem o dropdown correspondente in-situ através da classe `.is-dropdown-open`, permitindo inspecionar e verificar a hierarquia de navegação sem perder o contexto do editor.
   - Cliques em elementos estruturais com `[data-kd-section-id]` abrem a gaveta de propriedades sem causar saltos de rolagem verticais bruscos (`scrollIntoView` desativado na seleção via clique).

2. **Edição Visual Direta no Canvas (Inline Text Editing)**:
   - **Descoberta Visual**: Todo o texto editável dentro de blocos HTML recebe feedback visual ao passar o rato: outline tracejado azul `rgba(0, 102, 204, 0.65)` com cursor `text` e ligeiro realce de fundo.
   - **Estado Ativo / Foco**: Ao receber foco, o elemento exibe contorno sólido de 2px em `#0066CC` com anel de foco `rgba(0, 102, 204, 0.15)`.
   - **Barra Flutuante de Formatação Rápida**:
     - Fundo escuro de alto contraste (`#0F172A`), tipografia branca (`#F8FAFC`), raio de 6px e elevação suave (`0 10px 25px -5px rgba(0,0,0,0.3)`).
     - Posicionada dinamicamente centrada acima do elemento editável (ou abaixo, caso o topo da viewport esteja próximo).
     - Controlos canónicos: Negrito, Itálico, Sublinhado, Seletor de Tamanho (12px a 64px com passos rápidos A- / A+), Alinhamento (Esquerda, Centro, Direita) e Seletor de Cores.
     - **Retenção de Seleção**: Clicar nos botões da barra flutuante intercepta `mousedown` com `e.preventDefault()`, impedindo o browser de desfazer a seleção de texto ativa enquanto o utilizador formata.

3. **Tratamento Ergonómico de Quebras de Linha (`Enter`)**:
   - Em títulos (`h1..h6`), botões e badges, pressionar a tecla `Enter` **não deve gerar tags `<div>` aninhadas**.
   - O motor intercepta a tecla e insere uma quebra de linha limpa (`<br>` via `document.execCommand('insertLineBreak')`), preservando a semântica do título e prevenindo a desestruturação do HTML ou bloqueios subsequentes de edição.
   - Títulos com múltiplas linhas ou quebras mantêm-se **incondicionalmente editáveis**, aceitando seleção, digitação e formatação em qualquer linha interna.

4. **Garantia Universal de Edição (Click-to-Edit)**:
   - Se por qualquer motivo um nó textual não tiver sido pré-processado (devido a marcações de terceiros ou injeções assíncronas), o clique direto do utilizador sobre o texto ativa o `contenteditable="true"` imediatamente, dá foco ao cursor na posição do clique e abre a barra de formatação.

5. **Substituição Visual de Imagens com 1 Clique**:
   - Imagens dentro de blocos HTML recebem um indicador flutuante ergonómico (`#kd-image-hover-badge`: "Substituir Imagem") ao passar o rato.
   - O clique abre a Biblioteca de Mídia oficial do WordPress (`wp.media`) com o botão de confirmação canónico. Ao selecionar uma nova imagem, o `src` é atualizado na moldura com uma transição suave de opacidade e o código é sincronizado automaticamente com a gaveta lateral.

6. **Campos do Editor e Scrollbars SaaS no Painel Lateral**:
   - Todos os inputs de texto e seletores respeitam a altura canónica de 40px e cantos de 6px (§25.1).
   - O campo de código `.kd-code-textarea` tem quebra de linha ativada (`white-space: pre-wrap !important; word-break: break-word !important; overflow-wrap: anywhere !important;`), eliminando texto cortado na margem direita.
   - As barras de rolagem do painel e gaveta são refinadas para 6px de largura com thumb suave `#CBD5E1`, eliminando barras nativas cinzentas grossas que comprimiam o conteúdo.

---

# 33.4. Padrões de UX para Cabeçalho da Loja & Ações de Conversão (Estilo TX RACE)

O cabeçalho principal da loja (`#kardeu-masthead`) é o elemento visual primário de orientação e autoridade do e-commerce. As suas diretrizes de experiência de utilizador seguem:

1. **Dimensões e Equilíbrio Visual**:
   - **Margem Superior (`header_margin_top`)**: Permite separar o cabeçalho do topo do ecrã ou da barra de avisos/portes grátis, evitando poluição visual.
   - **Preenchimentos Verticais (`header_padding_top` / `header_padding_bottom`)**: Garantem respiração visual aos elementos interiores sem aumentar desnecessariamente a área acima da dobra (above-the-fold).
   - **Altura Mínima Controlada (`header_height`)**: Escala consistente (64px, 72px, 80px, 88px) que preserva a legibilidade do logótipo e a facilidade de toque (touch-targets mínimos de 48px).

2. **Orientação Espacial com 3 Estados Cromáticos do Menu**:
   - Para que o utilizador compreenda instantaneamente o estado da navegação, o menu implementa **três estados visuais obrigatórios**:
     1. **Estado Normal (Repouso)**: Cor com contraste de conformidade WCAG AA (mínimo 4.5:1) contra a superfície do cabeçalho.
     2. **Estado Hover (Ao Passar o Rato)**: Transição suave de cor (150ms) indicando interatividade.
     3. **Estado Ativo (Página Atual)**: Cor destacada (`.current-menu-item`, `.current_page_item`, `.active`), informando inequivocamente em que secção ou categoria o cliente está a navegar.
   - **Tipografia e Espaçamento de Impacto (Estilo TX RACE)**:
     - Suporte a pesos arrojados de fonte (**700 Bold** e **800 Extra Bold**) e transformação em maiúsculas opcional.
     - Controlo de **distância entre palavras (`word-spacing`)** de -2px a +10px e **espaçamento entre itens (`gap`)** de 16px a 48px, permitindo adequar a densidade ao comprimento dos termos do menu.

3. **Ergonomia dos Gatilhos de Ação (Pesquisa antes do Carrinho)**:
   - Seguindo o fluxo de leitura ocidental e os padrões de alta conversão do e-commerce moderno, os gatilhos de ação à direita são estritamente ordenados:
     `[Minha Conta] -> [Pesquisa Rápida] -> [Carrinho de Compras]`
   - O gatilho de pesquisa rápida (`render_header_search_trigger`, prioridade 8) situa-se **imediatamente antes do carrinho** (prioridade 10). Ao clicar, expande uma janela de pesquisa ágil sem provocar navegações pesadas.

4. **Seletor de Carrinho & Visibilidade do Contador**:
   - Três modelos visuais claros:
     - **Carrinho Moderno (`modern_cart`)**: Wireframe minimalista com rodas e grelha com máxima modernidade (estilo TX RACE).
     - **Saco de Compras (`bag`)**: Silhueta sóbria e clássica.
     - **Personalizado SVG (`custom_svg`)**: Suporte a ícones de marca via Media Library ou código SVG direto.
   - **Badge do Contador de Artigos**: Pílula numérica de alto contraste posicionada no canto superior do ícone com fundo distintivo (`--kd-header-cart-badge-bg`), garantindo que o cliente visualiza imediatamente que tem produtos selecionados para compra.

5. **4º Arquétipo Fechado: Clássico / Menu à Direita (`classic_right`)**:
   - O alinhamento da navegação principal à direita (adjacente às ações) liberta amplitude visual ao centro da página e aproxima as opções de catálogo das ações de pesquisa, login e carrinho. É o padrão recomendado para lojas com menus compactos (3 a 5 itens) e estética moderna e minimalista.

6. **Visibilidade de Ícones Adaptada ao Dispositivo (PC / Tablet / Telemóvel)**:
   - Dispositivos móveis e tablets possuem largura de ecrã restrita. Permitir ligar/desligar a visibilidade de pesquisa e login independentemente por dispositivo (Computador, Tablet, Telemóvel) previne quebras de linha e sobreposições no cabeçalho sem forçar o lojista a desativar as funcionalidades no computador de secretária.

---

# 33.5. UX da Grelha em Colunas Heterogéneas no Theme Studio (`layout_grid`)

1. **Flexibilidade Visual Sem Quebra de Padrão**:
   - 6 presets pré-calculados garantem proporções harmoniosas (`100%`, `50/50`, `33/33/33`, `25/25/25/25`, `66/33`, `33/66`) sem risco de sobreposições ou quebras em ecrãs estreitos.
   - Redimensionamento contínuo por puxadores de arrasto no canvas (`.kd-grid-resizer-handle`) permite ajustes milimétricos com feedback visual imediato.

2. **Slots Modulares Universais**:
   - Cada coluna da grelha funciona como um contentor neutro capaz de receber qualquer tipo de conteúdo do catálogo (HTML/Tailwind, Banner, Vídeo, Produtos WooCommerce, Newsletter, etc.) mantendo o alinhamento de margens e paddings perfeitamente orquestrado.

---

# 33.6. Padrões de UX para Experiência Multi-Idioma & Localização Total (Frontend & Backend)

Para proporcionar uma experiência internacional de nível empresarial com zero fricção e zero poluição cognitiva, a arquitetura multi-idioma segue estes padrões estritos de UX:

1. **Princípio da "Localização Absoluta" (Zero Mistura Linguística)**:
   - Uma interface bilíngue ou mal traduzida destrói a confiança do comprador e a autoridade da marca.
   - Quando o idioma ativo é o **Inglês (`en_US`)**, absolutamente 100% dos elementos devem ser apresentados em inglês (menus, tooltips, modais de confirmação, etiquetas de IVA, alertas de VIES, gaveta do carrinho e passos de checkout).
   - Quando o idioma ativo é o **Português (`pt_PT`)**, 100% dos elementos devem ser apresentados em português nativo, claro e gramaticalmente impecável.

2. **Deteção Automática Inteligente com Desacoplamento Total**:
   - Por defeito, a opção **"Automático (Detetar idioma do WordPress)"** sincroniza a suite de forma transparente com as preferências de cada utilizador (`get_user_locale()`) e com o locale do site público (`determine_locale()`).
   - O administrador tem a liberdade de desacoplar o **Backend** e o **Frontend**: um gestor pode trabalhar no painel de controlo em Inglês enquanto a loja opera em Português para os clientes locais, ou vice-versa.

3. **UX do Painel de Idioma & Localização (Global Settings)**:
   - **Indicadores de Estado em Tempo Real (Pills)**: Cada secção de seleção exibe um crachá visual verde com o locale efetivamente ativo no momento (ex: `Ativo: 🇵🇹 Português`), eliminando qualquer ambiguidade sobre qual idioma está em vigor.
   - **Feedback do Locale do WordPress**: A opção "Automático" indica expressamente no próprio texto qual é a língua detetada pelo WordPress (ex: `⚡ Automático (Detetar idioma do WordPress) — Atual: 🇵🇹 Português`).
   - **Roadmap Visual de Expansão**: Exibição elegante em grelha com crachás dos próximos idiomas europeus (Espanhol, Francês, Alemão, Italiano) e documentação de filtros para desenvolvedores.

4. **Microcópia de Alta Conversão no Frontend**:
   - **Carrinho Flutuante (Cart Drawer)**: Microcópia focada no valor (`Portes Grátis`, `Finalizar Compra Segura`, `O seu carrinho está vazio`).
   - **Conformidade de IVA & VIES**: Alertas de autoliquidação B2B em linguagem clara, transmitindo segurança fiscal sem termos técnicos intimidantes para o comprador europeu.
   - **Diálogos Modais e Notificações**: Textos empáticos, diretos e com ações inequívocas nos botões (`Descartar e continuar`, `Sair e Guardar`, `Continuar a editar`).

---

# 34. Golden Rule

**Design for clarity.  
Build for accessibility.  
Optimize for conversion without deception.  
Keep every interaction predictable, fast and consistent.**

