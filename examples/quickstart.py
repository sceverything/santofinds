from santofinds import SantoFindsClient


def main() -> None:
    with SantoFindsClient() as client:
        people = client.search_by_name("Example Name", tier="basic", max_results=5)
        print(f"Found {len(people)} matches")
        for person in people:
            print(person.get("name"))
            print(person.get("currentAddress") or person.get("address"))
            print(client.best_phone(person))


if __name__ == "__main__":
    main()
