from Repositories.database import engine
from Repositories.schema.schema import Base
# from Repositories.schema.schema import ErrorLog


def create_tables():
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")

    except Exception as e:
        print("Error creating tables:", e)



def run_migration():
    create_tables()



if __name__ == "__main__":
    run_migration()