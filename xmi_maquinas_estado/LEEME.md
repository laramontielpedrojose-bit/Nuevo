# Máquinas de Estado (StateDiagram) — XMI nativo de EA 15

Máquinas de estado de los 6 casos de uso, en formato nativo de EA
(`diagramType="StateDiagram"`, igual que la plantilla `state.xml`):
`ActivityModel` con transiciones y estados (`SimpleState`, `PseudoState`
initial/final), elemento `StateMachine` y el diagrama con su geometría.

## Archivos y modelo
| Archivo | CU | Estados modelados |
|---------|----|-------------------|
| CU-03_InactivarCoordinador.xmi | Inactivar Coordinador | Activo → Por confirmar → Inactivando → Inactivo / Error |
| CU-06_ConsultarOrganizacionVinculada.xmi | Consultar Org. Vinculada | Cargando → Lista mostrada / Sin registros / Error |
| CU-07_RegistrarTecnicoResponsable.xmi | Registrar Téc. Responsable | Capturando → Validando → Guardando → Registrado |
| CU-08_ConsultarTecnicoResponsable.xmi | Consultar Téc. Responsable | Cargando → Lista mostrada / Sin registros / Error |
| CU-13_InactivarPracticante.xmi | Inactivar Practicante | Activo → Por confirmar → Inactivando → Inactivo / Error |
| CU-15_ConsultarProfesor.xmi | Consultar Profesor | Cargando → Lista mostrada / Error |

## Criterios
- Cada **transición** lleva su `trigger [guard] / effect` (p.ej.
  `inactivateCoordinator [coordinador seleccionado] / showAlertAndWait(...)`),
  con los métodos/guardas reales del flujo (rama jbh-developer).
- Estado **inicial** (●) y **final** (◉) como `PseudoState`.
- Sin capa BD; el modelo refleja el proceso del CU (pantalla/entidad).

## Importar en EA 15
Project Browser → clic derecho en el paquete → **Import/Export →
Import Package from XMI…** (`Ctrl+Alt+I`) → *XMI Type* = **XMI 1.1**, marca
**Import diagrams**.

> La posición de los estados es automática (por capas); reacomódalos en EA a tu gusto.
