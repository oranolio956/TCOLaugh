import hashlib
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None

try:
    import mediapipe as mp  # type: ignore

    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available. Using Mock Face Detection.")


class FaceEngine:
    def __init__(self):
        if MEDIAPIPE_AVAILABLE and cv2 is not None:
            self.mp_face_detection = mp.solutions.face_detection
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 0 for close faces, 1 for far faces
                min_detection_confidence=0.5,
            )
        else:
            self.detector = None
        print("FaceEngine initialized.")

    def detect_faces(self, image: np.ndarray) -> List[Any]:
        if not MEDIAPIPE_AVAILABLE or cv2 is None:

            class MockDetection:
                def __init__(self):
                    self.score = [0.99]

            return [MockDetection()]

        results = self.detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.detections:
            return []
        return results.detections

    def get_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Generates a deterministic 512-dim embedding based on image content hash.
        This ensures that searching for the same image returns the same vector.
        """
        if cv2 is not None:
            resized = cv2.resize(face_crop, (64, 64))
            buffer = resized.tobytes()
        else:
            buffer = face_crop.tobytes()

        img_hash = hashlib.md5(buffer).hexdigest()

        # 3. Seed random generator with this hash
        seed = int(img_hash, 16) % (2**32)
        np.random.seed(seed)

        # 4. Generate Vector
        embedding = np.random.rand(512).astype("float32")

        # 5. Normalize
        norm = np.linalg.norm(embedding)
        return embedding / norm

    def process_image(self, image_path: str) -> List[Dict[str, Any]]:
        image = None
        if cv2 is not None:
            image = cv2.imread(image_path)
        if image is None:
            image = np.zeros((100, 100, 3), dtype=np.uint8)

        detections = self.detect_faces(image)
        results = []

        for detection in detections:
            # In real app, we crop here. For mock, we use full image as crop
            vector = self.get_embedding(image)

            results.append(
                {"detection_score": detection.score[0], "embedding": vector.tolist()}
            )

        return results
