from app.database import engine, Base, SessionLocal

def test_db_connection():
    # Test if we can connect and execute a simple query
    with engine.connect() as connection:
        result = connection.execute(Base.metadata.tables["logs"].select().limit(1))
        assert result is not None

def test_session_lifecycle(db):
    # Test session fixture
    assert db.is_active
    db.close()

def test_init_db():
    from app.database import init_db
    # Should not raise any exception
    init_db()
