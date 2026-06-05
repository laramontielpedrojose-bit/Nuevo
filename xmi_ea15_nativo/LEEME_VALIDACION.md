# Validación CU-11 — XMI nativo de Enterprise Architect 15

Este archivo (`CU-11_EliminarProyecto.xmi`) es el **diagrama de secuencia CU-11
(Eliminar Proyecto)** regenerado en el **formato nativo de EA (XMI 1.1 / UML 1.3)**,
idéntico en estructura a tu plantilla `algo sucede.xml`.

> Es una **prueba de validación**: si este importa bien en tu EA 15, genero los
> 11 casos de uso restantes con el mismo molde.

## Cómo importar
1. Project Browser → clic derecho sobre el paquete destino.
2. **Import/Export → Import Package from XMI…** (`Ctrl+Alt+I`).
3. *XMI Type* = **XMI 1.1 (UML 1.3)** · marca **Import diagrams**.
4. Importar.

## Qué contiene / qué revisar
- **5 líneas de vida**: Coordinador (Actor), :GUIManageProject «boundary»,
  :ManageProjectController «control», :ProjectDAO «control», BD «entity».
- **35 mensajes**: 21 llamadas **Synch** (flecha sólida) y 14 **Return**
  (línea punteada `-->`).
- **3 fragmentos combinados anidados**: `alt` (selectedItem==null / proyecto
  seleccionado) → `opt` (response==OK) → `alt` (eliminado / ReferentialIntegrity
  / Service / ValidationException).

## Por favor confírmame
1. ¿Importó **sin errores**?
2. ¿Las líneas de vida salen **separadas** (no encimadas)?
3. ¿Los retornos se ven **punteados**?
4. ¿Las cajas `alt` / `opt` muestran el **operador correcto**?
   - Codifiqué el operador en `ea_ntype` (alt=0, opt=1, loop=2). Si EA muestra un
     operador equivocado, dime cuál sale y ajusto el mapeo antes de generar el resto.

Una vez confirmes, genero: CU-12, CU-14, CU-16, CU-17, CU-18, CU-19, CU-20,
CU-21, CU-22, CU-23, CU-25 + un archivo combinado.
