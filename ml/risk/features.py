from dataclasses import dataclass


@dataclass
class RiskFeatures:
    current_occupancy: float
    event_size: float
    time_remaining_minutes: float
    vendor_reliability: float
    staff_availability: float
    equipment_status: float
    historical_incidents: float

    def to_vector(self) -> list[float]:
        return [
            self.current_occupancy,
            self.event_size,
            self.time_remaining_minutes,
            self.vendor_reliability,
            self.staff_availability,
            self.equipment_status,
            self.historical_incidents,
        ]