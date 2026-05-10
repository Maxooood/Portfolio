"""
Run this script once to create the admin user.
Usage (from the toir_system directory):
    python create_admin.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

EMAIL    = 'atisstatisstov@gmail.com'
PASSWORD = 'qwerty1234'
NAME     = 'Admin'
EMP_NUM  = '001'
ROLE     = 'admin'

with app.app_context():
    db.create_all()

    existing = User.query.filter_by(email=EMAIL).first()
    if existing:
        existing.set_password(PASSWORD)
        existing.role = ROLE
        existing.is_active = True
        db.session.commit()
        print(f'[OK] User {EMAIL} already existed — password and role updated.')
    else:
        user = User(
            employee_number=EMP_NUM,
            full_name=NAME,
            email=EMAIL,
            role=ROLE,
        )
        user.set_password(PASSWORD)
        db.session.add(user)
        db.session.commit()
        print(f'[OK] Admin user created: {EMAIL}')

    print('Done. You can now log in at http://localhost:5000/login')
