#!/usr/bin/env python3
"""
Initialization script for ИС ТОиР.
Creates all tables and populates sample data.
Run from the backend/ directory: python ../create_admin.py
Or from root: python create_admin.py
"""
import asyncio
import sys
import os

# Allow running from project root or backend/
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.join(_script_dir, "backend")
sys.path.insert(0, _backend_dir)
# Change CWD to backend so SQLite db is created there
os.chdir(_backend_dir)

from app.db.session import init_db, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.equipment import Equipment, EquipmentNorm, EquipmentStatus
from app.models.request import FaultType
from app.models.service import AuxiliaryService, RoutingRule
from sqlalchemy import select


async def create_sample_data():
    await init_db()
    print("✓ Database tables created")

    async with AsyncSessionLocal() as db:
        # Check if admin exists
        existing = await db.execute(select(User).where(User.email == "admin@toir.ru"))
        if existing.scalar_one_or_none():
            print("Admin user already exists, skipping seed data")
            return

        # ─── Users ──────────────────────────────────────────────────────────
        users = [
            User(
                employee_number="EMP001",
                full_name="Администратор Системы",
                email="admin@toir.ru",
                role=UserRole.ADMIN,
                department="ИТ",
                phone="+7-999-000-0001",
                password_hash=get_password_hash("admin123"),
                is_active=True,
            ),
            User(
                employee_number="EMP002",
                full_name="Иванов Пётр Сергеевич",
                email="ppr@toir.ru",
                role=UserRole.PPR_ENGINEER,
                department="Отдел ТОиР",
                phone="+7-999-000-0002",
                password_hash=get_password_hash("ppr123"),
                is_active=True,
            ),
            User(
                employee_number="EMP003",
                full_name="Сидорова Анна Владимировна",
                email="dispatcher@toir.ru",
                role=UserRole.DISPATCHER,
                department="Диспетчерская",
                phone="+7-999-000-0003",
                password_hash=get_password_hash("disp123"),
                is_active=True,
            ),
            User(
                employee_number="EMP004",
                full_name="Козлов Дмитрий Олегович",
                email="executor1@toir.ru",
                role=UserRole.EXECUTOR,
                department="Бригада №1",
                phone="+7-999-000-0004",
                password_hash=get_password_hash("exec123"),
                is_active=True,
            ),
            User(
                employee_number="EMP005",
                full_name="Новиков Алексей Михайлович",
                email="executor2@toir.ru",
                role=UserRole.EXECUTOR,
                department="Бригада №2",
                phone="+7-999-000-0005",
                password_hash=get_password_hash("exec123"),
                is_active=True,
            ),
            User(
                employee_number="EMP006",
                full_name="Петрова Елена Ивановна",
                email="shift@toir.ru",
                role=UserRole.SHIFT_MANAGER,
                department="Производство",
                phone="+7-999-000-0006",
                password_hash=get_password_hash("shift123"),
                is_active=True,
            ),
            User(
                employee_number="EMP007",
                full_name="Фёдоров Андрей Павлович",
                email="manager@toir.ru",
                role=UserRole.MANAGER,
                department="Управление",
                phone="+7-999-000-0007",
                password_hash=get_password_hash("mgr123"),
                is_active=True,
            ),
        ]
        db.add_all(users)
        await db.flush()
        print(f"✓ Created {len(users)} users")

        # ─── Equipment ──────────────────────────────────────────────────────
        equipment_list = [
            Equipment(
                name="Токарный станок ТВ-320",
                inventory_number="EQ-001",
                equipment_type="Металлообрабатывающее",
                location="Цех №1, участок А",
                department="Производство",
                manufacturer="ОАО СТАНКОМАШ",
                model="ТВ-320",
                year_of_manufacture=2018,
                status=EquipmentStatus.OPERATIONAL,
            ),
            Equipment(
                name="Фрезерный станок ФС-500",
                inventory_number="EQ-002",
                equipment_type="Металлообрабатывающее",
                location="Цех №1, участок Б",
                department="Производство",
                manufacturer="СТАН-ИНСТРУМЕНТ",
                model="ФС-500",
                year_of_manufacture=2019,
                status=EquipmentStatus.OPERATIONAL,
            ),
            Equipment(
                name="Компрессор КМ-7500",
                inventory_number="EQ-003",
                equipment_type="Компрессорное",
                location="Компрессорная станция",
                department="Энергетика",
                manufacturer="Компрессормаш",
                model="КМ-7500",
                year_of_manufacture=2015,
                status=EquipmentStatus.UNDER_MAINTENANCE,
            ),
            Equipment(
                name="Мостовой кран МК-5",
                inventory_number="EQ-004",
                equipment_type="Подъёмно-транспортное",
                location="Цех №2",
                department="Производство",
                manufacturer="Кранстрой",
                model="МК-5",
                year_of_manufacture=2012,
                status=EquipmentStatus.BROKEN,
            ),
            Equipment(
                name="Сварочный агрегат СА-200",
                inventory_number="EQ-005",
                equipment_type="Сварочное",
                location="Сварочный пост №3",
                department="Сборочный цех",
                manufacturer="ЭлектроСвар",
                model="СА-200",
                year_of_manufacture=2020,
                status=EquipmentStatus.OPERATIONAL,
            ),
        ]
        db.add_all(equipment_list)
        await db.flush()
        print(f"✓ Created {len(equipment_list)} equipment items")

        # ─── Equipment Norms ────────────────────────────────────────────────
        norms = [
            # Токарный станок
            EquipmentNorm(
                equipment_id=equipment_list[0].id,
                norm_type="weekly",
                interval_days=7,
                description="Еженедельное смазывание направляющих",
                is_active=True,
            ),
            EquipmentNorm(
                equipment_id=equipment_list[0].id,
                norm_type="monthly",
                interval_days=30,
                description="Ежемесячная проверка геометрической точности",
                is_active=True,
            ),
            # Компрессор
            EquipmentNorm(
                equipment_id=equipment_list[2].id,
                norm_type="monthly",
                interval_days=30,
                description="Замена масла и фильтров",
                is_active=True,
            ),
            EquipmentNorm(
                equipment_id=equipment_list[2].id,
                norm_type="quarterly",
                interval_days=90,
                description="Техническое обслуживание клапанов",
                is_active=True,
            ),
            # Мостовой кран
            EquipmentNorm(
                equipment_id=equipment_list[3].id,
                norm_type="monthly",
                interval_days=30,
                description="Проверка тормозов и канатов",
                is_active=True,
            ),
        ]
        db.add_all(norms)
        await db.flush()
        print(f"✓ Created {len(norms)} equipment norms")

        # ─── Fault Types ────────────────────────────────────────────────────
        fault_types = [
            FaultType(
                name="Механическая неисправность",
                description="Поломка механических узлов и деталей",
                is_active=True,
            ),
            FaultType(
                name="Электрическая неисправность",
                description="Неисправность электрооборудования и цепей",
                is_active=True,
            ),
            FaultType(
                name="Плановое ТО",
                description="Плановое техническое обслуживание по регламенту",
                is_active=True,
            ),
        ]
        db.add_all(fault_types)
        await db.flush()
        print(f"✓ Created {len(fault_types)} fault types")

        # ─── Auxiliary Services ─────────────────────────────────────────────
        services = [
            AuxiliaryService(
                name="Механическая служба",
                description="Ремонт и обслуживание механического оборудования",
                is_active=True,
            ),
            AuxiliaryService(
                name="Электрослужба",
                description="Ремонт электрооборудования и систем",
                is_active=True,
            ),
            AuxiliaryService(
                name="Служба ТО компрессорного оборудования",
                description="Специализированное обслуживание компрессоров",
                is_active=True,
            ),
        ]
        db.add_all(services)
        await db.flush()
        print(f"✓ Created {len(services)} auxiliary services")

        # ─── Routing Rules ───────────────────────────────────────────────────
        routing_rules = [
            RoutingRule(
                service_id=services[0].id,
                equipment_type="Металлообрабатывающее",
                executor_id=users[3].id,  # executor1
                order=1,
                is_active=True,
            ),
            RoutingRule(
                service_id=services[1].id,
                fault_type_id=fault_types[1].id,  # electrical
                executor_id=users[4].id,  # executor2
                order=1,
                is_active=True,
            ),
            RoutingRule(
                service_id=services[2].id,
                equipment_type="Компрессорное",
                executor_id=users[3].id,  # executor1
                order=2,
                is_active=True,
            ),
        ]
        db.add_all(routing_rules)
        await db.flush()
        print(f"✓ Created {len(routing_rules)} routing rules")

        await db.commit()

    print("\n" + "="*60)
    print("ИС ТОиР — Инициализация завершена!")
    print("="*60)
    print("\nУчётные данные:")
    print(f"  Администратор:  admin@toir.ru      / admin123")
    print(f"  ППР-инженер:    ppr@toir.ru         / ppr123")
    print(f"  Диспетчер:      dispatcher@toir.ru  / disp123")
    print(f"  Исполнитель 1:  executor1@toir.ru   / exec123")
    print(f"  Исполнитель 2:  executor2@toir.ru   / exec123")
    print(f"  Нач. смены:     shift@toir.ru       / shift123")
    print(f"  Менеджер:       manager@toir.ru     / mgr123")
    print("\nЗапуск сервера:")
    print("  cd backend && python run.py")
    print("\nAPI документация: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(create_sample_data())
