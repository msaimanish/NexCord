from occupancy.counter import (
    OccupancyResult,
    calculate_occupancy,
)
from occupancy.detector import PersonDetector


class OccupancyAnalyzer:
    def __init__(
        self,
        detector: PersonDetector | None = None,
    ):
        self.detector = detector or PersonDetector()

    def analyze(
        self,
        image,
        room_capacity: int,
    ) -> dict:
        detection = self.detector.detect(image)

        occupancy: OccupancyResult = calculate_occupancy(
            people_count=detection["count"],
            room_capacity=room_capacity,
        )

        return {
            "people_count": occupancy.people_count,
            "room_capacity": occupancy.room_capacity,
            "occupancy_ratio": occupancy.occupancy_ratio,
            "occupancy_percent": occupancy.occupancy_percent,
            "crowding": occupancy.crowding,
            "detections": {
                "boxes": detection["boxes"],
                "scores": detection["scores"],
            },
            "device": str(self.detector.device),
        }