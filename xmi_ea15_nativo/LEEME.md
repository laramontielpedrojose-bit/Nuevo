# Diagramas de Secuencia — XMI nativo de Enterprise Architect 15

Los 12 casos de uso del sistema (SPP) regenerados en el **formato nativo de EA
(XMI 1.1 / UML 1.3)**, con la misma estructura que la plantilla `algo sucede.xml`.
Este dialecto es el que importa de forma fiable en **Enterprise Architect 15**
(a diferencia del XMI 2.1 genérico).

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
- **Parámetros y valores de retorno respetados**: las etiquetas conservan firmas
  completas (`metodo(args) : Retorno`) y se reflejan en `privatedata2`
  (`retval=...;paramsDlg=...`).
- **Mensajes**: llamadas `synchCall` → **Synch / Call** (flecha sólida);
  `reply` → **Return** (línea punteada `-->`).
- **Estereotipos de robustez**: GUI «boundary», Controller/DAO/Loader/Checker/
  Generator «control», DTO «entity», Actor `uml:Actor`.
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
