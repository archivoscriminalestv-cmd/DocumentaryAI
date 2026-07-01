# Repository Structure Proposal — DocumentaryAI v1.0 (WP-0006)

> **Documento de diseño conceptual.** Propone cómo organizar físicamente el repositorio de DocumentaryAI para la versión 1.0.
> Es **independiente del lenguaje y de los frameworks**: no asume Python, TypeScript, Java ni ninguna tecnología.
> **No** define la arquitectura del dominio ni módulos funcionales; solo la **organización física** del repositorio.
> No mueve ni crea archivos: es una propuesta para que el Arquitecto la apruebe antes de cualquier reorganización.

---

# 1. Objetivo

Una buena organización del repositorio resuelve problemas que, de no atajarse pronto, escalan con el proyecto:

- **Descubribilidad:** cualquier persona (o asistente de IA) encuentra rápido dónde vive cada cosa.
- **Separación de preocupaciones física:** documentación, código, pruebas, configuración e infraestructura no se mezclan, reduciendo el acoplamiento accidental.
- **Escalabilidad estructural:** la estructura admite crecimiento (nuevos módulos, nuevas superficies) sin reorganizaciones traumáticas.
- **Onboarding y mantenimiento:** convenciones predecibles bajan el coste de entrada y el de mantenimiento a largo plazo.
- **Automatización fiable:** rutas estables y predecibles facilitan herramientas, validaciones y CI futuros.
- **Independencia tecnológica:** una organización conceptual evita que decisiones de framework contaminen la raíz del proyecto.

Este documento define **dónde va cada cosa**, no **cómo se programa** ni **cómo se diseña el sistema**.

---

# 2. Principios de organización

Criterios usados para estructurar el repositorio (criterios de **organización**, no de arquitectura del sistema):

1. **Separación de responsabilidades.** Cada carpeta de primer nivel tiene un propósito único y claramente distinto del resto.
2. **Modularidad.** El código se organiza en unidades cohesivas y reemplazables; la estructura permite añadir o quitar módulos sin afectar a los demás.
3. **Escalabilidad.** La jerarquía crece "a lo ancho" (más módulos/superficies) sin necesidad de reestructurar lo existente.
4. **Independencia tecnológica.** Los nombres y la jerarquía son conceptuales; no presuponen lenguaje, framework ni gestor de paquetes concreto.
5. **Mantenibilidad y legibilidad.** Convenciones uniformes y predecibles; una raíz limpia con pocas entradas de primer nivel.
6. **Separación núcleo / detalles externos.** La organización refleja la frontera entre lo propio del proyecto y lo que depende del mundo exterior (infraestructura, herramientas), sin definir aquí la arquitectura interna del núcleo.
7. **Lo generado no se versiona junto a lo fuente.** Artefactos, cachés y salidas tienen su lugar (o se ignoran), separados del código fuente.

---

# 3. Propuesta de estructura

Estructura conceptual de primer nivel. Los nombres son **genéricos** y orientativos; el Arquitecto puede ajustarlos. **No se inventan módulos de negocio**: donde aparece `<module>` es un marcador de posición.

```
documentaryai/
├── docs/                  # Documentación del proyecto
│   ├── architecture/      #   Documentación de arquitectura (RFC, ADR, ARCH, SPEC, estándares, índices)
│   └── ...                #   Otra documentación (gobierno, guías)
│
├── src/                   # Código fuente del producto
│   ├── core/              #   Núcleo del sistema (centro del diseño) — estructura interna fuera de alcance de este WP
│   ├── <module>/          #   Módulos del producto (nombres genéricos; sin definir aquí)
│   └── interfaces/        #   Superficies de entrada/salida (CLI, API, web...) — conceptual
│
├── tests/                 # Pruebas (separadas del código fuente)
│   ├── unit/              #   Pruebas unitarias
│   ├── integration/       #   Pruebas de integración
│   └── e2e/               #   Pruebas de extremo a extremo
│
├── tools/                 # Herramientas internas de desarrollo (utilidades del repositorio)
│
├── scripts/               # Scripts de automatización puntual (tareas operativas)
│
├── config/                # Configuración del proyecto (parámetros, perfiles por entorno)
│
├── infra/                 # Infraestructura como descripción (despliegue, contenedores, entornos)
│
├── automation/            # Automatización del ciclo de vida (pipelines/CI, hooks, flujos repetibles)
│
├── examples/              # Ejemplos de uso y muestras ejecutables/ilustrativas
│
├── assets/                # Recursos estáticos (imágenes, plantillas, datos de muestra no sensibles)
│
└── (archivos raíz)        # Metadatos del repositorio (README, licencia, ignore, manifiestos)
```

Distinción explícita pedida por el WP:

| Concepto | Ubicación propuesta |
|---|---|
| Documentación | `docs/` |
| Código fuente | `src/` |
| Pruebas | `tests/` |
| Herramientas | `tools/` |
| Configuración | `config/` |
| Infraestructura | `infra/` |
| Automatización | `automation/` (pipelines/CI) y `scripts/` (tareas puntuales) |
| Ejemplos | `examples/` |
| Recursos | `assets/` |

> Nota: separo **`automation/`** (procesos repetibles del ciclo de vida, p. ej. pipelines) de **`scripts/`** (tareas operativas puntuales). El Arquitecto puede fusionarlas si prefiere una sola.

---

# 4. Responsabilidad de cada carpeta

- **`docs/`** — Toda la documentación. `docs/architecture/` concentra la documentación de arquitectura y sus estándares; el resto, guías y gobierno.
- **`src/`** — El código fuente del producto. `src/core/` es el centro del diseño (su organización interna se decidirá en su propio WP, fuera de alcance aquí). `src/interfaces/` agrupa las superficies de interacción. `src/<module>/` son módulos del producto con nombres aún no definidos.
- **`tests/`** — Todas las pruebas, separadas del código fuente y organizadas por tipo (unitarias, integración, e2e). La estructura interna puede reflejar la de `src/`.
- **`tools/`** — Utilidades internas para trabajar con el repositorio (p. ej. la futura herramienta de validación documental), no parte del producto entregable.
- **`scripts/`** — Scripts de automatización puntual y tareas operativas (preparación de entorno, mantenimiento). Acciones, no lógica de producto.
- **`config/`** — Configuración del proyecto: parámetros y perfiles por entorno. Sin lógica de negocio.
- **`infra/`** — Descripción de la infraestructura (despliegue, contenedores, definición de entornos). Separa "cómo se ejecuta" de "qué es" el producto.
- **`automation/`** — Definición del ciclo de vida automatizado: pipelines/CI, hooks y flujos repetibles.
- **`examples/`** — Ejemplos de uso y muestras que ilustran cómo se utiliza el producto, sin formar parte de él.
- **`assets/`** — Recursos estáticos (imágenes, plantillas, datos de muestra). Nada sensible ni secreto.
- **Archivos raíz** — Metadatos mínimos del repositorio (README, licencia, archivo de exclusiones, manifiestos del ecosistema). La raíz se mantiene limpia.

---

# 5. Reglas de organización

Reglas **de organización del repositorio** (no reglas de programación):

1. **Nuevos módulos del producto → dentro de `src/`**, como una unidad cohesiva propia. No se crean módulos de producto fuera de `src/`.
2. **Documentación → siempre en `docs/`**; la de arquitectura, en `docs/architecture/`. Ningún documento oficial vive fuera de `docs/`.
3. **Herramientas internas → en `tools/`**; **tareas/scripts puntuales → en `scripts/`**; **pipelines y flujos del ciclo de vida → en `automation/`**. No mezclar utilidades de desarrollo con código de producto.
4. **Pruebas → en `tests/`**, nunca entremezcladas con el código fuente; se clasifican por tipo.
5. **Configuración → en `config/`**; los **secretos no se versionan** (se gestionan por entorno y se excluyen del control de versiones).
6. **Infraestructura → en `infra/`**, separada del código de producto.
7. **Recursos estáticos → en `assets/`**; **ejemplos → en `examples/`**; no se colocan en `src/`.
8. **La raíz se mantiene mínima:** solo metadatos del repositorio; cualquier otra cosa pertenece a una carpeta de primer nivel.
9. **Lo generado no se versiona** junto a lo fuente (artefactos, cachés, salidas) y se excluye explícitamente.
10. **Nombres consistentes y predecibles** en todo el árbol, para que las rutas sean estables y automatizables.

---

# 6. Riesgos

Posibles problemas futuros de organización a vigilar:

- **Sobre-estructuración prematura:** crear todas las carpetas antes de necesitarlas contradice el principio de evolución progresiva del proyecto; conviene introducir cada carpeta cuando aporte valor real.
- **Divergencia entre estructura propuesta y estado actual:** hoy el repositorio usa una disposición distinta (código en la raíz, sin `src/`); adoptar esta propuesta implicaría una reorganización que debe planificarse como WP propio y con cuidado del historial de Git.
- **Ambigüedad `scripts/` vs `automation/` vs `tools/`:** sin una regla clara, las utilidades pueden acabar dispersas; la propuesta las delimita, pero requiere disciplina (o fusión deliberada).
- **Acoplamiento accidental por mala ubicación:** colocar pruebas, recursos o configuración dentro de `src/` erosiona la separación de responsabilidades con el tiempo.
- **Crecimiento desordenado de `docs/`:** sin índice y convención de nombres (ya señalado en auditorías previas), `docs/` puede volverse difícil de navegar.
- **Secretos versionados por error:** sin reglas y exclusiones claras en `config/`, riesgo de filtrar credenciales.
- **Nombres genéricos sin gobierno:** los marcadores `<module>` deben sustituirse con una convención acordada para evitar inconsistencias.
- **Coste de migración:** cuanto más tarde se adopte una estructura objetivo, mayor es el coste y el riesgo de moverla.

---

_Fin de la propuesta. Documento conceptual y de organización física; no implementa funcionalidades, no define la arquitectura del dominio ni asume tecnologías, y no modifica el repositorio._
