def normalize_payload(items: list[dict]) -> list[dict]:
    return sorted(
        items,
        key=lambda item: item["phone_number"],
    )
