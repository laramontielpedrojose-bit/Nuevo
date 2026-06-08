# Diagramas de Comunicación (Collaboration) — XMI nativo de EA 15

Diagramas de comunicación de 6 casos de uso, en formato nativo de EA
(`diagramType="CollaborationDiagram"`, igual que la plantilla `comunicacion.xml`).
El flujo de mensajes se extrajo del **código real** del repositorio
`owsy12/SistemaParaPracticasProfesionales` (rama **jbh-developer**).

## Archivos
| Archivo | Caso de uso | Controlador (origen) |
|---------|-------------|----------------------|
| CU-03_InactivarCoordinador.xmi | Inactivar Coordinador | DeactivateCoordinatorController |
| CU-06_ConsultarOrganizacionVinculada.xmi | Consultar Organización Vinculada | ManageLinkedOrganizationController |
| CU-07_RegistrarTecnicoResponsable.xmi | Registrar Técnico Responsable | AddTechnicalResponsibleController |
| CU-08_ConsultarTecnicoResponsable.xmi | Consultar Técnico Responsable | ManageTechnicalResponsibleController |
| CU-13_InactivarPracticante.xmi | Inactivar Practicante | DeactivateInterController |
| CU-15_ConsultarProfesor.xmi | Consultar Profesor | DeactivateProfessorController |

## Criterios
- **Objetos** (ClassifierRole `ea_stype=Object`): Actor, GUI, Controller, DAO(s) y DTO(s),
  con los **nombres reales** de las clases del código.
- **Enlaces** (`AssociationRole`) entre los objetos que se comunican.
- **Mensajes** con **numeración anidada** (1, 1.1, 1.1.1, …) según la pila de llamadas,
  y la firma real del método con parámetros y retorno (`OpParams=1` para mostrarlos).
- **Sin capa BD**: el flujo llega hasta DAO/DTO (consistente con los diagramas de secuencia).
- Las **guardas** de los flujos alternativos van en el texto del mensaje, p.ej.
  `[selectedUser == null] showAlert(...)`.

## Importar en EA 15
Project Browser → clic derecho en el paquete destino → **Import/Export →
Import Package from XMI…** (`Ctrl+Alt+I`) → *XMI Type* = **XMI 1.1**, marca
**Import diagrams**.

## Notas
- El **actor** se asignó según la función (Administrador para CU-03/CU-07,
  Coordinador para CU-06/08/13/15). Si tu modelo lo asigna distinto, es un cambio
  de una línea por diagrama.
- La posición 2D de los objetos es automática; reacomódalos en EA a tu gusto.
