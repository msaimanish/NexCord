import torch

from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn_v2,
    FasterRCNN_ResNet50_FPN_V2_Weights,
)


class PersonDetector:
    def __init__(
        self,
        device: str | None = None,
    ):
        if device is None:
            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        self.device = torch.device(device)

        self.weights = (
            FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        )

        self.model = fasterrcnn_resnet50_fpn_v2(
            weights=self.weights,
            box_score_thresh=0.7,
        )

        self.model.to(self.device)
        self.model.eval()

        self.transforms = self.weights.transforms()

        self.person_class_id = 1

    def detect(
        self,
        image,
    ) -> dict:
        tensor = self.transforms(
            image
        ).to(self.device)

        with torch.inference_mode():
            prediction = self.model(
                [tensor]
            )[0]

        labels = prediction["labels"]
        scores = prediction["scores"]
        boxes = prediction["boxes"]

        person_mask = labels == self.person_class_id

        person_scores = scores[person_mask]
        person_boxes = boxes[person_mask]

        return {
            "count": int(person_mask.sum().item()),
            "boxes": person_boxes.cpu().tolist(),
            "scores": person_scores.cpu().tolist(),
        }