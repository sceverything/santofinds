SantoFinds

SantoFinds is a Python client for people-search and public-record lookup services.

It provides a simple interface for searching by name, phone number, or address while keeping the underlying response available for developers who need structured data.

Features

- Name search
- Reverse phone lookup
- Address lookup
- Multiple search inputs
- Basic and premium lookup tiers
- Phone and email filtering
- Minimum-age filtering
- State filtering
- Best-phone selection
- Cost estimation
- Context-manager support
- Structured Python results
- Apify-backed lookup support

Installation

pip install -e .

Configuration

Set your Apify API token in the environment:

export APIFY_API_TOKEN="your_apify_api_token"

Do not commit API tokens or other secrets to the repository.

Basic Usage

from santofinds import SantoFindsClient

with SantoFindsClient() as client:
    people = client.search_by_name("Michael Johnson", tier="basic")

    for person in people:
        print(person["name"])

Search by Name

from santofinds import SantoFindsClient

with SantoFindsClient() as client:
    results = client.search_by_name(
        "Michael Johnson",
        tier="basic",
        max_results=5,
    )

    for person in results:
        print(person)

Search by Phone

from santofinds import SantoFindsClient

with SantoFindsClient() as client:
    results = client.search_by_phone(
        "+1-555-555-5555",
        tier="basic",
    )

    for person in results:
        print(person)

Search by Address

from santofinds import SantoFindsClient

with SantoFindsClient() as client:
    results = client.search_by_address(
        "123 Main St, Example City, CA 90000",
        tier="basic",
    )

    for person in results:
        print(person)

Filtering Results

with SantoFindsClient() as client:
    results = client.search_by_name("Michael Johnson")

    results = client.filter_with_phone(results)
    results = client.filter_with_email(results)
    results = client.filter_by_min_age(results, 18)
    results = client.filter_by_state(results, "SC")

Selecting a Phone Number

with SantoFindsClient() as client:
    results = client.search_by_name("Michael Johnson")

    if results:
        phone = client.best_phone(results[0])
        print(phone)

Cost Estimation

from santofinds import SantoFindsClient

with SantoFindsClient() as client:
    estimated_cost = client.estimate_cost(
        expected_results=100,
        tier="basic",
    )

    print(estimated_cost)

Cost estimates are provided by SantoFinds for planning purposes and should not be treated as a current quote from the external lookup provider.

API

"search()"

General-purpose search supporting names, addresses, and phone numbers.

"search_by_name()"

Search by one or more names.

"search_by_phone()"

Search by one or more phone numbers.

"search_by_address()"

Search by one or more addresses.

"filter_with_phone()"

Keep results containing phone information.

"filter_with_email()"

Keep results containing email information.

"filter_by_min_age()"

Keep results meeting a minimum age.

"filter_by_state()"

Keep results associated with a specified state.

"best_phone()"

Return the preferred phone number from a result.

"estimate_cost()"

Estimate lookup cost from an expected number of results.

Data Handling

Returned information may contain public-record data and may be incomplete, outdated, or inaccurate.

Use SantoFinds and any returned information only for lawful purposes and in accordance with applicable laws, regulations, and the terms governing the underlying data source.

Do not use returned information for stalking, harassment, discrimination, fraud, or other unlawful activity.

Returned information must not be used to make decisions regulated by the Fair Credit Reporting Act.

Attribution

SantoFinds is a modified derivative of MIT-licensed software originally published by ApiVault Labs.

The original MIT license and copyright notice are retained in "LICENSE".

The current lookup functionality uses an external Apify actor as its backend.

License

SantoFinds is released under the MIT License.

See "LICENSE" for the complete license text.
