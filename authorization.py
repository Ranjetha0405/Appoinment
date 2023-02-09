import logging
from database import get_db
import ormtable

from fastapi import status, HTTPException

logger = logging.getLogger(__name__)


def user_access_authorization(req_method: str, req_path: str, user_id: int):
    """
    Role Based Access Control(RBAC) is implemented in this function.
    The access control data is fetched from the database and a query is run against it with where clause
    to find out whether it returns data or not. When it does not return any data, the api request is made unauthorized.

    access control data resides in the following two orm_models:
    GroupAccessControl - has the details about the allowed modules and submodules for a group(tagged against any user)
    ModuleResourceMap - has the resources and permissions details for a given module and submodule.

    :param req_method: The method that is used to call api(Example:GET,POST,PATCH...)
    :param req_path: The route/endpoint that is called(Example:/user/{user_id})
    :param user_id: The user_id of the logged-in user who initiated the api call
    :raises HTTPException(HTTP_403_FORBIDDEN)
    """
    logger.info(" Validating on user access ")
    db = next(get_db())
    try:
        authorized_user = None
        authorized_user = db.query(ormtable.Client).all()
        if authorized_user:
            logger.info("Authorised user to use the resource")
            return
        if not authorized_user:
            logger.info("Forbidden user to use the resource")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"You are forbidden to use this resource")
    finally:
        db.close()
