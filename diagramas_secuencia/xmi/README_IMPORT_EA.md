# Importar a Enterprise Architect (XMI 2.1)

Archivos generados a partir de los `.puml` (UML 2 / XMI 2.1):

- `SPP_Secuencias_TODOS.xmi` — un solo modelo con las 12 interacciones (importación de una vez).
- `CU-XX_*.xmi` — un archivo por caso de uso (importación individual).

Cada archivo contiene, por caso de uso:
- una `uml:Collaboration` con una `uml:Interaction`,
- las **lifelines** (Actor, IU, Controller, DAO, BD),
- los **mensajes** (`messageSort` = `synchCall`, `reply` o `createMessage`),
- los **fragmentos combinados** `alt` / `opt` / `loop` con sus guardas.

## Pasos en Enterprise Architect

1. En el **Project Browser**, selecciona el paquete destino (o crea uno, p. ej. "Diagramas de Secuencia").
2. Clic derecho → **Import/Export → Import Package from XMI...** (atajo `Ctrl+Alt+I`).
3. En *File*, elige el `.xmi`. En *XMI Type* selecciona **XMI 2.1**.
4. Marca *Import diagrams* y *Strip GUIDs* (recomendado si reimportas).
5. Aceptar.

## Notas / limitaciones

- Se importa el **modelo** de cada interacción (lifelines, mensajes ordenados y
  fragmentos). Según la versión de EA, el **diagrama** se crea automáticamente o
  puede requerir: abrir la Interaction → clic derecho → *Create Diagram → Sequence*,
  o arrastrar la Interaction al lienzo; EA reconstruye el orden a partir de los
  `MessageOccurrenceSpecification`.
- El XMI es UML 2.1 estándar (sin extensión propietaria de EA), por eso la
  **geometría/posición** exacta no viaja; EA aplica su auto-layout de secuencia.
- Si tu versión de EA no dibuja el diagrama al importar, dime la versión y genero
  la variante con la extensión `<xmi:Extension extender="Enterprise Architect">`
  (incluye el layout del diagrama).
