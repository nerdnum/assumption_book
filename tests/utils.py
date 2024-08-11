
from passlib.context import CryptContext
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=2)


def remove_uuid(response_json):
    if 'uuid' in response_json:
        del response_json["uuid"]
    return response_json


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(password)
    print(password_hash)


def print_response(response):
    print()
    print()
    print('---------------------------------------')
    pp.pprint(response.json())
    print('---------------------------------------')
    print()
