from app.database import SessionLocal, engine
from app import models

# Create the database tables
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    dummy_notes = [
        models.Note(
            title="Prod-DB-Password", 
            tags="production,database", 
            created_by="admin_user",
        ),
        models.Note(
            title="AWS-Root-Key", 
            tags="infrastructure,critical", 
            created_by="devops_lead",
        ),
        models.Note(
            title="Grafana-API-Token", 
            tags="monitoring,read-only", 
            created_by="borik_dev",
        )
    ]

    try:
        db.add_all(dummy_notes)
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()