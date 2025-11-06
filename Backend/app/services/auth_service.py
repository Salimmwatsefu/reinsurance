from flask_jwt_extended import create_access_token
from app import db
from app.models import User, UserRole
import bcrypt
from werkzeug.exceptions import BadRequest, Unauthorized


def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password: str, password_hash: bytes) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)


def create_user(email: str, first_name: str, last_name: str, password: str, role: str) -> User:
    """Create a new user with hashed password."""
    if User.query.filter_by(email=email).first():
        raise BadRequest(f"User with email {email} already exists")

    try:
        role_enum = UserRole(role)  # 👈 enforce enum
    except ValueError:
        raise BadRequest("Role must be 'admin' or 'insurer'")

    hashed_password = hash_password(password)

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=hashed_password.decode('utf-8'),  # Store as string
        role=role_enum
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> dict:
    """Authenticate a user and return a JWT token."""
    user = User.query.filter_by(email=email).first()
    if not user:
        raise Unauthorized("Invalid email or password")

    if not verify_password(password, user.password_hash.encode('utf-8')):
        raise Unauthorized("Invalid email or password")

    # JWT payload uses .value
    access_token = create_access_token(
        identity=str(user.id),  # must be a string
        additional_claims={
            'email': user.email,
            'role': user.role.value
        }
    )

    return {
        'access_token': access_token,
        'user': user.to_dict()  
    }
