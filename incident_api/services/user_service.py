"""
Servicio para la lógica de negocio relacionada con los usuarios.

Este módulo encapsula la lógica de negocio para las operaciones de usuarios,
actuando como intermediario entre los endpoints de la API y la capa de acceso a datos (CRUD).
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
import io
import csv
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom

from incident_api import crud, models, schemas
from incident_api.core.hashing import Hasher
from incident_api.models import UserRole
from incident_api.services.audit_service import audit_service


class UserService:
    """
    Clase de servicio para gestionar la lógica de negocio de los usuarios.
    """

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[models.User]:
        """
        Obtiene un usuario por su ID, incluyendo la relación de grupo.

        Args:
            db: La sesión de la base de datos.
            user_id: El ID del usuario a buscar.

        Returns:
            El objeto User o None si no se encuentra.
        """
        return crud.user.get(db, id=user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[models.User]:
        """
        Obtiene un usuario por su email, incluyendo la relación de grupo.
        """
        return crud.user.get_by_email(db, email=email)

    def get_all_users(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.User]:
        """
        Obtiene una lista de todos los usuarios con paginación.
        """
        return crud.user.get_multi(db, skip=skip, limit=limit)

    def get_all_users_with_filters(
        self, db: Session, status: str = None, role: str = None, skip: int = 0, limit: int = 1000
    ) -> List[models.User]:
        """
        Obtiene una lista de todos los usuarios con filtros opcionales.
        """
        return crud.user.get_multi_with_filters(db, status=status, role=role, skip=skip, limit=limit)

    def create_user(self, db: Session, user_in: schemas.UserCreate) -> models.User:
        """
        Crea un nuevo usuario.

        Verifica si el email ya existe antes de la creación.
        Hashea la contraseña antes de guardarla.
        """
        # Hash the password
        hashed_password = Hasher.get_password_hash(user_in.password)
        # Create user data dict with hashed_password instead of password
        user_data = user_in.model_dump(exclude={'password'})
        user_data['hashed_password'] = hashed_password
        # Aquí se podrían añadir validaciones de negocio, como:
        # if crud.user.get_by_email(db, email=user_in.email):
        #     raise HTTPException(status_code=400, detail="Email already registered")
        return crud.user.create(db, obj_in=user_data)

    def update_user(
        self, db: Session, *, user: models.User, user_in: schemas.UserUpdate, current_user: models.User
    ) -> models.User:
        """
        Actualiza la información de un usuario.
        Hashea la contraseña si se proporciona una nueva.

        Args:
            db: La sesión de la base de datos.
            user: El usuario a actualizar.
            user_in: Los datos de actualización.
            current_user: El usuario que realiza la actualización.

        Raises:
            HTTPException: Si no se tienen permisos para cambiar ciertos campos.
        """
        # Autorización: un usuario no puede cambiar su propio rol o grupo
        if user.user_id == current_user.user_id:
            if user_in.role is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puedes cambiar tu propio rol.",
                )
            if user_in.group_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puedes cambiar tu propio grupo.",
                )
        else:
            # Para actualizar otros usuarios, solo administradores pueden cambiar rol o grupo
            if current_user.role != UserRole.ADMINISTRADOR:
                if user_in.role is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para cambiar el rol de un usuario.",
                    )
                if user_in.group_id is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para cambiar el grupo de un usuario.",
                    )

        if user_in.password:
            # Hash the new password
            hashed_password = Hasher.get_password_hash(user_in.password)
            # Create update data dict with hashed_password
            update_data = user_in.model_dump(exclude_unset=True)
            update_data['hashed_password'] = hashed_password
            del update_data['password']
            return crud.user.update(db, db_obj=user, obj_in=update_data)
        else:
            return crud.user.update(db, db_obj=user, obj_in=user_in)

    def deactivate_user(self, db: Session, user_id: int, performed_by: Optional[models.User] = None) -> Optional[models.User]:
        """
        Desactiva la cuenta de un usuario.
        """
        user_to_deactivate = crud.user.get(db, id=user_id)
        if not user_to_deactivate:
            return None

        deactivated_user = crud.user.deactivate(db, db_obj=user_to_deactivate)

        # Registrar en auditoría
        audit_service.log_action(
            db=db,
            user_id=performed_by.user_id if performed_by else user_id,
            action="DEACTIVATE_USER",
            resource_type="USER",
            resource_id=user_id,
            details={"reason": "User account deactivated", "target_user": user_to_deactivate.email},
            success=True
        )

        return deactivated_user

    def activate_user(self, db: Session, user_id: int) -> Optional[models.User]:
        """
        Activa la cuenta de un usuario.
        """
        user_to_activate = crud.user.get(db, id=user_id)
        if not user_to_activate:
            return None
        return crud.user.activate(db, db_obj=user_to_activate)

    def delete_user(self, db: Session, user_id: int) -> Optional[models.User]:
        """
        Elimina un usuario de la base de datos.
        """
        return crud.user.remove(db, id=user_id)

    def get_irt_members(self, db: Session) -> List[models.User]:
        """
        Obtiene una lista de todos los usuarios que son miembros o líderes del IRT.
        """
        return crud.user.get_multi_by_role(
            db, roles=[models.UserRole.MIEMBRO_IRT, models.UserRole.LIDER_IRT]
        )

    def export_users(self, db: Session, format: str, status: str = None, role: str = None):
        """
        Exporta una lista de todos los usuarios a un archivo CSV, JSON o XML.
        """
        users = self.get_all_users_with_filters(db, status=status, role=role)

        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["user_id", "email", "full_name", "role", "position", "city", "is_active", "group_id", "created_at"])
            for user in users:
                writer.writerow([user.user_id, user.email, user.full_name, user.role, user.position, user.city, user.is_active, user.group_id, user.created_at])
            output.seek(0)
            return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users.csv"})
        elif format == "xml":
            root = ET.Element("users")
            for user in users:
                user_elem = ET.SubElement(root, "user")
                ET.SubElement(user_elem, "user_id").text = str(user.user_id)
                ET.SubElement(user_elem, "email").text = user.email
                ET.SubElement(user_elem, "full_name").text = user.full_name
                ET.SubElement(user_elem, "role").text = user.role
                ET.SubElement(user_elem, "position").text = user.position or ""
                ET.SubElement(user_elem, "city").text = user.city or ""
                ET.SubElement(user_elem, "is_active").text = str(user.is_active)
                ET.SubElement(user_elem, "group_id").text = str(user.group_id) if user.group_id else ""
                ET.SubElement(user_elem, "created_at").text = str(user.created_at)

            # Pretty print the XML
            rough_string = ET.tostring(root, encoding='utf-8')
            reparsed = xml.dom.minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')

            output = io.BytesIO(pretty_xml)
            output.seek(0)
            return StreamingResponse(output, media_type="application/xml", headers={"Content-Disposition": "attachment; filename=users.xml"})
        else: # json
            users_dict = [schemas.UserInDB.from_orm(user).model_dump() for user in users]
            json_data = json.dumps(users_dict, indent=2, ensure_ascii=False, default=str)
            return StreamingResponse(io.BytesIO(json_data.encode('utf-8')), media_type="application/json", headers={"Content-Disposition": "attachment; filename=users.json"})


# Crear una instancia del servicio para ser usada en la aplicación
user_service = UserService()
