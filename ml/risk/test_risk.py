from risk.features import RiskFeatures
from risk.model import IncidentRiskPredictor
from risk.training import generate_dataset



def main() -> None:
    samples, labels = generate_dataset()

    predictor = IncidentRiskPredictor()

    predictor.fit(
        samples,
        labels,
    )

    normal_state = RiskFeatures(
        current_occupancy=0.55,
        event_size=100,
        time_remaining_minutes=120,
        vendor_reliability=0.95,
        staff_availability=0.95,
        equipment_status=1.0,
        historical_incidents=0,
    )

    dangerous_state = RiskFeatures(
        current_occupancy=1.15,
        event_size=450,
        time_remaining_minutes=20,
        vendor_reliability=0.55,
        staff_availability=0.60,
        equipment_status=0.50,
        historical_incidents=4,
    )

    print("Normal state:")
    print(
        predictor.predict(
            normal_state
        )
    )

    print()

    print("Dangerous state:")
    print(
        predictor.predict(
            dangerous_state
        )
    )


if __name__ == "__main__":
    main()