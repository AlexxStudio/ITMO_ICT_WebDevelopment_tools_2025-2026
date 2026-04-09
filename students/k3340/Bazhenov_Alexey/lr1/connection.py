from sqlmodel import SQLModel, Session, create_engine


DATABASE_URL = "postgresql://postgres:Spec10spec!@localhost/finance_db"

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(engine)