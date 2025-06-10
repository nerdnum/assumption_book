from app.services.database import sessionmanager
from app.sqlalchemy_models.components_sql import Component
from app.sqlalchemy_models.user_project_role_sql import Project, User
from app.sqlalchemy_models.risk_types_sql import RiskType


async def validate_project_id(project_id: int) -> int:
    """
    Validate the project ID.

    Args:
        project_id (int): The ID of the project to validate.

    Raises:
        ValueError: If the project ID is not valid.

    Returns:
        int: The validated project ID.
    """

    async with sessionmanager.session() as db:
        project = await db.get(Project, project_id)
        if not project:
            raise ValueError("The referenced project does not exist")
        return project_id


async def validate_component_id(component_id: int) -> int:
    """
    Validate the component ID.

    Args:
        component_id (int): The ID of the component to validate.

    Raises:
        ValueError: If the component ID is not valid.

    Returns:
        int: The validated component ID.
    """

    async with sessionmanager.session() as db:
        parent = await db.get(Component, component_id)
        if not parent:
            raise ValueError("The referenced component does not exist")
        return component_id


async def validate_user_id(user_id: int) -> int:
    """
    Validate the user ID.

    Args:
        user_id (int): The ID of the user to validate.

    Raises:
        ValueError: If the user ID is not valid.

    Returns:
        int: The validated user ID.
    """

    async with sessionmanager.session() as db:
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("The referenced user does not exist")
        return user_id


async def validate_risk_type_id(risk_type_id: int) -> int:
    """
    Validate the risk type ID.

    Args:
        risk_type_id (int): The ID of the risk type to validate.

    Raises:
        ValueError: If the risk type ID is not valid.

    Returns:
        int: The validated risk type ID.
    """

    async with sessionmanager.session() as db:
        risk_type = await db.get(RiskType, risk_type_id)
        if not risk_type:
            raise ValueError("The referenced risk type does not exist")
        return risk_type_id
