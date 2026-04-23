from fastapi.testclient import TestClient


def test_create_lead(client: TestClient) -> None:
    payload = {
        "nombre": "Juan Perez",
        "email": "juan.perez@example.com",
        "telefono": "+573001112244",
        "fuente": "instagram",
        "producto_interes": "Curso premium",
        "presupuesto": 350,
    }

    response = client.post("/leads", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["email"] == payload["email"]
    assert body["fuente"] == payload["fuente"]


def test_duplicate_email_returns_409(client: TestClient) -> None:
    payload = {
        "nombre": "Ana Perez",
        "email": "ana.perez@example.com",
        "fuente": "facebook",
    }

    first = client.post("/leads", json=payload)
    second = client.post("/leads", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "El email ya existe"


def test_list_leads_with_pagination_and_source_filter(client: TestClient) -> None:
    payloads = [
        {
            "nombre": "Lead One",
            "email": "lead.one@example.com",
            "fuente": "instagram",
        },
        {
            "nombre": "Lead Two",
            "email": "lead.two@example.com",
            "fuente": "facebook",
        },
        {
            "nombre": "Lead Three",
            "email": "lead.three@example.com",
            "fuente": "instagram",
        },
    ]

    for payload in payloads:
        response = client.post("/leads", json=payload)
        assert response.status_code == 201

    response = client.get(
        "/leads", params={"page": 1, "limit": 1, "fuente": "instagram"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 1
    assert body["total"] == 2
    assert len(body["items"]) == 1
    assert body["items"][0]["fuente"] == "instagram"


def test_update_lead(client: TestClient) -> None:
    created = client.post(
        "/leads",
        json={
            "nombre": "Carlos Diaz",
            "email": "carlos.diaz@example.com",
            "fuente": "landing_page",
        },
    )
    assert created.status_code == 201
    lead_id = created.json()["id"]

    response = client.patch(
        f"/leads/{lead_id}",
        json={
            "nombre": "Carlos Diaz Actualizado",
            "presupuesto": 999,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == "Carlos Diaz Actualizado"
    assert body["presupuesto"] == "999.00"


def test_soft_delete_lead(client: TestClient) -> None:
    created = client.post(
        "/leads",
        json={
            "nombre": "Elena Lopez",
            "email": "elena.lopez@example.com",
            "fuente": "referido",
        },
    )
    assert created.status_code == 201
    lead_id = created.json()["id"]

    delete_response = client.delete(f"/leads/{lead_id}")
    get_response = client.get(f"/leads/{lead_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_stats(client: TestClient) -> None:
    payloads = [
        {
            "nombre": "Stats One",
            "email": "stats.one@example.com",
            "fuente": "instagram",
            "presupuesto": 100,
        },
        {
            "nombre": "Stats Two",
            "email": "stats.two@example.com",
            "fuente": "facebook",
            "presupuesto": 300,
        },
    ]

    for payload in payloads:
        response = client.post("/leads", json=payload)
        assert response.status_code == 201

    response = client.get("/leads/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["total_leads"] == 2
    assert body["leads_por_fuente"]["instagram"] == 1
    assert body["leads_por_fuente"]["facebook"] == 1
    assert body["promedio_presupuesto"] == "200.00"
    assert body["leads_ultimos_7_dias"] == 2
