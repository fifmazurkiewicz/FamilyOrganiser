"""Privacy export and account-erasure API contracts."""

from sqlalchemy import select

from app.models.user import User


class TestPrivacyExport:
    async def test_export_contains_profile_without_credentials(self, client):
        response = await client.get("/users/me/export")

        assert response.status_code == 200
        assert response.headers["content-disposition"].startswith("attachment;")
        body = response.json()
        assert body["account"]["email"] == "test@example.com"
        assert "hashed_password" not in body["account"]
        assert "notifications" in body
        assert "investments" in body


class TestAccountDeletion:
    async def test_delete_anonymises_local_account(self, client, db_session, test_user):
        response = await client.delete("/users/me")

        assert response.status_code == 204
        db_session.expire_all()
        user = await db_session.scalar(select(User).where(User.id == test_user.id))
        assert user is not None
        assert user.full_name == "Usunięty użytkownik"
        assert user.email.endswith("@invalid.local")
        assert user.hashed_password is None
        assert user.is_active is False
        assert user.is_approved is False

    async def test_group_admin_must_transfer_role(self, client, family_group):
        response = await client.delete("/users/me")

        assert response.status_code == 400
        assert "Transfer admin role" in response.json()["detail"]
