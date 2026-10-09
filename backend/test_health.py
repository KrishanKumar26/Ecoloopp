"""
Quick health check test for EcoLoop backend.
Tests API endpoints and basic database operations.
"""

import asyncio
import sys
from sqlalchemy import select, text
from database import init_db, engine, async_session_maker
from models import User, UserRole


async def test_database_operations():
    """Test basic database operations with SQLAlchemy models."""
    print("\n🧪 Testing Database Operations...")

    try:
        # Initialize database
        init_db()

        # Import engine after initialization
        from database import engine as db_engine
        print("✓ Database engine initialized")

        # Test raw SQL query
        async with db_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            assert row[0] == 1
            print("✓ Raw SQL query successful")

        # Test enum types exist
        async with db_engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT typname FROM pg_type WHERE typname IN ('userrole', 'pickupstatus')"
            ))
            types = [row[0] for row in result.fetchall()]
            assert 'userrole' in types
            assert 'pickupstatus' in types
            print(f"✓ PostgreSQL enum types found: {types}")

        # Test enum values
        async with db_engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT enumlabel FROM pg_enum "
                "WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole') "
                "ORDER BY enumlabel"
            ))
            user_roles = [row[0] for row in result.fetchall()]
            assert user_roles == ['admin', 'collector', 'user']
            print(f"✓ UserRole enum values correct: {user_roles}")

            result = await conn.execute(text(
                "SELECT enumlabel FROM pg_enum "
                "WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'pickupstatus') "
                "ORDER BY enumlabel"
            ))
            pickup_statuses = [row[0] for row in result.fetchall()]
            assert set(pickup_statuses) == {'pending', 'accepted', 'in_transit', 'completed', 'cancelled'}
            print(f"✓ PickupStatus enum values correct: {pickup_statuses}")

        # Test table count
        async with db_engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
                "AND table_name != 'alembic_version'"
            ))
            table_count = result.scalar()
            assert table_count == 6
            print(f"✓ Database has {table_count} tables (expected 6)")

        # Test User model Python enum values
        assert UserRole.USER.value == 'user'
        assert UserRole.COLLECTOR.value == 'collector'
        assert UserRole.ADMIN.value == 'admin'
        print("✓ Python UserRole enum values match lowercase specification")

        print("\n✅ All database tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test API endpoints using requests."""
    print("\n🧪 Testing API Endpoints...")

    try:
        import requests

        # Test root endpoint
        response = requests.get("http://127.0.0.1:8000/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        print("✓ GET / - API root endpoint working")

        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ GET /health - Health check endpoint working")

        # Test database health endpoint
        response = requests.get("http://127.0.0.1:8000/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["connected"] is True
        assert data["database"]["database"] == "ecoloop_dev"
        print("✓ GET /health/db - Database health endpoint working")
        print(f"  Connected to: {data['database']['database']} @ {data['database']['host']}")

        print("\n✅ All API endpoint tests passed!")
        return True

    except ImportError:
        print("⚠️  requests library not installed, skipping API tests")
        print("   Install with: pip install requests")
        return True
    except Exception as e:
        print(f"\n❌ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("EcoLoop Backend Health Check")
    print("=" * 60)

    # Test database operations
    db_passed = await test_database_operations()

    # Test API endpoints
    api_passed = await test_api_endpoints()

    # Summary
    print("\n" + "=" * 60)
    if db_passed and api_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
