from models import Base, engine

def reset_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    reset_database()