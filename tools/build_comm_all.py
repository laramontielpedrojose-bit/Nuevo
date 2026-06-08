#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera los diagramas de comunicacion de los 6 CU solicitados, a partir de los
flujos reales extraidos del codigo (rama jbh-developer). Sin capa BD (hasta DAO/DTO).
"""
import os, sys
import gen_comm_xmi as GC

# Cada CU: (nombre_archivo, titulo, participantes, llamadas)
#   participante: (alias, nombre, kind)   kind: actor|boundary|control|dao|dto
#   llamada: (emisor, receptor, etiqueta)

DIAGRAMS = {}

# ---------------- CU-03 Inactivar Coordinador ----------------
DIAGRAMS['CU-03_InactivarCoordinador'] = ('CU-03 Inactivar Coordinador', [
    ('A', 'Administrador', 'actor'),
    ('UI', ':GUIDeactivateCoordinator', 'boundary'),
    ('C', ':DeactivateCoordinatorController', 'control'),
    ('CDAO', ':CoordinatorDAO', 'dao'),
    ('URDAO', ':UserRoleDAO', 'dao'),
    ('U', 'selectedUser : User', 'dto'),
], [
    ('A', 'UI', 'initialize()'),
    ('UI', 'C', 'initialize()'),
    ('C', 'C', 'loadCoordinators()'),
    ('C', 'CDAO', 'new CoordinatorDAO()'),
    ('C', 'CDAO', 'findActiveCoordinators() : List<Coordinator>'),
    ('C', 'UI', 'tableView.getItems().setAll(coordinators)'),
    ('A', 'UI', 'inactivateCoordinator(actionEvent)'),
    ('UI', 'C', 'inactivateCoordinator(actionEvent)'),
    ('C', 'UI', 'tableView.getSelectionModel().getSelectedItem() : User'),
    ('C', 'UI', '[selectedUser == null] showAlert("Sin seleccion","Seleccione un coordinador.",WARNING)'),
    ('C', 'UI', '[seleccion valida] showAlertAndWait("Desea desactivar","Confirmar?",CONFIRMATION) : Optional<ButtonType>'),
    ('C', 'U', '[OK] setStatus("Inactivo")'),
    ('C', 'U', 'setRole("Coordinador")'),
    ('C', 'C', 'deactivateProcess(selectedUser)'),
    ('C', 'URDAO', 'new UserRoleDAO()'),
    ('C', 'URDAO', 'updateUserRolStatus(user) : boolean'),
    ('C', 'UI', 'showAlert("Coordinador desactivado","Operacion exitosa.",INFORMATION)'),
    ('C', 'C', 'loadCoordinators()'),
])

# ---------------- CU-06 Consultar Organizacion Vinculada ----------------
DIAGRAMS['CU-06_ConsultarOrganizacionVinculada'] = ('CU-06 Consultar Organizacion Vinculada', [
    ('Co', 'Coordinador', 'actor'),
    ('UI', ':GUIManageLinkedOrganization', 'boundary'),
    ('C', ':ManageLinkedOrganizationController', 'control'),
    ('DAO', ':LinkedOrganizationDAO', 'dao'),
    ('O', 'org : LinkedOrganization', 'dto'),
], [
    ('Co', 'UI', 'initialize()'),
    ('UI', 'C', 'initialize()'),
    ('C', 'C', 'loadOrganizations()'),
    ('C', 'DAO', 'new LinkedOrganizationDAO()'),
    ('C', 'DAO', 'findAll() : List<LinkedOrganization>'),
    ('DAO', 'O', 'mapLinkedOrganization(resultSet) : LinkedOrganization'),
    ('C', 'UI', '[!isEmpty] organizationTableView.getItems().setAll(organizations)'),
    ('C', 'UI', '[isEmpty] showAlert("Sin registros","No hay organizaciones.",INFORMATION)'),
])

# ---------------- CU-07 Registrar Tecnico Responsable ----------------
DIAGRAMS['CU-07_RegistrarTecnicoResponsable'] = ('CU-07 Registrar Tecnico Responsable', [
    ('A', 'Administrador', 'actor'),
    ('UI', ':GUIAddTechnicalResponsible', 'boundary'),
    ('C', ':AddTechnicalResponsibleController', 'control'),
    ('LODAO', ':LinkedOrganizationDAO', 'dao'),
    ('TRDAO', ':TechnicalResponsibleDAO', 'dao'),
    ('T', 'technical : TechnicalSupervisor', 'dto'),
], [
    ('A', 'UI', 'initialize()'),
    ('UI', 'C', 'initialize()'),
    ('C', 'C', 'loadLinkedOrganization()'),
    ('C', 'LODAO', 'new LinkedOrganizationDAO()'),
    ('C', 'LODAO', 'findAllActive() : List<LinkedOrganization>'),
    ('C', 'UI', 'organizationComboBox.getItems().addAll(organizations)'),
    ('A', 'UI', 'addTechnical(actionEvent)'),
    ('UI', 'C', 'addTechnical(actionEvent)'),
    ('C', 'C', 'hasEmptyFields() : boolean'),
    ('C', 'UI', '[campos vacios] showAlert("Campos vacios","Complete los campos.",WARNING)'),
    ('C', 'UI', '[email invalido] showAlert("Email invalido","Ingrese un email valido.",WARNING)'),
    ('C', 'C', '[datos validos] processRegistration()'),
    ('C', 'T', 'new TechnicalSupervisor()'),
    ('C', 'T', 'setName(nameField.getText())'),
    ('C', 'T', 'seteMail(emailField.getText())'),
    ('C', 'T', 'setLastName(lastNameField.getText())'),
    ('C', 'T', 'setSecondLastName(lastNameMaterField.getText())'),
    ('C', 'T', 'setPosition(cargoField.getText())'),
    ('C', 'T', 'setIdOrganization(linkedOrganization.getIdLinkedOrganization())'),
    ('C', 'TRDAO', 'new TechnicalResponsibleDAO()'),
    ('C', 'TRDAO', 'saveTechnicalResponsible(technicalSupervisor) : boolean'),
    ('C', 'UI', '[exito] showAlert("Registro exitoso","Tecnico registrado.",INFORMATION)'),
    ('C', 'C', 'clearFields()'),
    ('C', 'UI', '[fallo] showAlert("Registro fallido","No se registro.",ERROR)'),
])

# ---------------- CU-08 Consultar Tecnico Responsable ----------------
DIAGRAMS['CU-08_ConsultarTecnicoResponsable'] = ('CU-08 Consultar Tecnico Responsable', [
    ('Co', 'Coordinador', 'actor'),
    ('UI', ':GUIManageTechnicalResponsible', 'boundary'),
    ('C', ':ManageTechnicalResponsibleController', 'control'),
    ('DAO', ':TechnicalResponsibleDAO', 'dao'),
    ('T', 'technical : TechnicalSupervisor', 'dto'),
], [
    ('Co', 'UI', 'initialize()'),
    ('UI', 'C', 'initialize()'),
    ('C', 'C', 'loadTechnicalResponsibles()'),
    ('C', 'DAO', 'new TechnicalResponsibleDAO()'),
    ('C', 'DAO', 'findAll() : List<TechnicalSupervisor>'),
    ('DAO', 'T', 'mapTechnicalSupervisor(resultSet) : TechnicalSupervisor'),
    ('C', 'UI', '[!isEmpty] technicalResponsibleTableView.getItems().setAll(technicals)'),
    ('C', 'UI', '[isEmpty] showAlert("Sin registros","No hay tecnicos.",INFORMATION)'),
])

# ---------------- CU-13 Inactivar Practicante ----------------
DIAGRAMS['CU-13_InactivarPracticante'] = ('CU-13 Inactivar Practicante', [
    ('Co', 'Coordinador', 'actor'),
    ('UI', ':GUIDeactivateIntern', 'boundary'),
    ('C', ':DeactivateInterController', 'control'),
    ('DAO', ':InternDAO', 'dao'),
    ('I', 'intern : Intern', 'dto'),
    ('U', 'selectedUser : User', 'dto'),
], [
    ('Co', 'UI', 'initialize()'),
    ('UI', 'C', 'initialize()'),
    ('C', 'C', 'loadActiveInterns()'),
    ('C', 'DAO', 'new InternDAO()'),
    ('C', 'DAO', 'findAllActiveinterns() : List<Intern>'),
    ('DAO', 'I', 'mapIntern(resultSet) : Intern'),
    ('C', 'UI', 'internsTableView.getItems().setAll(interns)'),
    ('Co', 'UI', 'inactivateIntern(actionEvent)'),
    ('UI', 'C', 'inactivateIntern(actionEvent)'),
    ('C', 'UI', 'internsTableView.getSelectionModel().getSelectedItem() : User'),
    ('C', 'UI', '[selectedUser == null] showAlert("Sin seleccion","Seleccione un practicante.",WARNING)'),
    ('C', 'UI', '[seleccion valida] showAlertAndWait("Advertencia","Esta seguro?",CONFIRMATION) : Optional<ButtonType>'),
    ('C', 'C', '[OK] inactiveProcess(selectedUser)'),
    ('C', 'DAO', 'new InternDAO()'),
    ('C', 'DAO', 'deactivateIntern(user.getId()) : boolean'),
    ('C', 'C', 'loadActiveInterns()'),
])

# ---------------- CU-15 Consultar Profesor ----------------
DIAGRAMS['CU-15_ConsultarProfesor'] = ('CU-15 Consultar Profesor', [
    ('Co', 'Coordinador', 'actor'),
    ('UI', ':GUIDeactivateProfessor', 'boundary'),
    ('C', ':DeactivateProfessorController', 'control'),
    ('DAO', ':ProfessorDAO', 'dao'),
    ('P', 'professor : Professor', 'dto'),
], [
    ('Co', 'UI', 'initialize()'),
    ('UI', 'C', 'initialize()'),
    ('C', 'C', 'loadProfessors()'),
    ('C', 'DAO', 'new ProfessorDAO()'),
    ('C', 'DAO', 'findActiveProfessors() : List<Professor>'),
    ('DAO', 'P', 'mapProfessor(resultSet) : Professor'),
    ('C', 'UI', 'tableView.getItems().setAll(professors)'),
])


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else 'out_comm'
    os.makedirs(outdir, exist_ok=True)
    for fname, (title, parts, calls) in DIAGRAMS.items():
        xml = GC.build_comm(title, parts, calls)
        with open(os.path.join(outdir, fname + '.xmi'), 'w', encoding='cp1252', errors='xmlcharrefreplace') as f:
            f.write(xml)
        print('OK ->', fname + '.xmi', '(%d objetos, %d mensajes)' % (len(parts), len(calls)))


if __name__ == '__main__':
    main()
