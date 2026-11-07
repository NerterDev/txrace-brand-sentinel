# UI COMPONENTS — CANONICAL COMPONENT IMPLEMENTATION STANDARD

**Version:** 1.1  
**Status:** Production Master Standard

---

# 1. Purpose

`UI_COMPONENTS.md` is the canonical bridge between:

- `UX.md` — what the component must look and feel like
- `rules.md` — how the software must be engineered
- `QA.md` — how correctness is verified

A reusable component should have one canonical implementation rather than multiple slightly different versions.

---

# 2. Component Contract

Every reusable component must define:

```text
Name
Purpose
Contexts
HTML structure
Variants
States
Design tokens
Accessibility
JavaScript behavior
PHP integration
WooCommerce compatibility
Responsive behavior
Test requirements
```

---

# 3. Naming

Use stable, product-owned prefixes.

Example:

```text
ao-button
ao-card
ao-field
ao-modal
ao-switch
ao-spinner
ao-notice
ao-tabs
ao-badge
ao-table
kd-blog-grid
kd-blog-card
```

Avoid generic classes such as:

```text
.button
.card
.modal
.container
```

---

# 4. Component Ownership

Each component owns:

- Markup
- Component CSS
- Component JS
- Accessibility behavior
- Variants
- State handling

Components must not unexpectedly mutate unrelated UI.

---

# 5. Button

## API

```text
variant:
- primary
- secondary
- tertiary
- danger
- ghost

state:
- idle
- loading
- success
- disabled
```

## Requirements

From UX.md:

- Minimum 48px touch target
- Product CTA: 52px desktop / 56px mobile
- Checkout CTA: 50–54px desktop / 56px mobile
- Visible focus
- Loading state
- No duplicate activation

Example:

```html
<button class="ao-button ao-button--primary">
  Finalizar compra
</button>
```

Loading:

```html
<button
  class="ao-button is-loading"
  aria-busy="true"
  disabled>
  <span class="ao-button__spinner" aria-hidden="true"></span>
  Finalizar compra
</button>
```

---

# 6. Input

Requirements:

- 48–50px height
- 16px minimum mobile font
- Explicit label
- Description where needed
- Error association

Example:

```html
<label class="ao-field">
  <span class="ao-field__label">Email</span>
  <input
    class="ao-field__input"
    type="email"
    autocomplete="email"
    aria-describedby="email-help">
  <span id="email-help" class="ao-field__help">
    Usaremos este email para confirmar a encomenda.
  </span>
</label>
```

---

# 7. Error Field

Required behavior:

- Error visually apparent
- Error not communicated only through color
- Error message associated with field
- Focus moved appropriately when necessary
- Existing input preserved

Example:

```html
<input
  aria-invalid="true"
  aria-describedby="email-error">

<p id="email-error" role="alert">
  Introduza um endereço de email válido.
</p>
```

---

# 8. Switch

Use native button semantics where appropriate:

```html
<button
  type="button"
  role="switch"
  aria-checked="false">
  <span class="ao-switch__track">
    <span class="ao-switch__thumb"></span>
  </span>
  <span class="ao-switch__label">Ativar funcionalidade</span>
</button>
```

Requirements:

- Keyboard accessible
- State announced
- 48px touch area
- No color-only state

---

# 9. Spinner

Canonical:

```text
14–16px
CSS animation
~0.65s
currentColor
```

Must not cause layout shift.

Respect reduced-motion preferences.

---

# 10. Card

Card:

```text
Background: surface token
Border: border token
Radius: 8px admin / UX-defined storefront radius
Padding: 16/24/32px according to hierarchy
```

Cards should communicate one coherent information group.

Avoid excessive nesting.

---

# 11. Notice / Alert

Variants:

```text
info
success
warning
error
```

Requirements:

- Semantic meaning
- Icon optional
- Text remains understandable without icon
- Adequate contrast
- Dismissal only when safe
- Errors use `role="alert"` where appropriate

---

# 12. Modal

Use only when the task genuinely requires interruption.

Requirements:

- Focus trap
- Escape support where appropriate
- Initial focus
- Return focus to trigger
- Accessible name
- No background interaction while modal is active
- Mobile-friendly layout

Do not use modals for information that can be shown inline more efficiently.

---

# 13. Tabs

Requirements:

- Correct tab semantics where true tabs are used
- Keyboard navigation
- Active state
- Focus state
- URL/deep-link behavior where useful

Do not use tabs merely as decorative navigation.

---

# 14. Admin UI Components (Padrão Canónico EU VAT & VIES)

Todas as interfaces de administração devem implementar estritamente os componentes canónicos definidos pelo módulo EU VAT & VIES:

### 14.1 Admin Header (`.kardeu-header`)
- **Marcação**:
  ```html
  <header class="kardeu-header">
      <div class="kardeu-brand">
          <div class="kardeu-logo-badge">
              <!-- SVG Icon 22x22 stroke -->
          </div>
          <div>
              <span class="kardeu-title">Kardeu WooCommerce</span>
              <p class="kardeu-subtitle">Nome do Submenu — Descrição funcional clara</p>
          </div>
      </div>
      <div class="kardeu-header-actions">
          <span class="kardeu-pill kardeu-pill-success">
              <span class="kardeu-pill-dot"></span>
              Módulo Ativo
          </span>
          <span class="kardeu-version-tag">v1.0.0</span>
          <!-- Botão opcional de ação primária com spinner -->
      </div>
  </header>
  ```

### 14.2 Admin Tabs Navigation (`.kardeu-nav-tabs`)
- **Marcação**:
  ```html
  <nav class="kardeu-nav-tabs" role="tablist">
      <a href="?page=kardeu-...&tab=..." class="kardeu-tab-link is-active" role="tab">
          <!-- SVG stroke icon 18x18 -->
          <span>Nome da Aba</span>
      </a>
  </nav>
  ```
- **Regra**: Barra inferior com `border-bottom: 2px solid #E2E8F0`. O item ativo possui `color: #0066CC` e `border-bottom: 3px solid #0066CC; margin-bottom: -2px;`. Proibido formato em bloco / botão.

### 14.3 Admin Cards & Section Headers (`.kardeu-card`)
- **Marcação**:
  ```html
  <div class="kardeu-card">
      <div class="kardeu-card-header">
          <h2 class="kardeu-card-title">Título do Bloco</h2>
          <p class="kardeu-card-desc">Instrução contextual sobre o grupo de opções.</p>
      </div>
      <!-- Conteúdo do Formulário -->
      <div class="kardeu-card-footer">
          <button type="submit" class="kardeu-btn kardeu-btn-primary">
              Guardar Alterações
          </button>
      </div>
  </div>
  ```

### 14.4 Form Fields & Switches (`.kardeu-form-row` & `.kardeu-switch-row`)
- **Inputs & Selects Canónicos (Padrão Cart Checkout)**:
  ```html
  <div class="kardeu-form-row">
      <label class="kardeu-label" for="field_id">Rótulo do Campo</label>
      <input type="text" id="field_id" class="kardeu-input" placeholder="Ex: Contact Information" />
      <p class="kardeu-hint">Texto de apoio explicativo.</p>
  </div>
  ```
- **Regras CSS dos Campos**:
  ```css
  /* Inputs de Formulário e Selects Unificados */
  .kardeu-admin-wrap input[type="text"],
  .kardeu-admin-wrap input[type="search"],
  .kardeu-admin-wrap input[type="url"],
  .kardeu-admin-wrap input[type="email"],
  .kardeu-admin-wrap input[type="password"],
  .kardeu-admin-wrap input[type="number"],
  .kardeu-admin-wrap .regular-text,
  .kardeu-admin-wrap .kardeu-input,
  .kardeu-card input[type="text"],
  .kardeu-card .regular-text {
      height: 40px;
      padding: 0 12px;
      background: #FFFFFF;
      border: 1px solid var(--kardeu-input-border, #CBD5E1);
      border-radius: 6px;
      font-size: 14px;
      color: var(--kardeu-text, #0F172A);
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      box-sizing: border-box;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }

  .kardeu-admin-wrap input:hover,
  .kardeu-card input:hover {
      border-color: var(--kardeu-input-border-hover, #94A3B8);
  }

  .kardeu-admin-wrap input:focus,
  .kardeu-card input:focus {
      border-color: var(--kardeu-primary, #0066CC);
      box-shadow: 0 0 0 3px var(--kardeu-primary-light, #EFF6FF);
      outline: none;
  }

  /* Selects com Chevron Integrado */
  .kardeu-admin-wrap select,
  .kardeu-card select,
  .kardeu-select {
      height: 40px !important;
      min-height: 40px !important;
      line-height: 38px !important;
      padding: 0 38px 0 12px !important;
      background-color: #FFFFFF !important;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") !important;
      background-repeat: no-repeat !important;
      background-position: right 12px center !important;
      background-size: 16px 16px !important;
      border: 1px solid var(--kardeu-input-border, #CBD5E1) !important;
      border-radius: 6px !important;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
      -webkit-appearance: none !important;
      appearance: none !important;
      cursor: pointer !important;
  }
  ```
- **Switch Toggles**:
  ```html
  <div class="kardeu-switch-row">
      <div class="kardeu-switch-info">
          <label class="kardeu-label" for="toggle_id">Ativar Funcionalidade</label>
          <p class="kardeu-hint">Explicação dos efeitos da ativação.</p>
      </div>
      <label class="kardeu-switch">
          <input type="checkbox" id="toggle_id" name="settings[key]" value="1" />
          <span class="kardeu-slider"></span>
      </label>
  </div>
  ```

### 14.5 Botões, Barra de Salvamento Flutuante e Spinner Universal (`.kardeu-btn`, `.kardeu-card-footer` & `.kardeu-spinner`)
- **Padrão Estrito do Botão**:
  - Altura: 40px, Raio: 6px, Padding: `0 20px` (ou `10px 24px` na barra flutuante).
  - **SEM ÍCONES ESTÁTICOS**: Proibido adicionar dashicons ou SVGs decorativos dentro de botões de submissão em repouso. O botão apresenta apenas o texto de ação.
- **Barra de Salvamento Flutuante / Sticky Save Bar (`.kardeu-card-footer`)**:
  - Em todas as abas e subplugins do Kardeu WooCommerce, o rodapé de submissão do formulário é **flutuante e fixo no fundo do ecrã** (`position: fixed; bottom: 0;`), permitindo ao utilizador guardar alterações a qualquer momento sem necessidade de rolar a página para cima ou para baixo.
  - Alinhamento do viewport WordPress: `left: 160px; right: 0;` (com menu WP aberto), adaptando-se automaticamente a `left: 36px;` quando `body.folded` ou em ecrãs `<= 960px`, e a `left: 0;` em telemóveis/tablets (`<= 782px`).
  - Efeito visual SaaS Premium: fundo `rgba(255, 255, 255, 0.95)` com `backdrop-filter: blur(12px)`, sombra suave superior (`box-shadow: 0 -4px 20px rgba(15, 23, 42, 0.08)`), e borda superior discreta.
  - **Padding de Segurança Obrigatório**: O contentor principal `.kardeu-admin-wrap` deve sempre ter `padding-bottom: 90px !important;` para garantir que nenhum campo ou texto no final do formulário fica tapado pela barra flutuante.
- **Marcação Canónica do Rodapé Flutuante**:
  ```html
  <div class="kardeu-card-footer">
      <button type="submit" class="kardeu-btn kardeu-btn-primary" id="kardeu-save-btn">
          <?php esc_html_e('Guardar Alterações', 'kardeu-woocommerce'); ?>
      </button>
  </div>
  ```
- **Spinner CSS Canónico 15px**:
  ```css
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
  ```
- **Ciclo de Submissão Universal (Vanilla JS)**:
  Ao clicar/submeter qualquer formulário no admin, a rotina `setButtonLoading(btn)` deve:
  1. Travar a largura do botão (`btn.style.minWidth = Math.ceil(rect.width) + 'px'`).
  2. Adicionar `.is-loading` e `aria-busy="true"`.
  3. Injetar `<span class="kardeu-spinner" aria-hidden="true"></span> <span>A guardar...</span>`.
  4. Prevenir duplo envio (`dataset.kardeuSubmitting = 'true'`).

### 14.6 Info Banner & Key Badges (`.kardeu-field-info-banner`)
- Card de destaque azul claro (`#EFF6FF`) com borda `#BFDBFE`, raio 8px, ícone circular SVG e tags `<code class="kardeu-key-code">` em mono cinzento/azul.

---

# 15. Product Card

Must support:

- Image
- Title
- Price
- Rating where available
- Availability where relevant
- Primary action

Grid:

```text
Mobile: 2 columns
Desktop: 4 columns
```

Content must not create uncontrolled height differences.

---

# 16. Trust Block

Must support:

- Payment trust
- Delivery
- Returns
- Warranty
- Availability

Claims must be factually supported.

No fake urgency.

---

# 17. Empty State

Every meaningful collection should define:

```text
Title
Explanation
Primary next action
Optional secondary action
```

Avoid dead ends.

---

# 18. Loading / Skeleton

Skeletons should be used only where they improve perceived continuity.

Do not create fake skeleton complexity for operations that complete almost instantly.

Never allow skeletons to hide failures indefinitely.

---

# 19. Component CSS Rules

All component CSS must:

- Be scoped
- Use tokens
- Avoid global selectors
- Avoid unnecessary specificity
- Avoid `!important`
- Support responsive behavior

Example:

```css
.ao-scope .ao-button {
  min-height: 48px;
  padding-inline: 20px;
}
```

---

# 20. Component JS Rules

JS must:

- Be progressively enhanced
- Avoid duplicate initialization
- Clean up listeners where necessary
- Respect keyboard interaction
- Respect reduced motion
- Avoid global variables
- Avoid unnecessary DOM polling

---

# 21. PHP Integration

PHP should render semantic markup and data.

Avoid:

- Large inline scripts
- Large inline styles
- Business logic inside templates
- Unsafe HTML construction

Escape according to output context.

---

# 22. WooCommerce Integration

Components used in WooCommerce must be tested in:

- Product page
- Product loop
- Cart
- Classic checkout
- Blocks checkout where applicable
- My Account where applicable

Do not assume all contexts expose identical hooks or DOM.

---

# 23. Component Registry

Each production component should appear in a registry:

| Component | Status | Contexts | Accessibility | Tests |
|---|---|---|---|---|
| Button | Stable | Store/Admin | AA | Required |
| Field | Stable | Store/Admin | AA | Required |
| Switch | Stable | Admin | AA | Required |
| Notice | Stable | Store/Admin | AA | Required |
| Spinner | Stable | Store/Admin | AA | Required |
| Modal | Stable | Admin/Store | AA | Required |
| Tabs | Stable | Admin | AA | Required |
| Product Card | Stable | Store | AA | Required |
| Blog Grid / Card | Stable | Store (Blog / Archives) | AA | Required |
| Site Layout Metabox | Stable | Admin (Pages / Posts) | AA | Required |
| Standalone Tailwind Engine | Stable | Store / Admin (Gutenberg) | N/A | Required |
| Inline Editable Node | Stable | Studio Preview Canvas | AA | Required |
| Inline Formatting Toolbar | Stable | Studio Preview Canvas | AA | Required |
| Image Replace Badge | Stable | Studio Preview Canvas | AA | Required |
| Studio Code Textarea | Stable | Studio Admin Drawer | AA | Required |
| Header Navigation & Triggers | Stable | Storefront App-Shell | AA | Required |
| Layout Grid Container | Stable | Studio Preview / Storefront | AA | Required |

---

# 24. Storefront & Editorial Components

### 24.1 Article Card & Blog Grid (`.kd-blog-grid` & `.kd-blog-card`)
- **Inspiração:** Shopify Dawn Editorial Article Card.
- **Contexto:** `home.php`, `archive.php`, `index.php` do tema `kardeu-canvas`.
- **Estrutura Semântica**:
  ```html
  <div class="kd-blog-grid">
      <article class="kd-blog-card">
          <a href="<?php the_permalink(); ?>" class="kd-blog-card__image-link">
              <img src="..." alt="..." class="kd-blog-card__image" loading="lazy" />
          </a>
          <div class="kd-blog-card__content">
              <div class="kd-blog-card__meta">
                  <span class="kd-blog-card__category">Categoria</span>
                  <time class="kd-blog-card__date">13 Setembro, 2026</time>
              </div>
              <h2 class="kd-blog-card__title">
                  <a href="<?php the_permalink(); ?>">Título com Hiperligação Estável</a>
              </h2>
              <div class="kd-blog-card__excerpt">Excerto editorial conciso...</div>
              <a href="<?php the_permalink(); ?>" class="kd-blog-card__read-more">
                  Ler artigo completo →
              </a>
          </div>
      </article>
  </div>
  ```
- **Responsividade**: Grelha fluida CSS Grid: 1 coluna em mobile (<768px), 2 colunas em tablet, 3 colunas em desktop (minmax 320px).

### 24.2 Page Layout Controller (`Kardeu_Site_Layout_Metabox`)
- **Ficheiro:** `subplugins/site-layout/includes/class-site-layout-metabox.php`
- **Contexto:** Painel lateral de edição nativa de Páginas (`page`) e Artigos (`post`).
- **Controlos Granulares Suportados**:
  - `_kardeu_layout_container`: `default` (1200px boxed), `full` (100% full-width), `narrow` (800px leitura).
  - `_kardeu_hide_header`: `1` ou `0` (Oculta cabeçalho para landing pages / funis).
  - `_kardeu_hide_footer`: `1` ou `0` (Oculta rodapé para páginas de conversão focada).
  - `_kardeu_hide_title`: `1` ou `0` (Oculta `h1.entry-title` para páginas com Hero customizado).
  - `_kardeu_no_padding`: `1` ou `0` (Remove paddings verticais para blocos ponta a ponta).

### 24.3 Standalone Local Tailwind Engine
- **Ficheiro:** `subplugins/site-layout/assets/js/tailwind.min.js` (407 KB, standalone JIT).
- **Enfileiramento:** Registado no subplugin `site-layout` via `wp_enqueue_script` no frontend e `enqueue_block_editor_assets` no admin.
- **Isolamento e Segurança:** Zero chamadas a APIs remotas (eliminando dependência do Tailpress e falhas de rede), compilação local no browser, total compatibilidade com blocos HTML e CSS utilitário.

### 24.4 Kardeu Theme Studio & Canvas Visual Components
- **Contexto:** `preview-listener.js`, `theme-studio.js`, `site-layout.css`, `theme-studio.css`.
- **Componentes**:
  1. **Nó Editável Inline (`.kd-inline-editable`)**:
     - Atributos: `contenteditable="true"`, `spellcheck="false"`.
     - Hover: `outline: 1px dashed rgba(0, 102, 204, 0.65) !important; background-color: rgba(0, 102, 204, 0.05) !important; cursor: text !important;`.
     - Foco: `outline: 2px solid #0066cc !important; background-color: rgba(0, 102, 204, 0.08) !important; box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.15) !important;`.
     - Comportamento de Enter: Insere `<br>` sem criar `<div>`s internas.
  2. **Barra Flutuante de Formatação (`.kd-inline-toolbar`)**:
     - Estilo: Fundo `#0F172A`, texto `#F8FAFC`, borda `1px solid rgba(255,255,255,0.15)`, sombra suave de 25px.
     - Elementos: Botões `.kd-tb-btn` (Bold, Italic, Underline), seletor de tamanho `.kd-tb-dropdown-wrap`, botões de incremento/decremento `A-` / `A+`, alinhamento (esquerda, centro, direita) e paleta de cores.
     - Retenção: `mousedown` interceptado com `preventDefault` para não colapsar a seleção de texto.
  3. **Badge Flutuante de Imagem (`#kd-image-hover-badge`)**:
     - Estilo: Pílula flutuante azul escuro `#0F172A` com ícone de câmara SVG e texto "Substituir Imagem".
     - Gatilho: `mouseenter` em qualquer `img` dentro de `.kd-html-section-body`.
     - Ação: Invoca modal `wp.media` e atualiza o atributo `src` na tela e no código JSON.
  4. **Área de Código Responsiva (`.kd-code-textarea`)**:
     - Estilo: Altura canónica de 420px, fonte monospace (`ui-monospace`, `monospace`), borda `#CBD5E1`.
     - Quebra de Linha: `white-space: pre-wrap !important; word-break: break-word !important; overflow-wrap: anywhere !important;` (anti-corte de texto).
  5. **Caixa Informativa de Edição Visual (`.kd-visual-edit-tip`)**:
     - Estilo: Fundo suave `#F0F9FF`, borda `1px solid #BAE6FD`, ícone de lápis SVG em azul `#0284C7`, texto ergonómico explicativo para o utilizador.

### 24.5 Cabeçalho Canónico & Gatilhos de Ação (Estilo TX RACE)
- **Ficheiros:** `class-site-layout-config.php`, `class-site-layout-frontend.php`, `site-layout.css`, `tab-header.php`, `admin.css`.
- **4 Presets de Cabeçalho (Body Classes Canónicas):**
  1. `kd-header-preset-classic`: Clássico E-Commerce (logo esquerda, nav centro, ações direita).
  2. `kd-header-preset-classic_right`: Clássico Menu à Direita (logo esquerda, nav alinhada à direita junto às ações, ações no extremo direito).
  3. `kd-header-preset-centered`: Centrado / Elegante (nav esquerda, logo imponente ao centro, ações direita).
  4. `kd-header-preset-minimal`: Minimalista / Drawer (logo esquerda, hambúrguer gaveta lateral, ações direita).
- **Estrutura Semântica**:
  ```html
  <header id="kardeu-masthead" class="site-header">
      <div class="kd-header-inner kd-container">
          <!-- Logótipo -->
          <div class="kd-site-branding">...</div>
          <!-- Navegação Principal -->
          <nav class="kd-site-navigation">
              <ul class="kd-nav-menu-list">
                  <li class="menu-item"><a href="...">Início</a></li>
                  <li class="menu-item current-menu-item"><a href="...">Catálogo</a></li>
                  <li class="menu-item"><a href="...">Contacto</a></li>
              </ul>
          </nav>
          <!-- Ações Ordenadas (kardeu_header_actions) -->
          <div class="kd-header-actions">
              <!-- Prioridade 5: Conta (com classes condicionais .kd-hide-desktop, .kd-hide-tablet, .kd-hide-mobile) -->
              <div class="kd-header-account-wrapper kd-hide-tablet">
                  <a href="..." class="kd-header-account-link" aria-label="A Minha Conta">...</a>
              </div>
              <!-- Prioridade 8: Pesquisa Rápida (com classes condicionais de visibilidade) -->
              <div class="kd-header-search-wrapper kd-hide-mobile">
                  <button type="button" class="kd-header-search-trigger" aria-label="Pesquisar">
                      <svg class="kd-search-icon">...</svg>
                  </button>
                  <div class="kd-header-search-dropdown">...</div>
              </div>
              <!-- Prioridade 10: Carrinho de Compras -->
              <div class="kd-header-cart-wrapper">
                  <a href="<?php echo esc_url(wc_get_cart_url()); ?>" class="kd-header-cart-trigger">
                      <span class="kd-cart-icon-wrap">
                          <!-- SVG: modern_cart | bag | custom_svg -->
                      </span>
                      <span class="kd-header-cart-count">0</span>
                  </a>
              </div>
          </div>
      </div>
  </header>
  ```
- **Visibilidade Responsiva Granular por Dispositivo:**
  - `.kd-hide-desktop`: `@media (min-width: 993px) { display: none !important; }`
  - `.kd-hide-tablet`: `@media (min-width: 769px) and (max-width: 992px) { display: none !important; }`
  - `.kd-hide-mobile`: `@media (max-width: 768px) { display: none !important; }`
  - **Componente Admin**: Grupo de seleção tátil `.kardeu-device-visibility-group` com rótulos `.kardeu-device-checkbox-label` estilizados como badges interativos com hover e foco claros.
- **Tokens CSS Canónicos do Cabeçalho (`:root`)**:
  ```css
  :root {
      /* Dimensões e Espaçamento */
      --kd-header-margin-top: 0px;
      --kd-header-padding-top: 0px;
      --kd-header-padding-bottom: 0px;
      --kd-header-height: 72px;

      /* Tipografia do Menu */
      --kd-header-font-size: 15px;
      --kd-header-font-weight: 700;
      --kd-header-menu-word-spacing: 0px;
      --kd-header-menu-gap: 24px;
      --kd-header-menu-margin-left: 32px;
      --kd-header-menu-margin-right: 32px;

      /* 3 Estados de Cores da Navegação */
      --kd-header-menu-color: #0F172A;
      --kd-header-menu-hover: #0066CC;
      --kd-header-menu-active: #0066CC;

      /* Gatilhos de Ação */
      --kd-header-search-icon-size: 20px;
      --kd-header-search-icon-color: #0F172A;
      --kd-header-cart-icon-size: 22px;
      --kd-header-cart-icon-color: #0F172A;
      --kd-header-cart-badge-bg: #16A34A;
      --kd-header-cart-badge-color: #FFFFFF;
  }
  ```

### 24.6 Grelha de Layout em Colunas Heterogéneas (`layout_grid`)
- **Ficheiros:** `theme-studio.js`, `preview-listener.js`, `tab-sections.php`, `site-layout.css`.
- **Estrutura**:
  ```html
  <section class="kd-section kd-section--layout-grid kd-container">
      <div class="kd-layout-grid-container" style="--kd-grid-cols: 2; --kd-gap-x: 24px; --kd-gap-y: 24px;">
          <div class="kd-layout-grid-col" style="flex: 0 0 66%;">
              <!-- Slot Modular 1: Ex: Imagem/Banner -->
          </div>
          <div class="kd-layout-grid-col" style="flex: 0 0 33%;">
              <!-- Slot Modular 2: Ex: Grelha de Produtos / CTA -->
          </div>
      </div>
  </section>
  ```
- **Presets de Proporção Suportados**:
  - `[ 100% ]`: 1 coluna largura total.
  - `[ 50% | 50% ]`: 2 colunas simétricas.
  - `[ 33% | 33% | 33% ]`: 3 colunas simétricas.
  - `[ 25% | 25% | 25% | 25% ]`: 4 colunas simétricas.
  - `[ 66% | 33% ]`: Coluna de destaque ampla + barra lateral.
  - `[ 33% | 66% ]`: Barra lateral + coluna de destaque ampla.
- **Interatividade no Canvas**:
  - Puxador de redimensionamento (`.kd-grid-resizer-handle`) com drag contínuo horizontal.
  - Sincronização direta com a chave `columns_ratio` e re-renderização em tempo real sem saltos de tela.

---

# 25. Golden Rule

**One component, one contract, one canonical implementation, many safe contexts.**
