#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera todos los diagramas de secuencia en XMI nativo de EA 15:
   - los 12 CU a partir de los XMI 2.1 de origen,
   - el CU 'Anadir Actividad' (sin fuente, definido por especificacion),
   - y el archivo combinado con todos.
Uso:  python3 build_all.py <dir_origen_xmi> <dir_salida>
"""
import sys, os, glob
import gen_ea_xmi as G

# --- CU 'Anadir Actividad' (no tiene fuente; se modela por analogia con CU-14
#     y CU-26: crea una Activity y la guarda; SOLO agrega, no modifica) ---------
AA_PARTICIPANTS = [
    ('Profesor', 'Profesor', 'actor'),
    ('UI', ':GUIAddActivity', 'boundary'),
    ('C', ':AddActivityController', 'control'),
    ('A', 'activity : Activity', 'object'),
    ('DAO', ':ActivityDAO', 'object'),
]

AA_EVENTS = [
    ('msg', 'Profesor', 'UI', 'llenar formulario y clic en "Guardar"', 'call'),
    ('msg', 'UI', 'C', 'addActivity(actionEvent)', 'call'),
    ('alt', [
        ('campos requeridos vacios', [
            ('msg', 'C', 'UI', 'showAlert("Campos vacios", "Complete los campos obligatorios.", WARNING)', 'call'),
            ('msg', 'UI', 'Profesor', 'muestra dialogo', 'reply'),
        ]),
        ('fechas fuera del rango del proyecto', [
            ('msg', 'C', 'UI', 'showAlert("Fechas fuera del rango del proyecto", "Ajuste las fechas.", WARNING)', 'call'),
            ('msg', 'UI', 'Profesor', 'muestra dialogo', 'reply'),
        ]),
        ('datos validos', [
            ('msg', 'C', 'A', 'new Activity()', 'create'),
            ('msg', 'C', 'A', 'setName(nameTextField.getText())', 'call'),
            ('msg', 'C', 'A', 'setDescription(descriptionTextArea.getText())', 'call'),
            ('msg', 'C', 'A', 'setStartDate(fechaInicioPicker.getValue())', 'call'),
            ('msg', 'C', 'A', 'setEndDate(fechaFinPicker.getValue())', 'call'),
            ('msg', 'C', 'A', 'setIdProject(idProject)', 'call'),
            ('msg', 'C', 'DAO', 'save(activity)', 'call'),
            ('msg', 'DAO', 'A', 'getName() / getDescription() / getStartDate() / getEndDate() / getIdProject()', 'call'),
            ('msg', 'A', 'DAO', 'valores', 'reply'),
            ('msg', 'DAO', 'C', 'boolean', 'reply'),
            ('alt', [
                ('agregada', [
                    ('msg', 'C', 'UI', 'showAlert("Actividad agregada", "La actividad fue registrada correctamente.", INFORMATION)', 'call'),
                    ('msg', 'UI', 'Profesor', 'muestra dialogo', 'reply'),
                ]),
                ('ValidationException', [
                    ('msg', 'C', 'UI', 'showAlert("Error de validacion", validationException.getMessage(), ERROR)', 'call'),
                    ('msg', 'UI', 'Profesor', 'muestra dialogo', 'reply'),
                ]),
                ('ServiceException', [
                    ('msg', 'C', 'UI', 'showAlert("Servicio no disponible", "No se pudo guardar la actividad. Intente mas tarde.", ERROR)', 'call'),
                    ('msg', 'UI', 'Profesor', 'muestra dialogo', 'reply'),
                ]),
            ]),
        ]),
    ]),
]

AA_NAME = 'CU-27_AnadirActividad'


def addactivity_parsed():
    return G.build_spec(AA_NAME, AA_PARTICIPANTS, AA_EVENTS)


# ---- CU 'Registrar Proyecto' (AddProjectController; sin fuente, por flujo real) ----
AP_PARTICIPANTS = [
    ('Co', 'Coordinador', 'actor'),
    ('UI', ':GUIAddProject', 'boundary'),
    ('C', ':AddProjectController', 'control'),
    ('LODAO', ':LinkedOrganizationDAO', 'object'),
    ('EEDAO', ':EducationalExperienceDAO', 'object'),
    ('P', 'project : Project', 'object'),
    ('DAO', ':ProjectDAO', 'object'),
]

AP_EVENTS = [
    ('msg', 'Co', 'UI', 'initialize()', 'call'),
    ('msg', 'UI', 'C', 'initialize()', 'call'),
    ('msg', 'C', 'C', 'loadOrganizations()', 'call'),
    ('msg', 'C', 'LODAO', 'findAllActive() : List<LinkedOrganization>', 'call'),
    ('msg', 'C', 'C', 'loadEducationalExperiences()', 'call'),
    ('msg', 'C', 'EEDAO', 'findAll() : List<EducationalExperience>', 'call'),
    ('msg', 'Co', 'UI', 'llenar formulario y clic en "Guardar"', 'call'),
    ('msg', 'UI', 'C', 'addProject(actionEvent)', 'call'),
    ('alt', [
        ('!inputIsValid', [
            ('msg', 'C', 'UI', 'showAlert("Campos invalidos", "Complete los campos requeridos.", WARNING)', 'call'),
            ('msg', 'UI', 'Co', 'muestra dialogo', 'reply'),
        ]),
        ('inputIsValid', [
            ('msg', 'C', 'C', 'registrationProcess()', 'call'),
            ('msg', 'C', 'C', 'buildProject() : Project', 'call'),
            ('msg', 'C', 'P', 'new Project()', 'create'),
            ('msg', 'C', 'P', 'setNrc(selectedEE.getNrc())', 'call'),
            ('msg', 'C', 'P', 'setName(nameTextField.getText())', 'call'),
            ('msg', 'C', 'P', 'setDescription(descriptionTextField.getText())', 'call'),
            ('msg', 'C', 'P', 'setIdOrganization(organizationComboBox.getValue().getIdLinkedOrganization())', 'call'),
            ('msg', 'C', 'P', 'setIdTechnicalSupervisor(technicalComboBox.getValue().getIdTechnicalSupervisor())', 'call'),
            ('msg', 'C', 'P', 'setStartDate(startDate.getValue())', 'call'),
            ('msg', 'C', 'P', 'setEndDate(endDate.getValue())', 'call'),
            ('msg', 'C', 'P', 'setMaximumPlaces(Integer.parseInt(capacityTextField.getText()))', 'call'),
            ('msg', 'C', 'DAO', 'new ProjectDAO()', 'call'),
            ('msg', 'C', 'DAO', 'existsByNrc(project.getNrc()) : boolean', 'call'),
            ('alt', [
                ('nrcAlreadyUsed', [
                    ('msg', 'C', 'UI', 'showAlert("EE con proyecto existente", "Ya existe un proyecto para esa EE.", WARNING)', 'call'),
                    ('msg', 'UI', 'Co', 'muestra dialogo', 'reply'),
                ]),
                ('nrc disponible', [
                    ('msg', 'C', 'DAO', 'saveProject(project) : boolean', 'call'),
                    ('alt', [
                        ('guardado', [
                            ('msg', 'C', 'UI', 'showAlert("Exito", "El proyecto ha sido guardado exitosamente.", INFORMATION)', 'call'),
                            ('msg', 'UI', 'Co', 'muestra dialogo', 'reply'),
                        ]),
                        ('no guardado', [
                            ('msg', 'C', 'UI', 'showAlert("Error", "No se pudo guardar el proyecto.", ERROR)', 'call'),
                            ('msg', 'UI', 'Co', 'muestra dialogo', 'reply'),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ]),
]

AP_NAME = 'CU-RegistrarProyecto'


def addproject_parsed():
    return G.build_spec(AP_NAME, AP_PARTICIPANTS, AP_EVENTS)


def main():
    srcdir, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    cu_files = sorted(glob.glob(os.path.join(srcdir, 'CU-*.xmi')))

    # individuales (12 CU)
    for f in cu_files:
        xml = G.build(f)
        with open(os.path.join(outdir, os.path.basename(f)), 'w', encoding='cp1252', errors='xmlcharrefreplace') as fh:
            fh.write(xml)
    # individual de Anadir Actividad
    xml = G.build(addactivity_parsed())
    with open(os.path.join(outdir, AA_NAME + '.xmi'), 'w', encoding='cp1252', errors='xmlcharrefreplace') as fh:
        fh.write(xml)
    # individual de Registrar Proyecto
    xml = G.build(addproject_parsed())
    with open(os.path.join(outdir, AP_NAME + '.xmi'), 'w', encoding='cp1252', errors='xmlcharrefreplace') as fh:
        fh.write(xml)

    # combinado (12 CU + Anadir Actividad + Registrar Proyecto)
    sources = list(cu_files) + [addactivity_parsed(), addproject_parsed()]
    xml = G.build_combined(sources)
    with open(os.path.join(outdir, 'SPP_Secuencias_TODOS.xmi'), 'w', encoding='cp1252', errors='xmlcharrefreplace') as fh:
        fh.write(xml)
    print('OK: %d CU + Anadir Actividad + combinado -> %s' % (len(cu_files), outdir))


if __name__ == '__main__':
    main()
