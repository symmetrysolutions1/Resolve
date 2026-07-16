# Playbook operativo de Resolve

## Objetivo

Convertir oportunidades públicas o contratadas en ingresos cobrados, sin gastar
horas en carreras con baja probabilidad de pago.

La unidad de trabajo no es el ticket encontrado. Es el ticket pagado.

## Tipos de oportunidad

| Modalidad | Competencia | Cuándo se trabaja |
|---|---|---|
| Contrato o milestone | Antes de la contratación | Solo después de asignación y fondos |
| Bounty con claim | Antes de la asignación | Solo después de recibir el claim |
| Open race | Durante la implementación | Solo con ventaja clara y sin PR serio activo |
| Contest | Todos entregan | Solo si el valor esperado supera el mínimo |

En Upwork la competencia principal ocurre antes de ser contratado. Una vez
contratados, se trabaja contra un alcance y un milestone financiado.

En Algora y otros bounties de GitHub puede haber varios implementadores; el pago
suele depender de que nuestra solución sea la aceptada o la primera elegible.

En TaskBounty pueden existir varias soluciones que pasan las pruebas y el
creador selecciona. El premio publicado no equivale a ingreso garantizado.

En Superteam hay dos superficies distintas: Bounties son competitivos; Projects
selecciona primero al freelancer y luego se ejecuta el trabajo.

## Preflight obligatorio

Antes de cambiar preflight_complete a true:

1. Confirmar que el ticket y el repositorio siguen abiertos y activos.
2. Confirmar recompensa, moneda, comisión y método de pago.
3. Identificar si es contrato, claim, carrera abierta o concurso.
4. Revisar asignados, comentarios, forks y PRs relacionados.
5. Reproducir el problema o validar que el alcance es ejecutable.
6. Escribir criterios de aceptación concretos.
7. Estimar horas totales: lectura, setup, código, pruebas, PR y revisión.
8. Confirmar que el valor esperado sigue por encima de USD 15 por hora.
9. En contratos, comprobar que el milestone aparece financiado.
10. Guardar la evidencia y marcar el candidato como verificado.

Si no podemos responder cualquiera de estos puntos, el ticket permanece en
REVIEW o pasa a SKIP.

## Reglas de ejecución

- USD 30 en una hora es posible para documentación, configuración, CSS o fixes
  muy acotados. El tope interno total es dos horas.
- USD 100 en dos horas entra en fast track únicamente sin competencia visible,
  o cuando ya está asignado y financiado.
- USD 250 permite hasta 14 horas de esfuerzo.
- USD 300 permite hasta 17 horas de esfuerzo.
- Un deadline de 24 horas incluye margen para revisión; no autoriza 24 horas de
  trabajo si la economía deja de cumplir.
- Si aparece un PR competidor serio durante una open race, se reevalúa antes de
  continuar.
- No comenzar por una promesa en comentarios cuando la plataforma exige claim,
  contrato o milestone.

## Ciclo diario

### 1. Recolectar

Ejecutar el colector GitHub y agregar manualmente oportunidades de plataformas
con login.

    python -m resolve_scout collect --source github
    python -m resolve_scout score --input candidatos.json --output data/runs/manual

### 2. Revisar

Abrir primero GO y luego REVIEW por priority_score. Hacer preflight sobre un
máximo de cinco candidatos para no convertir la búsqueda en trabajo no pagado.

### 3. Reclamar o aplicar

Solicitar claim o contrato antes de implementar cuando la plataforma lo permita.
En Upwork, definir un milestone pequeño, verificable y financiado.

### 4. Ejecutar

Crear rama, reproducir, implementar la mínima solución completa, agregar pruebas
y preparar evidencia. Registrar tiempo real desde la primera lectura.

### 5. Entregar

Seguir exactamente el mecanismo de la plataforma. Un PR abierto no reemplaza el
botón de entrega, claim o Submit Work cuando la plataforma lo exige.

### 6. Cobrar y aprender

Registrar monto neto, tiempo total, días al pago y causa de cualquier rechazo.
Actualizar probabilidades de config/scoring.toml con datos propios.

## Métricas semanales

- Candidatos recolectados.
- Candidatos con preflight.
- Aplicaciones y claims.
- Tickets asignados.
- Tickets entregados.
- Tickets aceptados.
- Ingreso bruto y neto.
- Horas totales, incluidas búsqueda y propuestas.
- USD netos por hora total.
- Tiempo promedio hasta pago.
- Tasa de victoria por plataforma y modalidad.

La métrica principal es ingreso neto dividido por todas las horas de operación,
no solo las horas de programación.

## Activación de perfiles

Semana operativa inicial, sin esperar cuatro semanas:

1. GitHub: README de perfil, bio de Symmetry y repositorios destacados.
2. Upwork: perfil amplio enfocado en automatización, integraciones y fixes.
3. Algora: conectar GitHub y revisar reglas de cada bounty.
4. TaskBounty: conectar GitHub y validar porcentaje neto antes de trabajar.
5. OnlyDust: conectar GitHub y completar tecnologías.
6. Superteam Earn: crear perfil y priorizar Projects sobre Bounties al inicio.

Después de conseguir las primeras entregas pagadas, abrir Contra, Fiverr,
Freelancer y PeoplePerHour. IssueHunt y Opire solo se usan cuando el ticket y el
mantenedor pasan el preflight de actividad.

Immunefi, Code4rena, Sherlock y Cantina requieren una línea separada de
especialización en seguridad. No se tratan como tickets rápidos generales.
