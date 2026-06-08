#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maquinas de estado de los 6 CU (StateDiagram nativo de EA 15)."""
import os, sys
import gen_state_xmi as GS

# (archivo): (titulo, states, transitions)
#   state: (nombre, kind)  kind: initial|final|state
#   transition: (origen, destino, trigger, guard, effect)

S = {}

_inactivar = lambda ent, metodo: ([
    ('Initial', 'initial'), ('Activo', 'state'), ('Por confirmar', 'state'),
    ('Inactivando', 'state'), ('Inactivo', 'state'), ('Error', 'state'), ('Final', 'final'),
], [
    ('Initial', 'Activo', '', '', ''),
    ('Activo', 'Por confirmar', 'inactivate' + ent, ent.lower() + ' seleccionado', 'showAlertAndWait(CONFIRMATION)'),
    ('Activo', 'Activo', 'inactivate' + ent, 'sin seleccion', 'showAlert("Sin seleccion", WARNING)'),
    ('Por confirmar', 'Inactivando', '', 'response == OK', metodo),
    ('Por confirmar', 'Activo', '', 'cancela', ''),
    ('Inactivando', 'Inactivo', '', 'exito', 'showAlert("Desactivado", INFORMATION)'),
    ('Inactivando', 'Error', '', 'ServiceException / ValidationException', 'showAlert("Error", ERROR)'),
    ('Inactivo', 'Final', '', '', 'loadActive()'),
    ('Error', 'Activo', '', 'reintentar', ''),
])

_consultar = lambda metodo, lista, vacio=True: ([
    ('Initial', 'initial'), ('Cargando', 'state'), ('Lista mostrada', 'state')]
    + ([('Sin registros', 'state')] if vacio else [])
    + [('Error', 'state'), ('Final', 'final')],
    [
    ('Initial', 'Cargando', '', '', metodo),
    ('Cargando', 'Lista mostrada', '', 'hay registros', 'tableView.setAll(' + lista + ')'),
    ] + ([('Cargando', 'Sin registros', '', 'lista vacia', 'showAlert("Sin registros", INFORMATION)')] if vacio else []) + [
    ('Cargando', 'Error', '', 'ServiceException', 'showAlert("Error de servicio", ERROR)'),
    ('Lista mostrada', 'Final', '', '', ''),
    ] + ([('Sin registros', 'Final', '', '', '')] if vacio else []) + [
    ('Error', 'Final', '', '', ''),
])

# --- Inactivar ---
S['CU-03_InactivarCoordinador'] = ('CU-03 Inactivar Coordinador',
                                   *_inactivar('Coordinator', 'updateUserRolStatus(user)'))
S['CU-13_InactivarPracticante'] = ('CU-13 Inactivar Practicante',
                                   *_inactivar('Intern', 'deactivateIntern(user.getId())'))

# --- Consultar ---
S['CU-06_ConsultarOrganizacionVinculada'] = ('CU-06 Consultar Organizacion Vinculada',
                                             *_consultar('findAll() : List<LinkedOrganization>', 'organizations'))
S['CU-08_ConsultarTecnicoResponsable'] = ('CU-08 Consultar Tecnico Responsable',
                                          *_consultar('findAll() : List<TechnicalSupervisor>', 'technicals'))
S['CU-15_ConsultarProfesor'] = ('CU-15 Consultar Profesor',
                               *_consultar('findActiveProfessors() : List<Professor>', 'professors', vacio=False))

# --- Registrar ---
S['CU-07_RegistrarTecnicoResponsable'] = ('CU-07 Registrar Tecnico Responsable', [
    ('Initial', 'initial'), ('Capturando', 'state'), ('Validando', 'state'),
    ('Guardando', 'state'), ('Registrado', 'state'), ('Final', 'final'),
], [
    ('Initial', 'Capturando', '', '', 'loadLinkedOrganization()'),
    ('Capturando', 'Validando', 'addTechnical', '', 'hasEmptyFields()'),
    ('Validando', 'Capturando', '', 'campos vacios / email invalido', 'showAlert(WARNING)'),
    ('Validando', 'Guardando', '', 'datos validos', 'saveTechnicalResponsible(technical)'),
    ('Guardando', 'Registrado', '', 'exito', 'showAlert("Registro exitoso", INFORMATION)'),
    ('Guardando', 'Capturando', '', 'fallo / duplicado', 'showAlert("Registro fallido", ERROR)'),
    ('Registrado', 'Final', '', '', 'clearFields()'),
])


# clase de contexto (clasificador cuyo comportamiento describe la maquina)
CONTEXT = {
    'CU-03_InactivarCoordinador': 'DeactivateCoordinatorController',
    'CU-13_InactivarPracticante': 'DeactivateInterController',
    'CU-06_ConsultarOrganizacionVinculada': 'ManageLinkedOrganizationController',
    'CU-08_ConsultarTecnicoResponsable': 'ManageTechnicalResponsibleController',
    'CU-15_ConsultarProfesor': 'DeactivateProfessorController',
    'CU-07_RegistrarTecnicoResponsable': 'AddTechnicalResponsibleController',
}


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else 'out_state'
    os.makedirs(outdir, exist_ok=True)
    for fname, (title, states, transitions) in S.items():
        xml = GS.build_state(title, states, transitions, context=CONTEXT.get(fname))
        with open(os.path.join(outdir, fname + '.xmi'), 'w', encoding='cp1252', errors='xmlcharrefreplace') as f:
            f.write(xml)
        print('OK ->', fname + '.xmi', '(%d estados, %d transiciones)' % (len(states), len(transitions)))


if __name__ == '__main__':
    main()
