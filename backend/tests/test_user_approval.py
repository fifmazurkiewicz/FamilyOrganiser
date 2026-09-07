"""User approval gate: /me stays open; feature APIs 403 until approved."""

import uuid

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.services.user_provisioning import get_or_create_user_from_claims


async def _as_user(user: User):
    async def override():
        return user

    return override


class TestMeAllowsUnapproved:
    async def test_me_returns_is_approved_false(
        self, client, app_with_overrides, db_session
    ):
        pending = User(
            email="pending@example.com",
            hashed_password="hashed",
            full_name="Pending User",
            is_approved=False,
        )
        db_session.add(pending)
        await db_session.flush()
        app_with_overrides.dependency_overrides[get_current_user] = await _as_user(
            pending
        )

        resp = await client.get("/users/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "pending@example.com"
        assert body["is_approved"] is False


class TestFeatureApisRequireApproval:
    async def test_groups_list_forbidden_when_unapproved(
        self, client, app_with_overrides, db_session
    ):
        pending = User(
            email="pending-groups@example.com",
            hashed_password="hashed",
            full_name="Pending Groups",
            is_approved=False,
        )
        db_session.add(pending)
        await db_session.flush()
        app_with_overrides.dependency_overrides[get_current_user] = await _as_user(
            pending
        )

        resp = await client.get("/groups/")
        assert resp.status_code == 403
        assert resp.json()["detail"] == "account_pending_approval"

    async def test_notifications_forbidden_when_unapproved(
        self, client, app_with_overrides, db_session
    ):
        pending = User(
            email="pending-notif@example.com",
            hashed_password="hashed",
            full_name="Pending Notif",
            is_approved=False,
        )
        db_session.add(pending)
        await db_session.flush()
        app_with_overrides.dependency_overrides[get_current_user] = await _as_user(
            pending
        )

        resp = await client.get("/notifications/")
        assert resp.status_code == 403
        assert resp.json()["detail"] == "account_pending_approval"

    async def test_approved_user_can_list_groups(self, client, client_auth_headers):
        resp = await client.get("/groups/", headers=client_auth_headers)
        assert resp.status_code == 200


class TestProvisioningApproval:
    async def test_new_user_is_not_approved(self, db_session):
        user = await get_or_create_user_from_claims(
            db_session,
            {
                "sub": str(uuid.uuid4()),
                "email": "newcomer@example.com",
                "user_metadata": {"full_name": "New Comer"},
            },
        )
        assert user is not None
        assert user.is_approved is False
        assert user.is_app_admin is False

    async def test_admin_allowlist_auto_approved_on_insert(self, db_session):
        user = await get_or_create_user_from_claims(
            db_session,
            {
                "sub": str(uuid.uuid4()),
                "email": settings.ADMIN_EMAIL,
                "user_metadata": {"full_name": "Allowlist Admin"},
            },
        )
        assert user is not None
        assert user.is_app_admin is True
        assert user.is_approved is True

    async def test_allowlist_does_not_approve_existing_user(self, db_session):
        existing = User(
            email=settings.ADMIN_EMAIL.lower(),
            hashed_password="hashed",
            full_name="Existing",
            is_app_admin=False,
            is_approved=False,
            supabase_auth_id=uuid.uuid4(),
        )
        db_session.add(existing)
        await db_session.flush()

        user = await get_or_create_user_from_claims(
            db_session,
            {
                "sub": str(existing.supabase_auth_id),
                "email": settings.ADMIN_EMAIL,
            },
        )
        assert user is not None
        assert user.id == existing.id
        assert user.is_approved is False


class TestAdminApproveRevoke:
    async def test_admin_can_approve_and_revoke(
        self, client, app_with_overrides, admin_user, db_session
    ):
        pending = User(
            email="to-approve@example.com",
            hashed_password="hashed",
            full_name="To Approve",
            is_approved=False,
        )
        db_session.add(pending)
        await db_session.flush()
        app_with_overrides.dependency_overrides[get_current_user] = await _as_user(
            admin_user
        )

        approve = await client.post(f"/users/{pending.id}/approve")
        assert approve.status_code == 200
        await db_session.refresh(pending)
        assert pending.is_approved is True

        revoke = await client.post(f"/users/{pending.id}/revoke")
        assert revoke.status_code == 200
        await db_session.refresh(pending)
        assert pending.is_approved is False

    async def test_admin_cannot_revoke_self(
        self, client, app_with_overrides, admin_user, db_session
    ):
        app_with_overrides.dependency_overrides[get_current_user] = await _as_user(
            admin_user
        )

        resp = await client.post(f"/users/{admin_user.id}/revoke")
        assert resp.status_code == 400
        await db_session.refresh(admin_user)
        assert admin_user.is_approved is True
