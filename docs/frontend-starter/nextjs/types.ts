export type Role = "adm" | "doc" | "ptn";
export type Sex = "Masculino" | "Femenino" | "Otro";
export type AppointmentStatus = 1 | 2 | 3;

export type ApiResponse<T> = {
  statusCode: number;
  isSuccess: boolean;
  errorMessages: string[];
  successMessages: string[];
  result: T;
};

export type AuthUser = {
  idUsuario: number;
  nombreUsuario: string;
  rol: Role;
  has_doctor_profile?: boolean;
  has_paciente_profile?: boolean;
};

export type LoginResult = {
  user: AuthUser;
  token: string;
};

export type Usuario = {
  idUsuario: number;
  nombreUsuario: string;
  rol: Role;
};

export type Paciente = {
  idPaciente: number;
  usuarioID: number;
  nombrePaciente: string;
  apellidoPaciente: string;
  cedula: string;
  telefono: number;
  fechaNacimiento: string;
  sexo: Sex;
};

export type Doctor = {
  idDoctor: number;
  usuarioID: number;
  nombreDoctor: string;
  apellidoDoctor: string;
  tlfDoctor: number;
  especialidad: string;
  horario: string | null;
  sexo: Sex;
};

export type Servicio = {
  idServicios: number;
  nombreServicio: string;
  descripcion: string;
  costo: number;
};

export type CitaMedica = {
  idCita: number;
  pacienteID: number;
  fechaCita: string;
  hora: string;
  estado: AppointmentStatus;
  motivocancalacion: string | null;
};

export type Consulta = {
  idConsulta: number;
  doctorID: number;
  citaID: number;
  valoracion: string;
  fechaConsulta: string;
};

export type LoginPayload = {
  username: string;
  password: string;
};

export type RegisterPayload = {
  nombreUsuario: string;
  contrasenia: string;
  rol: Role;
};

export type CreatePacientePayload = {
  nombrePaciente: string;
  apellidoPaciente: string;
  cedula: string;
  telefono: number;
  fechaNacimiento: string;
  sexo: Sex;
};

export type UpdatePacientePayload = Partial<CreatePacientePayload>;

export type CreateDoctorPayload = {
  nombreDoctor: string;
  apellidoDoctor: string;
  tlfDoctor: number;
  especialidad: string;
  horario: string | null;
  sexo: Sex;
};

export type UpdateDoctorPayload = Partial<CreateDoctorPayload>;

export type CreateServicioPayload = {
  nombreServicio: string;
  descripcion: string;
  costo: number;
};

export type UpdateServicioPayload = Partial<CreateServicioPayload>;

export type CreateCitaPayload = {
  fechaCita: string;
  hora: string;
  estado: AppointmentStatus;
  motivocancalacion?: string | null;
};

export type UpdateCitaPayload = Partial<CreateCitaPayload>;

export type CreateConsultaPayload = {
  valoracion: string;
  fechaConsulta: string;
  citaID: number;
  servicios: number[];
};

export type UpdateConsultaPayload = {
  valoracion?: string;
  fechaConsulta?: string;
};
