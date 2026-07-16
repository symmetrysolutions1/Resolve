# Integración de Resolve con un root de Symmetry

## Decisión

Resolve permanece como repositorio y operación independiente:

- checkout local: C:\Users\INICIO\Resolve
- repositorio remoto: symmetrysolutions1/Resolve
- Symmetry no incorpora el código de Resolve como una carpeta versionada

Esta separación no impide que Resolve tenga un root empresarial. El repositorio
de software y el root on-chain cumplen funciones distintas.

## Tres fronteras

### Symmetry

Symmetry conserva la Factory, facets compartidos, herramientas de despliegue,
pipelines de evidencia, indexadores, monitoreo y soporte de upgrades.

### Repositorio Resolve

Resolve conserva el colector, puntuador, playbook, datos operativos permitidos,
integraciones con plataformas y métricas de tickets.

### Root empresarial de Resolve

Si Resolve se opera como empresa o unidad soberana, recibe un root desplegado
por EnterpriseRootFactory. Allí viven:

- identidad empresarial
- propietarios y permisos
- evidencia y auditoría
- entitlements de servicios
- referencias de configuración e integraciones
- gobernanza y upgrades autorizados

El root no debe almacenar credenciales de Upwork, PayPal, wallets privadas,
tokens de GitHub ni datos que deban permanecer secretos.

## Estado actual

La fase actual es validación de mercado. No se despliega un root automáticamente
porque todavía faltan decisiones empresariales y operativas:

1. Identidad legal que será propietaria de Resolve.
2. companyKey canónico.
3. Red y chain id.
4. Wallet de propietario y multisigs de gobernanza.
5. Servicios de Symmetry que se instalarán.
6. Política de evidencia y retención.
7. Artefacto de onboarding y responsables operativos.

Cuando esas decisiones estén listas, Symmetry puede provisionar el root sin
mover este repositorio dentro del monorepo.

## E14 no cambia esta regla

Una carpeta puede estar físicamente dentro del directorio local de Symmetry y
seguir excluida de su Git. Esa conveniencia de workspace no equivale a que la
empresa viva dentro del protocolo o del repositorio.

Para Resolve preferimos la frontera visible desde el inicio: repo separado,
historial separado, CI separado y, si corresponde, root empresarial separado.
