from santofinds import SantoFindsClient


def main() -> None:
    with SantoFindsClient() as client:
        people = client.search_by_phone("+1 212 555 0100", tier="basic", max_results=5)
        for person in people:
            print(person.get("name"), person.get("currentAddress"))
            print(client.best_phone(person))


if __name__ == "__main__":
    main()
