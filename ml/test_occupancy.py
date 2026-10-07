from pathlib import Path

from PIL import Image

from occupancy.analyzer import OccupancyAnalyzer


IMAGE_PATH = Path(
    "data/test_images/test.jpg"
)


def main() -> None:
    image = Image.open(
        IMAGE_PATH
    ).convert("RGB")

    analyzer = OccupancyAnalyzer()

    result = analyzer.analyze(
        image,
        room_capacity=60,
    )

    print(
        f"People detected: "
        f"{result['people_count']}"
    )

    print(
        f"Room capacity: "
        f"{result['room_capacity']}"
    )

    print(
        f"Occupancy: "
        f"{result['occupancy_percent']:.2f}%"
    )

    print(
        f"Crowding: "
        f"{result['crowding']}"
    )

    print(
        f"Device: "
        f"{result['device']}"
    )


if __name__ == "__main__":
    main()