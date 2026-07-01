# DocumentaryAI – Development Guide

## Propósito

Este documento define las normas de desarrollo de DocumentaryAI.

Todo cambio realizado por un asistente de IA (Claude Code u otro) debe respetar estas reglas.

El objetivo no es solo generar código funcional, sino construir una plataforma mantenible, escalable y comprensible durante muchos años.

---

# Filosofía del proyecto

DocumentaryAI no es un experimento.

Es una plataforma profesional para investigar casos criminales reales mediante inteligencia artificial.

El código debe priorizar:

1. Claridad.
2. Simplicidad.
3. Mantenibilidad.
4. Escalabilidad.

Nunca se añadirá complejidad si no aporta un beneficio real.

---

# Roles

## Arquitecto

La arquitectura del proyecto la define ChatGPT.

Claude Code nunca debe modificar la arquitectura por iniciativa propia.

Si detecta una mejora arquitectónica, debe proponerla antes de implementarla.

---

## Claude Code

Claude Code actúa como desarrollador.

Su responsabilidad es:

* implementar funcionalidades,
* refactorizar,
* escribir tests,
* corregir errores,
* documentar el código,
* mantener la calidad del proyecto.

No debe rediseñar el proyecto sin autorización.

---

# Principios generales

## Priorizar simplicidad

Siempre elegir la solución más sencilla que permita crecer posteriormente.

Evitar sobreingeniería.

---

## Evolución progresiva

No introducir arquitecturas complejas antes de necesitarlas.

Cada módulo debe aparecer cuando el proyecto lo requiera.

---

## Una responsabilidad por módulo

Cada archivo debe tener un propósito claro.

Evitar archivos enormes.

---

## Código legible

El código debe poder entenderse meses después sin esfuerzo.

La legibilidad es prioritaria frente a la concisión.

---

# Organización del proyecto

La arquitectura será modular.

El núcleo del sistema vivirá en `core/`.

La interfaz de usuario (CLI, web, API...) nunca contendrá lógica de negocio.

La lógica de negocio nunca dependerá de la interfaz.

---

# Dominio

El dominio representa el conocimiento del proyecto.

Ejemplos futuros:

* Case
* Document
* Timeline
* Event
* Person
* Location
* Hypothesis
* Contradiction
* Script

El dominio no debe imprimir por consola.

El dominio no debe depender de modelos de IA concretos.

---

# Inteligencia Artificial

Los proveedores de IA deberán poder intercambiarse.

Nunca acoplar el proyecto a un único proveedor.

Claude será el proveedor inicial, pero la arquitectura deberá permitir incorporar otros modelos sin modificar el núcleo.

---

# Calidad del código

Todo código nuevo debe:

* seguir PEP 8;
* incluir type hints cuando sea razonable;
* utilizar nombres descriptivos;
* evitar duplicación;
* eliminar código muerto;
* mantener funciones cortas y claras.

---

# Refactorización

Claude puede refactorizar únicamente cuando:

* simplifique el código;
* elimine duplicación;
* mejore la claridad;
* no cambie el comportamiento existente.

---

# Dependencias

Antes de añadir una nueva librería:

* comprobar si realmente es necesaria;
* preferir la biblioteca estándar de Python cuando sea suficiente;
* justificar dependencias importantes.

---

# Git

Cada cambio debe ser pequeño y coherente.

Los commits deben representar una única mejora.

---

# Antes de finalizar una tarea

Claude debe comprobar:

* que el proyecto sigue ejecutándose;
* que no ha roto funcionalidades existentes;
* que no quedan imports sin usar;
* que no quedan archivos temporales;
* que el código mantiene el estilo del proyecto.

---

# Comunicación

Al finalizar cada tarea, Claude debe entregar un resumen con:

1. Qué ha cambiado.
2. Qué archivos ha modificado.
3. Por qué se ha hecho.
4. Riesgos detectados.
5. Próximos pasos recomendados.

---

# Regla principal

La prioridad absoluta es construir una plataforma sólida para investigación documental.

Toda decisión técnica debe contribuir a ese objetivo.

Si existe una duda entre una solución más sofisticada y otra más clara, se elegirá la más clara.
