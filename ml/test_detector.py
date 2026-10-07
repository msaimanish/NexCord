from pathlib import Path

from PIL import Image

from occupancy.detector import PersonDetector


IMAGE_PATH = Path("data/test_images/test.jpg")


def main() -> None:
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Image not found: {IMAGE_PATH}"
        )

    image = Image.open(
        IMAGE_PATH
    ).convert("RGB")

    detector = PersonDetector()

    result = detector.detect(image)

    print(
        f"Detected people: {result['count']}"
    )

    print(
        f"Device: {detector.device}"
    )


if __name__ == "__main__":
    main()