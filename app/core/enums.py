from enum import Enum, IntEnum


class UserRole(str, Enum):
    ADMIN = "adm"
    DOCTOR = "doc"
    PATIENT = "ptn"


class Sex(str, Enum):
    MALE = "Masculino"
    FEMALE = "Femenino"
    OTHER = "Otro"


class AppointmentStatus(IntEnum):
    SCHEDULED = 1
    COMPLETED = 2
    CANCELED = 3


ROLE_ALIASES = {
    "adm": UserRole.ADMIN.value,
    "admin": UserRole.ADMIN.value,
    "administrator": UserRole.ADMIN.value,
    "doc": UserRole.DOCTOR.value,
    "doctor": UserRole.DOCTOR.value,
    "ptn": UserRole.PATIENT.value,
    "paciente": UserRole.PATIENT.value,
    "patient": UserRole.PATIENT.value,
}

SEX_ALIASES = {
    "m": Sex.MALE.value,
    "masculino": Sex.MALE.value,
    "male": Sex.MALE.value,
    "f": Sex.FEMALE.value,
    "femenino": Sex.FEMALE.value,
    "female": Sex.FEMALE.value,
    "o": Sex.OTHER.value,
    "otro": Sex.OTHER.value,
    "other": Sex.OTHER.value,
}


def normalize_role(value: str | None) -> str:
    if value is None:
        return ""
    return ROLE_ALIASES.get(value.strip().lower(), value.strip().lower())


def normalize_sex(value: str | None) -> str:
    if value is None:
        return ""
    return SEX_ALIASES.get(value.strip().lower(), value.strip())
