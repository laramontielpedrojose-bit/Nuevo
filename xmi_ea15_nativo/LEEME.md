# Diagramas de Secuencia — XMI nativo de Enterprise Architect 15

Los 12 casos de uso del sistema (SPP) regenerados en el **formato nativo de EA
(XMI 1.1 / UML 1.3)**, con la misma estructura que la plantilla `algo sucede.xml`.
Este dialecto es el que importa de forma fiable en **Enterprise Architect 15**
(a diferencia del XMI 2.1 genérico).

## Archivo combinado
- **`SPP_Secuencias_TODOS.xmi`** — los **12 casos de uso en un solo archivo**,
  dentro de un paquete contenedor `SPP_Secuencias_TODOS` con un subpaquete y un
  diagrama por caso de uso. Importa todo de una vez (mismos criterios que los
  individuales). IDs y `ea_localid` son únicos globalmente.

## Archivos
| Archivo | Caso de uso |
|---------|-------------|
| CU-11_EliminarProyecto.xmi | Eliminar proyecto |
| CU-12_ActualizarProyecto.xmi | Actualizar proyecto |
| CU-14_RegistrarPracticante.xmi | Registrar practicante |
| CU-16_EvaluarReporte.xmi | Evaluar reporte |
| CU-17_SubirFormatosIniciales.xmi | Subir formatos iniciales |
| CU-18_SolicitarProyecto.xmi | Solicitar proyecto |
| CU-19_GenerarReporte.xmi | Generar reporte |
| CU-20_AnadirReporte.xmi | Añadir reporte |
| CU-21_GenerarAutoevaluacion.xmi | Generar autoevaluación |
| CU-22_AnadirAutoevaluacion.xmi | Añadir autoevaluación |
| CU-23_EvaluacionOrganizacionVinculada.xmi | Evaluación de organización vinculada |
| CU-25_GestionarActividades.xmi | Gestionar actividades |

## Criterios aplicados
- **Sin capa de Base de Datos (`BD`)**: el flujo llega solo hasta la capa
  **DAO / DTO**. Los mensajes hacia/desde `BD` (consultas SQL, `ResultSet`, etc.)
  se omitieron y los `seqno` se renumeraron de forma contigua.
- **Parámetros y valores de retorno**: el atributo `name` de cada mensaje lleva la
  **etiqueta completa con sus argumentos** (`showAlert("...", "...", WARNING)`,
  `deleteProject(idProject)`, `setMatricula(idTextField.getText())`, …), porque EA
  muestra en el diagrama el `name` del conector. La firma se replica en `mt` y los
  parámetros en `privatedata2` (`paramsDlg=...`). Las etiquetas son idénticas a las
  definidas en los `.puml` de `diagramas_secuencia/` (la fuente de los parámetros).
- **Mensajes**: llamadas `synchCall` → **Synch / Call** (flecha sólida);
  `reply` → **Return** (línea punteada `-->`).
- **Líneas de vida**: solo la **GUI** («boundary») y el **Controller** («control»)
  llevan icono de robustez. Los **DAO** y **DTO** (y Loader/Checker/Generator) son
  **objetos rectangulares** (sin estereotipo). El Actor es `uml:Actor`.
- **Creación de objetos**: los objetos creados con un mensaje «create»
  (`new Tipo()`) arrancan su línea de vida en el punto de creación (lifecycle
  **New**), no en la parte superior.
- **Fragmentos combinados** `alt` / `opt` / `loop` como `InteractionFragment`
  nativo, con sus guardas como particiones (operandos).

## Cómo importar en EA 15
1. Project Browser → clic derecho sobre el paquete destino.
2. **Import/Export → Import Package from XMI…** (`Ctrl+Alt+I`).
3. *XMI Type* = **XMI 1.1 (UML 1.3)** · marca **Import diagrams**.
4. Importar (un archivo por caso de uso).

## Reproducir
Generados con `tools/gen_ea_xmi.py` a partir de los XMI 2.1 de origen:
```
python3 tools/gen_ea_xmi.py CU-XX_origen.xmi CU-XX_salida.xmi
```
