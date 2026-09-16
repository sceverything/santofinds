from santofinds import SantoFindsClient


def main() -> None:
    with SantoFindsClient() as client:
        people = client.search_by_address("Example Street; New York, NY 10001", tier="basic", max_results=10)
        for person in people:
            print(person.get("name"), client.best_phone(person))


if __name__ == "__main__":
    main()
