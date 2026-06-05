# XMI para Enterprise Architect (variante con extensión EA)

Usa **esta** carpeta (`xmi_ea/`), no `../xmi/`, si quieres que EA:
- muestre las **GUI como «boundary»** y los **Controller como «control»** (íconos
  de robustez), y
- **separe las lifelines** (ya no se sobreponen) gracias a la geometría incluida.

## Diferencia con `../xmi/`
`../xmi/` es UML 2.1 puro (solo modelo, sin estereotipos ni layout). Esta carpeta
añade la **extensión nativa de EA** (`<xmi:Extension extender="Enterprise Architect">`)
con clasificadores estereotipados, conectores y un diagrama con coordenadas.

## Archivos
- `SPP_Secuencias_TODOS.xmi` — los 12 casos de uso de una vez.
- `CU-XX_*.xmi` — uno por caso de uso.

## Mapeo de estereotipos (robustez)
| Línea de vida | Tipo / estereotipo |
|---------------|--------------------|
| Actor (Coordinador, Profesor, Practicante) | `uml:Actor` |
| `:GUI…` (vista FXML) | Class «**boundary**» |
| `…Controller` | Class «**control**» |
| `…DAO`, `…Loader`, `…Checker`, `…Generator` | Class «**control**» |
| DTO (`x : Tipo`) y `BD` | Class «**entity**» |

> Si prefieres que los **DAO** sean «entity» (o cualquier otro ajuste del mapeo),
> avísame y lo regenero.

## Importar
1. Project Browser → paquete destino.
2. Clic derecho → **Import/Export → Import Package from XMI…** (`Ctrl+Alt+I`).
3. *XMI Type* = **XMI 2.1**, marca *Import diagrams*.

Las lifelines quedan a 200 px una de otra (Left = 40, 240, 440, …). Si quieres más
o menos separación, dímelo y cambio el paso.
