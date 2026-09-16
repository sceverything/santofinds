import csv

from santofinds import SantoFindsClient

NAMES = [
    "Example Name; New York, NY",
    "Another Example; Austin, TX",
]


def main() -> None:
    with SantoFindsClient() as client:
        people = client.search(names=NAMES, tier="basic", max_results=5)
        with open("santofinds_contacts.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "age", "address", "phone", "profile_url"])
            for person in client.filter_with_phone(people):
                writer.writerow([
                    person.get("name", ""),
                    person.get("age", ""),
                    person.get("currentAddress") or person.get("address", ""),
                    client.best_phone(person) or "",
                    person.get("profileUrl", ""),
                ])


if __name__ == "__main__":
    main()
