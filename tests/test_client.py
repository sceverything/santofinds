from santofinds import SantoFindsClient


def make_client() -> SantoFindsClient:
    return SantoFindsClient(api_token="test-token")


def test_estimate_cost() -> None:
    client = make_client()
    assert client.estimate_cost(1000, "basic") == 7.0
    assert client.estimate_cost(1000, "premium") == 15.0
    client.close()


def test_best_phone() -> None:
    client = make_client()
    assert client.best_phone({"phones": [{"number": "123"}]}) == "123"
    assert client.best_phone({"phone": "456"}) == "456"
    client.close()


def test_filters() -> None:
    client = make_client()
    people = [
        {"name": "A", "age": 40, "currentAddress": "Austin, TX", "phones": ["1"]},
        {"name": "B", "age": 20, "currentAddress": "New York, NY", "emails": ["a@example.test"]},
    ]
    assert len(client.filter_with_phone(people)) == 1
    assert len(client.filter_with_email(people)) == 1
    assert len(client.filter_by_min_age(people, 30)) == 1
    assert len(client.filter_by_state(people, "TX")) == 1
    client.close()
