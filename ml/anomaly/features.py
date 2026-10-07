from dataclasses import dataclass


@dataclass
class OperationalFeatures:
    occupancy_ratio: float
    queue_length: float
    event_delay_minutes: float
    vendor_delay_minutes: float
    equipment_failure_count: float

    def to_vector(self) -> list[float]:
        return [
            self.occupancy_ratio,
            self.queue_length,
            self.event_delay_minutes,
            self.vendor_delay_minutes,
            self.equipment_failure_count,
        ]