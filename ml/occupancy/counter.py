from dataclasses import dataclass


@dataclass
class OccupancyResult:
    people_count: int
    room_capacity: int
    occupancy_ratio: float
    occupancy_percent: float
    crowding: bool


def calculate_occupancy(
    people_count: int,
    room_capacity: int,
) -> OccupancyResult:
    if people_count < 0:
        raise ValueError(
            "people_count cannot be negative"
        )

    if room_capacity <= 0:
        raise ValueError(
            "room_capacity must be greater than zero"
        )

    occupancy_ratio = people_count / room_capacity

    return OccupancyResult(
        people_count=people_count,
        room_capacity=room_capacity,
        occupancy_ratio=occupancy_ratio,
        occupancy_percent=occupancy_ratio * 100,
        crowding=people_count > room_capacity,
    )