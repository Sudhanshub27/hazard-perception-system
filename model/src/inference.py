import numpy as np
import cv2
import onnxruntime as ort
import ast

# Only allow driving-relevant classes through inference.
# This filters out irrelevant COCO classes (e.g., "cell phone", "pizza")
# when running with a generic pretrained model instead of a BDD100K fine-tuned one.
ALLOWED_CLASSES = {
    "person", "bicycle", "car", "motorcycle", "bus", "train", "truck",
    "traffic light", "traffic sign", "stop sign", "fire hydrant",
    "rider",  # BDD100K specific
}

class YOLOInference:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.session = None
        self.is_loaded = False
        self.names = {}

    def load(self):
        print(f"Loading YOLO ONNX model from {self.model_path} via ONNX Runtime...")
        try:
            # CPU Execution Provider is standard for this setup.
            # CUDAExecutionProvider can be added if GPU hardware is available.
            self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
            
            # Extract metadata class names dynamically from the ONNX model map
            metadata = self.session.get_modelmeta().custom_metadata_map
            if 'names' in metadata:
                try:
                    self.names = {int(k): v for k, v in ast.literal_eval(metadata['names']).items()}
                except Exception as parse_err:
                    print(f"Warning: Failed to parse model metadata names: {parse_err}")
            
            # Fallback to BDD100K class names if not found
            if not self.names:
                self.names = {
                    0: "car", 1: "truck", 2: "bus", 3: "person", 4: "rider",
                    5: "bicycle", 6: "motorcycle", 7: "traffic light", 8: "traffic sign", 9: "train"
                }

            self.is_loaded = True
            print(f"[SUCCESS] ONNX Model loaded! Classes loaded: {len(self.names)}")
            print(f"   Class map: {self.names}")
        except Exception as e:
            print(f"CRITICAL: Failed to load ONNX model at {self.model_path}: {e}")
            self.is_loaded = False

    def infer(self, frame: np.ndarray) -> list[dict]:
        if not self.is_loaded or self.session is None:
            return []

        h, w = frame.shape[:2]
        
        # 1. Preprocessing: Resize to 640x640, convert to RGB, normalize, transpose to CHW, expand to batch dimension
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 640))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)

        # 2. Run session
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        
        outputs = self.session.run([output_name], {input_name: img})
        output = outputs[0]  # Shape: (1, 4 + N, 8400) or similar
        
        if len(output.shape) == 3:
            output = output[0]  # Squeeze batch dimension to get (4 + N, 8400)

        # 3. Postprocessing: Decode bounding boxes and apply Non-Maximum Suppression (NMS)
        # Transpose output to make it (8400, 4 + N) for row-by-row iteration
        output = output.T

        boxes = []
        confidences = []
        class_ids = []
        
        conf_threshold = 0.45  # Raised from 0.35 to reduce false positives with generic models
        iou_threshold = 0.45

        # Class confidence scores start from index 4 onwards
        scores = output[:, 4:]
        max_scores = np.max(scores, axis=1)
        max_class_ids = np.argmax(scores, axis=1)

        # Filter boxes meeting the confidence threshold
        conf_mask = max_scores >= conf_threshold
        filtered_scores = max_scores[conf_mask]
        filtered_class_ids = max_class_ids[conf_mask]
        filtered_boxes = output[conf_mask, :4]

        # Convert YOLO center x, center y, width, height format to top-left x, y, width, height in 640x640 scale
        for box in filtered_boxes:
            cx, cy, box_w, box_h = box
            x = cx - box_w / 2.0
            y = cy - box_h / 2.0
            boxes.append([float(x), float(y), float(box_w), float(box_h)])
            
        confidences = filtered_scores.tolist()
        class_ids = filtered_class_ids.tolist()

        # Execute fast OpenCV DNN Non-Maximum Suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, iou_threshold)
        
        detections = []
        if len(indices) > 0:
            for idx in indices.flatten():
                x, y, box_w, box_h = boxes[idx]
                
                # Clamp coordinates to the 640x640 image frame
                x1 = max(0.0, x)
                y1 = max(0.0, y)
                x2 = min(640.0, x + box_w)
                y2 = min(640.0, y + box_h)
                
                class_id = class_ids[idx]
                class_name = self.names.get(class_id, f"object_{class_id}")
                
                # Filter: only allow driving-relevant classes
                if class_name not in ALLOWED_CLASSES:
                    continue
                
                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": float(confidences[idx]),
                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                })

        return detections
