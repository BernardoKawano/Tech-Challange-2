# DESIGN_SYSTEM

## Objetivo
Sistema visual do `web_viewer` para manter consistencia, legibilidade e sensacao premium.

## Tokens de Cor
- `--bg`: `#f5f7fb`
- `--surface`: `#ffffff`
- `--surface-soft`: `#f8fafc`
- `--text`: `#0f172a`
- `--muted`: `#475569`
- `--muted-2`: `#64748b`
- `--line`: `#e2e8f0`
- `--line-strong`: `#cbd5e1`
- `--brand`: `#0b5fff`
- `--brand-soft`: `#e8f0ff`
- `--warn-soft`: `#fff7ed`
- `--error-soft`: `#fef2f2`

## Tokens de Tipografia
- Hero title: `clamp(1.6rem, 2.6vw, 2.4rem)`, weight forte, letter-spacing negativo leve.
- Eyebrow: `0.75rem`, uppercase, 600.
- Body principal: `1rem`, line-height `1.5`.
- Labels KPI: `0.82rem`, 500.
- Valores KPI: `1.45rem`, 650.

## Tokens de Espacamento
- `--space-1`: `8px`
- `--space-2`: `12px`
- `--space-3`: `16px`
- `--space-4`: `24px`
- `--space-5`: `32px`

## Tokens de Radius
- `--radius-sm`: `10px`
- `--radius`: `14px`
- `--radius-lg`: `18px`

## Componentes Base
- Hero card
- KPI cards
- Status cards (`info`, `warning`, `error`)
- Chat bubbles (`user`, `assistant`)
- Tabs, inputs e button com foco visivel

## Regras
- Nao usar cores hardcoded fora de `theme.css`.
- Todo novo componente deve reutilizar tokens.
- Se houver novo estado visual, documentar aqui antes.
