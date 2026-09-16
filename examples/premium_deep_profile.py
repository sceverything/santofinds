from santofinds import SantoFindsClient


def main() -> None:
    with SantoFindsClient() as client:
        people = client.search_by_name("Example Name", tier="premium", max_results=3)
        for person in people:
            print(person)


if __name__ == "__main__":
    main()
