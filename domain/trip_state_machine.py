from enum import Enum
from typing import Optional, Dict, Tuple
from fastapi import HTTPException


# ======================
# ESTADOS DEL VIAJE
# ======================

class TripStatus(str, Enum):
    OFERTA_CLIENTE = "oferta_cliente"
    OFERTA_CONDUCTOR = "oferta_conductor"
    CONTRAOFERTA_CLIENTE = "contraoferta_cliente"
    ACORDADO = "acordado"
    EN_CURSO = "en_curso"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


# ======================
# ACCIONES POSIBLES
# ======================

class TripAction(str, Enum):
    OFERTAR = "ofertar"
    ACEPTAR = "aceptar"
    CONTRAOFERTAR = "contraofertar"
    INICIAR = "iniciar"
    FINALIZAR = "finalizar"
    CANCELAR = "cancelar"


# ======================
# MÁQUINA DE ESTADOS
# ======================

class StateMachine:

    # 🔥 TRANSICIONES VÁLIDAS
    # (estado_actual, acción) → nuevo_estado
    TRANSITIONS: Dict[Tuple[TripStatus, TripAction], TripStatus] = {

        # Conductor oferta sobre viaje del cliente
        (TripStatus.OFERTA_CLIENTE, TripAction.OFERTAR): TripStatus.OFERTA_CONDUCTOR,

        # Cliente acepta oferta del conductor
        (TripStatus.OFERTA_CONDUCTOR, TripAction.ACEPTAR): TripStatus.ACORDADO,

        # Cliente contraoferta
        (TripStatus.OFERTA_CONDUCTOR, TripAction.CONTRAOFERTAR): TripStatus.CONTRAOFERTA_CLIENTE,

        # Conductor acepta contraoferta
        (TripStatus.CONTRAOFERTA_CLIENTE, TripAction.ACEPTAR): TripStatus.ACORDADO,

        # Flujo principal del viaje
        (TripStatus.ACORDADO, TripAction.INICIAR): TripStatus.EN_CURSO,
        (TripStatus.EN_CURSO, TripAction.FINALIZAR): TripStatus.FINALIZADO,

        # Cancelaciones
        (TripStatus.OFERTA_CLIENTE, TripAction.CANCELAR): TripStatus.CANCELADO,
        (TripStatus.OFERTA_CONDUCTOR, TripAction.CANCELAR): TripStatus.CANCELADO,
        (TripStatus.ACORDADO, TripAction.CANCELAR): TripStatus.CANCELADO,
    }

    # 🔥 PERMISOS POR ROL
    PERMISSIONS: Dict[TripAction, list] = {
        TripAction.OFERTAR: ["conductor"],
        TripAction.ACEPTAR: ["cliente", "conductor"],
        TripAction.CONTRAOFERTAR: ["cliente"],
        TripAction.INICIAR: ["conductor"],
        TripAction.FINALIZAR: ["conductor"],
        TripAction.CANCELAR: ["cliente", "conductor"],
    }

    # ======================
    # VALIDACIÓN BASE
    # ======================

    @classmethod
    def can_transition(
        cls,
        current: TripStatus,
        action: TripAction,
        user_role: str,
        is_trip_owner: bool,
        is_assigned_conductor: bool
    ) -> Tuple[bool, Optional[TripStatus]]:

        # 1. Validar rol permitido
        allowed_roles = cls.PERMISSIONS.get(action, [])
        if user_role not in allowed_roles:
            return False, None

        # 2. Validar propiedad / contexto

        # Cliente solo actúa sobre SU viaje
        if user_role == "cliente" and not is_trip_owner:
            return False, None

        # Conductor solo actúa sobre SU viaje (si ya está asignado)
        if action in [TripAction.INICIAR, TripAction.FINALIZAR, TripAction.CANCELAR]:
            if user_role == "conductor" and not is_assigned_conductor:
                return False, None

        # 3. Validar transición de estado
        key = (current, action)
        if key not in cls.TRANSITIONS:
            return False, None

        return True, cls.TRANSITIONS[key]

    # ======================
    # VALIDACIÓN COMPLETA
    # ======================

    @classmethod
    def validate(
        cls,
        current: TripStatus,
        action: TripAction,
        user_id: int,
        user_role: str,
        trip_client_id: int,
        trip_conductor_id: Optional[int]
    ) -> TripStatus:

        is_owner = (user_id == trip_client_id)
        is_conductor = (trip_conductor_id == user_id) if trip_conductor_id else False

        can_do, new_state = cls.can_transition(
            current=current,
            action=action,
            user_role=user_role,
            is_trip_owner=is_owner,
            is_assigned_conductor=is_conductor
        )

        if not can_do:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"No permitido: acción='{action}' "
                    f"estado='{current}' rol='{user_role}' "
                    f"owner={is_owner} conductor={is_conductor}"
                )
            )

        return new_state