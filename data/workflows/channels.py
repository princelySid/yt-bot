from datetime import datetime, timezone

from yt_bot.services import CSVService


def _with_category(rows: list[dict], category: str) -> list[dict]:
    for row in rows:
        row["category"] = category
    return rows


def _merge_channel_lists(
    uncategorised: list[dict],
    music: list[dict],
    others: list[dict],
) -> list[dict]:
    uncategorised_ids = {row["channel_id"] for row in uncategorised}
    remaining = [row for row in others if row["channel_id"] not in uncategorised_ids]

    all_uncategorised = _with_category(uncategorised + remaining, "uncategorised")
    music_rows = _with_category(music, "music")
    music_ids = {row["channel_id"] for row in music_rows}

    non_music = [
        row for row in all_uncategorised if row["channel_id"] not in music_ids
    ]
    return music_rows + non_music


def _stamp_rows(rows: list[dict], now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    for row in rows:
        row["created_at"] = now
        row["updated_at"] = now
    return rows


def load_channels_from_csv(
    uncategorised_csv_path: str,
    music_csv_path: str,
    others_csv_path: str,
) -> tuple[list[dict], list[dict], list[dict]]:
    uncategorised = CSVService.read_csv_list_dict(uncategorised_csv_path)
    music = CSVService.read_csv_list_dict(music_csv_path)
    others = CSVService.read_csv_list_dict(others_csv_path)
    return uncategorised, music, others


def prepare_channel_seed_rows(
    uncategorised: list[dict],
    music: list[dict],
    others: list[dict],
) -> list[dict]:
    merged = _merge_channel_lists(uncategorised, music, others)
    return _stamp_rows(merged)

