"""
ONNX Runtime Inference Wrapper for YOLO26
Loads the exported best.onnx graph and performs CPU/GPU inference.
"""
import onnxruntime as ort
import numpy as np
import cv2

CLASS_NAMES = [
    "car", "truck", "bus", "person", "rider",
    "bicycle", "motorcycle", "traffic light", "traffic sign", "train"
]

class YOLOInference:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.is_loaded = False
        
        # We attempt to use CUDA (GPU) first, falling back to CPU seamlessly
        self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

    def load(self):
        print(f"Loading ONNX model from {self.model_path} via ONNXRuntime...")
        try:
            self.session = ort.InferenceSession(self.model_path, providers=self.providers)
            self.input_name = self.session.get_inputs()[0].name
            self.is_loaded = True
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load ONNX model: {e}")
            self.is_loaded = False

    def infer(self, frame: np.ndarray) -> list[dict]:
        """
        Runs the frame through ONNX runtime and parses YOLO's raw [1, 14, 8400] output array 
        into our readable Detection schema format.
        """
        if not self.is_loaded:
            return []

        # YOLO expects RGB, 640x640, Normalized to [0,1], CHW format
        original_h, original_w = frame.shape[:2]
        
        # 1. PRE-PROCESS
        resized = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = img.transpose((2, 0, 1)) # HWC to CHW
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0) # Add batch dimension -> (1, 3, 640, 640)

        # 2. INFERENCE
        outputs = self.session.run(None, {self.input_name: img})
        output = outputs[0] # Shape: (batch=1, classes+boxes=14, anchors=8400)
        
        # 3. POST-PROCESS
        # We need to filter and map coordinates back to full image size
        detections = []
        
        # Transpose output to (8400, 14) so each row is a prediction
        preds = output[0].T 
        
        for pred in preds:
            # pred formatting: [px, py, w, h, class0_conf, class1_conf, ..., class9_conf]
            box = pred[0:4]
            scores = pred[4:]
            
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])
            
            # Confidence thresholding (e.g. 0.4)
            if confidence > 0.4:
                # box is [x_center, y_center, width, height] mapped to 640x640
                xc, yc, w, h = box
                
                # Rescale coordinates to original image dimensions
                x1 = (xc - w/2) * (original_w / 640.0)
                y1 = (yc - h/2) * (original_h / 640.0)
                x2 = (xc + w/2) * (original_w / 640.0)
                y2 = (yc + h/2) * (original_h / 640.0)
                
                detections.append({
                    "class_id": class_id,
                    "class_name": CLASS_NAMES[class_id],
                    "confidence": confidence,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                })

        # Future: apply Non-Maximum Suppression (NMS) here to remove overlapping boxes
        # (YOLOv8 ONNX often requires manual NMS if not baked into the export graph.)
        return detections
