import psycopg2
import json
from slugify import slugify


def get_config():
    with open('config.json') as f:
        return json.load(f)["db_url"]


def slugify_components(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM components;")
    rows = cursor.fetchall()
    columns = [colom[0] for colom in cursor.description]
    print(columns)
    sql = "UPDATE components SET slug = '%s' WHERE id = %s;"
    for row in rows:
        data = dict(zip(columns, row))
        cursor.execute(sql % (slugify(data["title"]), data["id"]))
    cursor.close()


if __name__ == '__main__':
    url = get_config()
    with psycopg2.connect(host="localhost", dbname="fastapi", user="postgres", password="!Nerdnum#1") as connection:
        slugify_components(connection)
