from datetime import date

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.security import verify_password
from app.models.paciente.paciente import Paciente
from app.models.doctor.doctor import Doctor
from app.models.citamedica.citamedica import CitaMedica
from app.models.cons_serv.cons_serv import ConsServ
from app.models.servicios.servicios import Servicios
from app.models.usuario.usuario import Usuario
from app.schemas.citamedica.citamedica import CitaMedicaCreate
from app.schemas.consulta.consulta import ConsultaCreate
from app.schemas.doctor.doctor import DoctorCreate
from app.schemas.paciente.paciente import PacienteCreate, PacienteUpdate
from app.schemas.servicios.servicios import ServiciosCreate, ServiciosUpdate
from app.schemas.usuario import LoginRequest, UsuarioCreate
from app.services.citamedica_service import (
    citas_paciente_id_service,
    create_cita_medica_service,
    delete_cita_service,
)
from app.services.consulta_service import create_consulta_service
from app.services.doctor_service import create_doctor_service, delete_doctor_service
from app.services.paciente_service import (
    create_paciente_service,
    update_paciente_service,
)
from app.services.servicios_service import (
    create_servicio_service,
    list_servicios_service,
    update_servicio_service,
)
from app.services.user_service import login_user, register_user_service


def test_register_user_normalizes_role_and_hashes_password(db_session):
    user_out = register_user_service(
        UsuarioCreate(
            nombreUsuario="doctor1",
            contrasenia="secret123",
            rol="doctor",
        ),
        db_session,
    )

    stored_user = db_session.query(Usuario).filter(Usuario.nombreUsuario == "doctor1").first()

    assert user_out.rol == "doc"
    assert stored_user is not None
    assert stored_user.contrasenia != "secret123"
    assert verify_password("secret123", stored_user.contrasenia)


def test_login_user_returns_normalized_patient_role_and_profile_flag(db_session):
    register_user_service(
        UsuarioCreate(nombreUsuario="patient1", contrasenia="secret123", rol="ptn"),
        db_session,
    )
    user = db_session.query(Usuario).filter(Usuario.nombreUsuario == "patient1").first()

    paciente = Paciente(
        usuarioID=user.idUsuario,
        nombrePaciente="Ana",
        apellidoPaciente="Lopez",
        cedula="001-000000-0000A",
        telefono=88888888,
        fechaNacimiento=date(1998, 5, 10),
        sexo="F",
    )
    db_session.add(paciente)
    db_session.commit()

    result = login_user(
        LoginRequest(username="patient1", password="secret123"),
        db_session,
    )

    assert result["user"]["rol"] == "ptn"
    assert result["user"]["has_paciente_profile"] is True
    assert isinstance(result["token"], str)
    assert result["token"]


def test_create_paciente_service_uses_authenticated_user_id(db_session):
    user_out = register_user_service(
        UsuarioCreate(
            nombreUsuario="patient2",
            contrasenia="secret123",
            rol="paciente",
        ),
        db_session,
    )

    paciente_out = create_paciente_service(
        PacienteCreate(
            nombrePaciente="Luis",
            apellidoPaciente="Perez",
            cedula="002-000000-0000B",
            telefono=77777777,
            fechaNacimiento=date(1995, 1, 1),
            sexo="M",
        ),
        db_session,
        {"idUsuario": user_out.idUsuario, "nombreUsuario": user_out.nombreUsuario, "rol": "ptn"},
    )

    assert paciente_out.usuarioID == user_out.idUsuario
    assert paciente_out.nombrePaciente == "Luis"
    assert paciente_out.sexo == "Masculino"


def test_patient_cannot_update_another_patients_profile(db_session):
    owner = register_user_service(
        UsuarioCreate(nombreUsuario="owner", contrasenia="secret123", rol="ptn"),
        db_session,
    )
    intruder = register_user_service(
        UsuarioCreate(nombreUsuario="intruder", contrasenia="secret123", rol="ptn"),
        db_session,
    )

    paciente_out = create_paciente_service(
        PacienteCreate(
            nombrePaciente="Maria",
            apellidoPaciente="Owner",
            cedula="003-000000-0000C",
            telefono=66666666,
            fechaNacimiento=date(1990, 2, 2),
            sexo="F",
        ),
        db_session,
        {"idUsuario": owner.idUsuario, "nombreUsuario": owner.nombreUsuario, "rol": "ptn"},
    )

    with pytest.raises(HTTPException) as exc_info:
        update_paciente_service(
            paciente_out.idPaciente,
            PacienteUpdate(nombrePaciente="Hack"),
            db_session,
            {"idUsuario": intruder.idUsuario, "nombreUsuario": intruder.nombreUsuario, "rol": "ptn"},
            partial=True,
        )

    assert exc_info.value.status_code == 404


def test_admin_can_delete_any_doctor_profile(db_session):
    admin = register_user_service(
        UsuarioCreate(nombreUsuario="admin1", contrasenia="secret123", rol="adm"),
        db_session,
    )
    doctor_user = register_user_service(
        UsuarioCreate(nombreUsuario="doctor2", contrasenia="secret123", rol="doc"),
        db_session,
    )
    doctor_profile = create_doctor_service(
        DoctorCreate(
            nombreDoctor="Carlos",
            apellidoDoctor="Ruiz",
            tlfDoctor=55555555,
            especialidad="Cardiologia",
            horario="08:00-16:00",
            sexo="M",
        ),
        db_session,
        {"idUsuario": doctor_user.idUsuario, "nombreUsuario": doctor_user.nombreUsuario, "rol": "doc"},
    )

    deleted = delete_doctor_service(
        doctor_profile.idDoctor,
        db_session,
        {"idUsuario": admin.idUsuario, "nombreUsuario": admin.nombreUsuario, "rol": "adm"},
    )

    assert deleted.idDoctor == doctor_profile.idDoctor
    assert db_session.query(Doctor).filter(Doctor.idDoctor == doctor_profile.idDoctor).first() is None


def test_patient_cannot_view_other_patient_appointments(db_session):
    owner = register_user_service(
        UsuarioCreate(nombreUsuario="ptn-owner", contrasenia="secret123", rol="ptn"),
        db_session,
    )
    intruder = register_user_service(
        UsuarioCreate(nombreUsuario="ptn-intruder", contrasenia="secret123", rol="ptn"),
        db_session,
    )

    owner_paciente = create_paciente_service(
        PacienteCreate(
            nombrePaciente="Owner",
            apellidoPaciente="Patient",
            cedula="004-000000-0000D",
            telefono=99999999,
            fechaNacimiento=date(1991, 3, 3),
            sexo="F",
        ),
        db_session,
        {"idUsuario": owner.idUsuario, "nombreUsuario": owner.nombreUsuario, "rol": "ptn"},
    )
    create_paciente_service(
        PacienteCreate(
            nombrePaciente="Intruder",
            apellidoPaciente="Patient",
            cedula="005-000000-0000E",
            telefono=99999998,
            fechaNacimiento=date(1992, 4, 4),
            sexo="M",
        ),
        db_session,
        {"idUsuario": intruder.idUsuario, "nombreUsuario": intruder.nombreUsuario, "rol": "ptn"},
    )
    create_cita_medica_service(
        CitaMedicaCreate(
            fechaCita=date(2026, 4, 1),
            hora="09:00",
            estado=1,
            motivocancalacion=None,
        ),
        db_session,
        {"idUsuario": owner.idUsuario, "nombreUsuario": owner.nombreUsuario, "rol": "ptn"},
    )

    with pytest.raises(HTTPException) as exc_info:
        citas_paciente_id_service(
            owner_paciente.idPaciente,
            db_session,
            {"idUsuario": intruder.idUsuario, "nombreUsuario": intruder.nombreUsuario, "rol": "ptn"},
        )

    assert exc_info.value.status_code == 403


def test_create_consulta_uses_doctor_profile_id_and_real_service_records(db_session):
    doctor_user = register_user_service(
        UsuarioCreate(nombreUsuario="doctor3", contrasenia="secret123", rol="doc"),
        db_session,
    )
    patient_user = register_user_service(
        UsuarioCreate(nombreUsuario="ptn3", contrasenia="secret123", rol="ptn"),
        db_session,
    )

    doctor_profile = create_doctor_service(
        DoctorCreate(
            nombreDoctor="Laura",
            apellidoDoctor="Mendez",
            tlfDoctor=12345678,
            especialidad="Pediatria",
            horario="09:00-17:00",
            sexo="F",
        ),
        db_session,
        {"idUsuario": doctor_user.idUsuario, "nombreUsuario": doctor_user.nombreUsuario, "rol": "doc"},
    )
    patient_profile = create_paciente_service(
        PacienteCreate(
            nombrePaciente="Nora",
            apellidoPaciente="Diaz",
            cedula="006-000000-0000F",
            telefono=12344321,
            fechaNacimiento=date(2000, 6, 6),
            sexo="F",
        ),
        db_session,
        {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
    )
    cita = create_cita_medica_service(
        CitaMedicaCreate(
            fechaCita=date(2026, 4, 2),
            hora="10:30",
            estado=1,
            motivocancalacion=None,
        ),
        db_session,
        {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
    )
    servicio = Servicios(nombreServicio="Consulta General", descripcion="Revision", costo=25.0)
    db_session.add(servicio)
    db_session.commit()
    db_session.refresh(servicio)

    consulta_out = create_consulta_service(
        ConsultaCreate(
            valoracion="Paciente estable",
            fechaConsulta=date(2026, 4, 2),
            citaID=cita.idCita,
            servicios=[servicio.idServicios],
        ),
        db_session,
        {"idUsuario": doctor_user.idUsuario, "nombreUsuario": doctor_user.nombreUsuario, "rol": "doc"},
    )

    assoc = db_session.query(ConsServ).filter(ConsServ.consultaID == consulta_out.idConsulta).all()
    assert consulta_out.doctorID == doctor_profile.idDoctor
    assert consulta_out.citaID == cita.idCita
    assert len(assoc) == 1
    assert assoc[0].servicios == servicio.idServicios
    assert db_session.query(CitaMedica).filter(CitaMedica.pacienteID == patient_profile.idPaciente).count() == 1


def test_delete_cita_blocks_when_consulta_exists(db_session):
    doctor_user = register_user_service(
        UsuarioCreate(nombreUsuario="doctor4", contrasenia="secret123", rol="doc"),
        db_session,
    )
    patient_user = register_user_service(
        UsuarioCreate(nombreUsuario="ptn4", contrasenia="secret123", rol="ptn"),
        db_session,
    )

    create_doctor_service(
        DoctorCreate(
            nombreDoctor="Jose",
            apellidoDoctor="Soto",
            tlfDoctor=87654321,
            especialidad="General",
            horario="07:00-15:00",
            sexo="M",
        ),
        db_session,
        {"idUsuario": doctor_user.idUsuario, "nombreUsuario": doctor_user.nombreUsuario, "rol": "doc"},
    )
    create_paciente_service(
        PacienteCreate(
            nombrePaciente="Pedro",
            apellidoPaciente="Lopez",
            cedula="007-000000-0000G",
            telefono=33334444,
            fechaNacimiento=date(1999, 7, 7),
            sexo="M",
        ),
        db_session,
        {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
    )
    cita = create_cita_medica_service(
        CitaMedicaCreate(
            fechaCita=date(2026, 4, 3),
            hora="11:00",
            estado=1,
            motivocancalacion=None,
        ),
        db_session,
        {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
    )
    servicio = Servicios(nombreServicio="Control", descripcion="Seguimiento", costo=40.0)
    db_session.add(servicio)
    db_session.commit()
    db_session.refresh(servicio)
    create_consulta_service(
        ConsultaCreate(
            valoracion="Con observacion",
            fechaConsulta=date(2026, 4, 3),
            citaID=cita.idCita,
            servicios=[servicio.idServicios],
        ),
        db_session,
        {"idUsuario": doctor_user.idUsuario, "nombreUsuario": doctor_user.nombreUsuario, "rol": "doc"},
    )

    with pytest.raises(HTTPException) as exc_info:
        delete_cita_service(
            cita.idCita,
            db_session,
            {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
        )

    assert exc_info.value.status_code == 400


def test_invalid_role_is_rejected_by_schema():
    with pytest.raises(ValidationError):
        UsuarioCreate(nombreUsuario="x", contrasenia="secret123", rol="superadmin")


def test_canceled_appointment_requires_reason(db_session):
    patient_user = register_user_service(
        UsuarioCreate(nombreUsuario="ptn6", contrasenia="secret123", rol="ptn"),
        db_session,
    )
    create_paciente_service(
        PacienteCreate(
            nombrePaciente="Mario",
            apellidoPaciente="Campos",
            cedula="008-000000-0000H",
            telefono=22223333,
            fechaNacimiento=date(1994, 8, 8),
            sexo="Masculino",
        ),
        db_session,
        {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
    )

    with pytest.raises(ValidationError):
        CitaMedicaCreate(
            fechaCita=date(2026, 4, 4),
            hora="13:00",
            estado=3,
            motivocancalacion=None,
        )


def test_patient_can_list_services_but_cannot_create_them(db_session):
    doctor_user = register_user_service(
        UsuarioCreate(nombreUsuario="doctor5", contrasenia="secret123", rol="doc"),
        db_session,
    )
    patient_user = register_user_service(
        UsuarioCreate(nombreUsuario="ptn5", contrasenia="secret123", rol="ptn"),
        db_session,
    )

    created = create_servicio_service(
        ServiciosCreate(
            nombreServicio="Ultrasonido",
            descripcion="Imagen diagnostica",
            costo=55.0,
        ),
        db_session,
        {"idUsuario": doctor_user.idUsuario, "nombreUsuario": doctor_user.nombreUsuario, "rol": "doc"},
    )

    listed = list_servicios_service(
        0,
        1,
        db_session,
        {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
    )

    assert len(listed) == 1
    assert listed[0].idServicios == created.idServicios

    with pytest.raises(HTTPException) as exc_info:
        create_servicio_service(
            ServiciosCreate(
                nombreServicio="Laboratorio",
                descripcion="Panel completo",
                costo=80.0,
            ),
            db_session,
            {"idUsuario": patient_user.idUsuario, "nombreUsuario": patient_user.nombreUsuario, "rol": "ptn"},
        )

    assert exc_info.value.status_code == 403


def test_update_servicio_rejects_duplicate_name(db_session):
    admin = register_user_service(
        UsuarioCreate(nombreUsuario="admin2", contrasenia="secret123", rol="adm"),
        db_session,
    )

    service_a = create_servicio_service(
        ServiciosCreate(
            nombreServicio="Rayos X",
            descripcion="Imagen simple",
            costo=35.0,
        ),
        db_session,
        {"idUsuario": admin.idUsuario, "nombreUsuario": admin.nombreUsuario, "rol": "adm"},
    )
    create_servicio_service(
        ServiciosCreate(
            nombreServicio="Tomografia",
            descripcion="Imagen avanzada",
            costo=120.0,
        ),
        db_session,
        {"idUsuario": admin.idUsuario, "nombreUsuario": admin.nombreUsuario, "rol": "adm"},
    )

    with pytest.raises(HTTPException) as exc_info:
        update_servicio_service(
            service_a.idServicios,
            ServiciosUpdate(nombreServicio="Tomografia"),
            db_session,
            {"idUsuario": admin.idUsuario, "nombreUsuario": admin.nombreUsuario, "rol": "adm"},
        )

    assert exc_info.value.status_code == 409
