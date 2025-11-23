import logging
from typing import Any, Dict, List

import cv2
import numpy as np
import spacy
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)


class IntelExtractor:
    def __init__(self):
        # Initialize NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy loaded (en_core_web_sm).")
        except Exception as e:
            logger.error(f"Failed to load spaCy: {e}")
            self.nlp = None

        # Initialize OCR
        # use_angle_cls=True enables orientation detection
        # lang='en' for English
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            logger.info("PaddleOCR initialized.")
        except Exception as e:
            logger.error(f"Failed to load PaddleOCR: {e}")
            self.ocr = None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts Named Entities from text using spaCy.
        """
        if not self.nlp or not text:
            return {}

        doc = self.nlp(text)
        entities = {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)

        # Deduplicate
        for k in entities:
            entities[k] = list(set(entities[k]))

        return entities

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extracts all text from an image using PaddleOCR.
        """
        if not self.ocr:
            return ""

        try:
            result = self.ocr.ocr(image_path, cls=True)
            if not result or not result[0]:
                return ""

            # Result structure: [[[[points], (text, conf)], ...]]
            full_text = []
            for line in result[0]:
                text, conf = line[1]
                if conf > 0.6:  # Confidence threshold
                    full_text.append(text)

            return " ".join(full_text)
        except Exception as e:
            logger.error(f"OCR failed on {image_path}: {e}")
            return ""
