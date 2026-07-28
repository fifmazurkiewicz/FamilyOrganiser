"""Integration tests for Family Groups API."""

from app.api.deps import get_current_user


class TestFamilyGroupsAPI:
    async def test_create_and_list_groups(self, client, client_auth_headers):
        create = await client.post(
            "/groups/",
            json={"name": "Rodzina Test"},
            headers=client_auth_headers,
        )
        assert create.status_code == 201
        body = create.json()
        assert body["name"] == "Rodzina Test"
        assert body["member_count"] == 1

        listed = await client.get("/groups/", headers=client_auth_headers)
        assert listed.status_code == 200
        assert any(g["id"] == body["id"] for g in listed.json())

    async def test_invitation_and_join_flow(
        self, client, client_auth_headers, app_with_overrides, test_user, test_user2
    ):
        created = await client.post(
            "/groups/",
            json={"name": "Zaproszenie API"},
            headers=client_auth_headers,
        )
        assert created.status_code == 201
        group_id = created.json()["id"]

        invite = await client.post(
            f"/groups/{group_id}/invitations",
            json={"single_use": True, "expire_days": 7},
            headers=client_auth_headers,
        )
        assert invite.status_code == 201
        token = invite.json()["token"]
        assert token

        async def as_user2():
            return test_user2

        app_with_overrides.dependency_overrides[get_current_user] = as_user2
        try:
            join = await client.post(f"/groups/join/{token}", headers=client_auth_headers)
            assert join.status_code == 200
            assert "Zaproszenie API" in join.json()["message"]
        finally:
            async def as_user1():
                return test_user

            app_with_overrides.dependency_overrides[get_current_user] = as_user1

    async def test_join_invalid_token(self, client, client_auth_headers):
        resp = await client.post(
            "/groups/join/bad-token",
            headers=client_auth_headers,
        )
        assert resp.status_code == 404

    async def test_revoke_invitation(self, client, client_auth_headers):
        created = await client.post(
            "/groups/",
            json={"name": "Revoke API"},
            headers=client_auth_headers,
        )
        group_id = created.json()["id"]

        invite = await client.post(
            f"/groups/{group_id}/invitations",
            json={"single_use": True, "expire_days": 7},
            headers=client_auth_headers,
        )
        link_id = invite.json()["id"]

        revoke = await client.delete(
            f"/groups/{group_id}/invitations/{link_id}",
            headers=client_auth_headers,
        )
        assert revoke.status_code == 204

        join = await client.post(
            f"/groups/join/{invite.json()['token']}",
            headers=client_auth_headers,
        )
        assert join.status_code == 400
