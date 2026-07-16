# Resolve

Resolve es el sistema operativo de Symmetry para encontrar, evaluar y ejecutar
tickets pequeños y medianos con una meta mínima de USD 15 por hora esperada.

El rango inicial es USD 30 a USD 300. El sistema no confunde premio publicado
con ingreso probable: descuenta comisiones, riesgo de pago, competencia y horas
totales de entrega.

## Qué funciona hoy

- Recolección en vivo de issues públicos de GitHub que mencionan bounties o recompensas.
- Importación de candidatos JSON y CSV de Upwork, Algora, TaskBounty, OnlyDust,
  Superteam Earn y otras fuentes.
- Extracción de recompensa y detección aproximada de tecnologías.
- Puntuación por valor esperado por hora.
- Puertas GO, REVIEW y SKIP.
- Regla fast track para tickets de al menos USD 100 en máximo 2 horas, siempre
  que no exista competencia visible y el preflight esté completo.
- Reportes JSON, CSV y Markdown.
- Modo demo sin red y pruebas automatizadas sin dependencias externas.

No se automatiza el scraping autenticado de plataformas que no ofrecen una API
pública estable. Esas oportunidades entran mediante JSON o CSV hasta construir
un conector oficial o autorizado. Esta decisión evita cuentas bloqueadas y
recolectores que dejan de funcionar ante cualquier cambio visual.

## Inicio rápido

Requiere Python 3.11 o superior.

    python -m resolve_scout doctor
    python -m unittest discover -s tests -v
    python -m resolve_scout demo

El demo produce:

- data/runs/demo/ranked.json
- data/runs/demo/ranked.csv
- data/runs/demo/shortlist.md

También puede ejecutarse con Docker:

    docker build -t symmetry-resolve .
    docker run --rm symmetry-resolve doctor
    docker run --rm symmetry-resolve demo

## Recolección en vivo

GitHub permite una cuota mayor cuando se define GITHUB_TOKEN.

PowerShell:

    $env:GITHUB_TOKEN = (gh auth token)
    python -m resolve_scout collect --source github --pages 1 --per-page 50
    Remove-Item Env:GITHUB_TOKEN

Una consulta personalizada:

    python -m resolve_scout collect --source github --query "is:issue is:open label:bounty python"

Todo candidato recolectado automáticamente queda en REVIEW hasta hacer el
preflight manual. Nunca debe iniciarse trabajo solo porque el score sea alto.

## Importar oportunidades de otras plataformas

Crear un archivo JSON con una lista bajo candidates o usar directamente una
lista. Ejemplo mínimo:

    {
      "candidates": [
        {
          "id": "upwork:123",
          "title": "Automatizar reporte CSV",
          "url": "https://www.upwork.com/...",
          "platform": "upwork",
          "reward_usd": 100,
          "estimated_hours": 2,
          "contract_type": "contracted",
          "competition_count": 0,
          "funded": true,
          "preflight_complete": true,
          "scope_clarity": 0.9,
          "skills": ["python", "automation", "csv"]
        }
      ]
    }

Ejecutar:

    python -m resolve_scout score --input candidatos.json --output data/runs/manual

El CSV usa los mismos nombres de campo. Skills se separa con comas.

## Cómo decide

La métrica central es:

    expected_hourly =
      net_reward * acceptance_probability * payment_probability
      / estimated_total_hours

El resultado es SKIP cuando ocurre al menos una de estas condiciones:

- Recompensa fuera de USD 30 a USD 300.
- Valor esperado inferior a USD 15 por hora.
- Alcance insuficientemente claro.
- Esfuerzo superior al tope permitido por premio.
- Ticket cerrado o asignado a otra persona.
- PR competidor activo en una carrera abierta.
- Contrato sin milestone o fondos confirmados.

El resultado es REVIEW cuando pasa los filtros económicos, pero todavía falta
confirmar estado, claim, competencia, alcance o mecanismo de pago.

El resultado es GO únicamente cuando pasa todos los filtros y el preflight está
marcado como completo.

Los umbrales son editables en config/scoring.toml y el mapa de capacidades está
en config/skills.toml.

## Topes operativos iniciales

| Recompensa | Esfuerzo máximo |
|---:|---:|
| Hasta USD 50 | 2 horas |
| Hasta USD 100 | 5 horas |
| Hasta USD 250 | 14 horas |
| Hasta USD 300 | 17 horas |

El deadline puede ser de 24 horas, pero no significa trabajar 24 horas. El
margen restante se reserva para instalación, pruebas, revisión y correcciones.

## Dónde crear perfiles

Crear primero:

1. GitHub — https://github.com/
2. Upwork — https://www.upwork.com/
3. Algora — https://algora.io/
4. TaskBounty — https://www.task-bounty.com/
5. OnlyDust — https://onlydust.com/
6. Superteam Earn — https://superteam.fun/earn/

Segunda ola:

7. Contra — https://contra.com/
8. Fiverr — https://www.fiverr.com/
9. Freelancer — https://www.freelancer.com/
10. PeoplePerHour — https://www.peopleperhour.com/

Exploración selectiva:

11. IssueHunt — https://oss.issuehunt.io/
12. Opire — https://opire.dev/

Seguridad y Web3, después de construir un historial especializado:

13. Immunefi — https://immunefi.com/
14. Code4rena — https://code4rena.com/
15. Sherlock — https://audits.sherlock.xyz/
16. Cantina — https://cantina.xyz/

No conviene abrir y mantener dieciséis perfiles el primer día. El orden de
operación recomendado está en docs/OPERATING_PLAYBOOK.md.

## Mercado objetivo

La mayor oferta bruta suele estar en WordPress, WooCommerce y PHP. El segmento
con mejor encaje y margen para Symmetry es automatización e integraciones:
Python o JavaScript, APIs, webhooks, n8n, hojas de cálculo, PDF, email y scraping.

El orden inicial de caza es:

1. Automatización e integraciones.
2. Python para datos, scripts, APIs y scraping.
3. WordPress, WooCommerce y PHP.
4. Shopify y Liquid.
5. QA, Playwright, pruebas, CI y despliegues.
6. React, Next.js y TypeScript.
7. Solidity y Web3 cuando el pago y las reglas sean verificables.

## Documentación operativa

Ver docs/OPERATING_PLAYBOOK.md para el proceso diario, reglas de competencia,
preflight y métricas de rentabilidad.

La separación entre este repositorio y un futuro root empresarial de Resolve se
documenta en docs/SYMMETRY_ROOT_INTEGRATION.md.
