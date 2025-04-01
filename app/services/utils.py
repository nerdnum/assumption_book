import pprint

from sqlalchemy.exc import IntegrityError

from app.services.database import sessionmanager
from app.sqlalchemy_models.user_project_role_sql import Project


def error_print(filename, method, error_string):
    print()
    print("------------------ ERROR -------------------")
    print(filename, "-", method)
    print("------------------ DETAIL ------------------")
    print(error_string)
    print("-------------------- END -------------------")
    print()


def translate_exception(filename: str, method: str, exception: Exception) -> Exception:
    """
    Process an exception by printing the error details and returning an user and fastapi friendly
    exeption, either a ValueError or and HTTPException.

    Args:
        name (str): The name of the exception.
        exception (Exception): The exception object.

    Returns:
        Exception: The original exception object.

    """
    error_print(filename, method, exception)

    search_name = filename.split(".")[-1]

    error_str = str(exception)

    integrity_error_dict = {
        "components": {
            "create": [
                {
                    "text": 'insert or update on table "components" violates foreign key constraint "components_parent_id_fkey"',
                    "response": "The referenced parent component does not exist",
                },
                {
                    "text": 'insert or update on table "components" violates foreign key constraint "components_project_id_fkey',
                    "response": "The referenced project does not exist",
                },
                {
                    "text": 'duplicate key value violates unique constraint "components_parent_id_title_key"',
                    "response": "A component with the same title already exists for the parent component",
                },
            ]
        }
    }

    if isinstance(exception, IntegrityError):
        print("\n\n\n----------------------------------------------->")
        for item in integrity_error_dict[search_name][method]:
            if error_str.find(item["text"]) != -1:
                print("----------------------------------------------->\n\n\n")
                return ValueError(item["response"])
        return ValueError("Integrity error not identified")

    return exception


async def get_project(project_id: int):
    async with sessionmanager.session() as db:
        project = await db.get(Project, project_id)
        return project
    return False


async def get_parent(component_id: int):
    from app.sqlalchemy_models.components_sql import Component

    async with sessionmanager.session() as db:
        parent = await db.get(Component, component_id)
        return parent
    return False


def pretty_print(data):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)
