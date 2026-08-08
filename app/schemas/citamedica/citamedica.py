from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.enums import AppointmentStatus


class CitaMedicaBase(BaseModel):
    fechaCita: date
    hora: str
    estado: AppointmentStatus
    motivocancalacion: str | None = None

    @model_validator(mode="after")
    def validate_cancellation(self):
        if self.estado == AppointmentStatus.CANCELED and not self.motivocancalacion:
            raise ValueError("Debe indicar motivo de cancelación cuando la cita está cancelada.")
        if self.estado != AppointmentStatus.CANCELED and self.motivocancalacion:
            raise ValueError("El motivo de cancelación solo aplica para citas canceladas.")
        return self


class CitaMedicaCreate(CitaMedicaBase):
    pass


class CitaMedicaUpdate(BaseModel):
    fechaCita: date | None = None
    hora: str | None = None
    estado: AppointmentStatus | None = None
    motivocancalacion: str | None = None


class CitaMedicaOut(CitaMedicaBase):
    idCita: int
    pacienteID: int
    model_config = ConfigDict(from_attributes=True)
