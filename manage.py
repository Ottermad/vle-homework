"""Managment File."""
import logging

from flask_script import Manager

from flask_migrate import upgrade, migrate, init, Migrate

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from app import create_app, db
from config import DATABASE_NAME


manager = Manager(create_app)
manager.add_option("-c", "--config", dest="config_name", required=False)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')


@manager.command
def create_database():
    """Create database."""
    logging.info("Creating database")
    engine = create_engine("postgresql://{}:{}@{}/postgres".format(
        manager.app.config['PG_USER'],
        manager.app.config['PG_PASSWORD'],
        manager.app.config['PG_HOST']
    ))
    conn = engine.connect()
    conn.execute("commit")

    try:
        conn.execute("create database {}".format(DATABASE_NAME))
        logging.info("Created database")
    except ProgrammingError:
        logging.info("Database already existed, continuing")
    finally:
        conn.close()


@manager.command
def test():
    print(dir(manager.app.config))
    print(manager.app.config)

@manager.command
def db_migrate():
    m = Migrate(manager.app, db)
    migrate()


@manager.command
def db_upgrade():
    m = Migrate(manager.app, db)
    upgrade()


@manager.command
def db_init():
    m = Migrate(manager.app, db)
    init()


@manager.command
def run():
    """Run the app."""
    create_database()
    db_upgrade()
    manager.app.run(host="0.0.0.0", port=80)

if __name__ == "__main__":
    manager.run()
