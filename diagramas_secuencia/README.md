# Diagramas de secuencia (CU-11 en adelante)

Diagramas de secuencia UML por capas
**Usuario → IU (vista GUI) → Controller → DAO → Base de Datos**,
derivados del código del proyecto y siguiendo la notación de *UML @ Classroom*
(mensajes síncronos con respuesta punteada, fragmentos `alt`/`opt`/`loop`,
barras de activación).

La interacción se modela explícitamente: el **usuario** actúa sobre la **IU**
(la vista FXML, representada como `boundary`), la IU delega en el **controlador**,
éste invoca los **DAO** y los DAO ejecutan las sentencias sobre la **BD**; las
respuestas y mensajes (alertas) regresan controlador → IU → usuario.

## Convenciones de notación

- **Métodos y parámetros reales:** los mensajes usan los nombres y argumentos
  tal como aparecen en el código (p. ej. `saveIntern(intern)`,
  `updateStatus(reportId, statusUpdate)`, `concludeActiveByIntern(internId, grade)`).
- **Guardas reales:** las condiciones de los fragmentos `alt`/`opt` reflejan la
  validación del controlador (`[hasEmptyFields()]`, `[selectedReport == null]`, etc.).
- **Despliegue de mensajes:** los errores y avisos se modelan con la llamada real
  `showAlert("Título", "mensaje", TIPO)` (o `showStatus(...)` / `showError(...)`),
  enviada del controlador a la IU, que es la capa que muestra el diálogo al usuario.
  `showAlert` es `GUI.Utils.Alert.showAlert(String, String, Alert.AlertType)`;
  `TIPO` abrevia `Alert.AlertType` (`WARNING`, `ERROR`, `INFORMATION`, `CONFIRMATION`).
- **Recuperar y mostrar:** las consultas incluyen el paso `mapToXxx(resultSet) : List<DTO>`
  (el `mapXxx(ResultSet)` del estándar) y el retorno hacia la IU que carga la
  tabla/combo y muestra los datos.
- **Creación de DTO:** en los CU de registrar/crear se grafica `new Dto()`, los
  setters con sus valores reales y el paso del DTO como parámetro al DAO, que luego
  lee sus getters para armar el `INSERT`.

## Cómo regenerar las imágenes

```bash
# Requiere java; plantuml.jar se descarga del release oficial.
java -jar plantuml.jar -tpng -o png docs/diagramas_secuencia/CU-*.puml
# Equivalente en SVG:
java -jar plantuml.jar -tsvg -o svg docs/diagramas_secuencia/CU-*.puml
```

`_comun.puml` contiene el estilo compartido y se incluye con `!include _comun.puml`.

## Mapeo Caso de Uso ↔ Código

Solo se incluyen los CU de la lista del proyecto que corresponden a CU-11 en
adelante del documento. Los diagramas fuera de esa lista se movieron a
`no_en_lista/`.

| CU | Nombre (lista del proyecto) | IU (vista FXML) | Controller | DAO(s) principales |
|----|-----------------------------|-----------------|-----------|--------------------|
| CU-11 | Eliminar Proyecto | GUIManageProject | ManageProjectController | ProjectDAO |
| CU-12 | Actualizar Proyecto | GUIUpdateProject | UpdateProjectController | ProjectDAO |
| CU-14 | Registrar Estudiante | GUIAddIntern | AddInternController | InternDAO |
| CU-16 | Evaluar Reporte Mensual | GUIEvaluateReport | EvaluateReportController | ReportEvaluationDAO, ReportDAO, PracticeDAO |
| CU-17 | Subir Formatos Iniciales | GUIUploadInitialDocuments | UploadInitialDocumentsController | InitialFormatDAO |
| CU-18 | Solicitar Proyecto | GUIRequestProject, GUIViewProjectSelection | RequestProjectController, ViewProjectSelectionController | PracticeDAO, ApplicationDAO, InternDAO, ProjectApplicationDAO, ProjectDAO |
| CU-19 | Generar Reporte Mensual | GUIGenerateReport | GenerateReportController | ReportDAO, MonthlyReportDAO |
| CU-20 | Añadir Reporte (Parcial / Mensual) | GUIAddReport | AddReportController | ReportDAO |
| CU-21 | Generar Autoevaluación | GUIGenerateSelfEvaluation | GenerateSelfEvaluationController | SelfEvaluationDAO |
| CU-22 | Añadir Autoevaluación | GUIAddSelfEvaluation | AddSelfEvaluationController | SelfEvaluationDAO, ReportEvaluationDAO, PracticeDAO |
| CU-23 | Evaluación de la OV | GUIAddOVEvaluation | AddOVEvaluationController | OVEvaluationDAO, ReportEvaluationDAO, PracticeDAO |
| CU-25 | Gestionar Actividades (incluye Añadir / Generar Actividad) | GUIManageActivities | ManageActivitiesController | ActivityDAO, ProrrogaDAO |

### Fuera de la lista (movidos a `no_en_lista/`)
CU-13 Inactivar Practicante, CU-15 Consultar Profesor, CU-24 Registrar Experiencia Educativa, CU-26 Actualizar Actividad.

> Nota: CU-26 (Actualizar Actividad) se dispara desde el botón "Actualizar" de la
> vista de CU-25 (Gestionar Actividades).
