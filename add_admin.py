from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()  


admin = User(
    first_name="Admin",
    last_name="Test",
    email="admin@test.com",
    password=generate_password_hash("admin123"),
    role="admin"
)

db.session.add(admin)
db.session.commit()

print("Admin  dodat!")
