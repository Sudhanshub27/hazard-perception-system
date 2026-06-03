import uuid

def calculate_iou(box1: list[float], box2: list[float]) -> float:
    """
    Computes Intersection-over-Union (IoU) of two bounding boxes.
    Boxes format: [x1, y1, x2, y2]
    """
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union_area = area_box1 + area_box2 - intersection_area
    if union_area <= 0.0:
        return 0.0
        
    return intersection_area / union_area


class Track:
    def __init__(self, track_id: int, bbox: list[float], class_name: str, confidence: float):
        self.track_id = track_id
        self.bbox = bbox
        self.class_name = class_name
        self.confidence = confidence
        self.lost_count = 0  # Number of frames this object has been missing


class IoUTracker:
    def __init__(self, iou_threshold: float = 0.3, max_lost_frames: int = 5):
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self.next_track_id = 1
        self.active_tracks: list[Track] = []

    def update(self, detections: list[dict]) -> list[dict]:
        """
        Match current detections to existing tracks.
        Assigns 'track_id' to each detection dict.
        """
        matched_detections = []
        
        # Keep track of which active tracks and new detections get matched
        used_tracks = set()
        matched_dets_indices = set()

        # Step 1: Find best matches by IoU (greedy matching)
        # Sort by confidence so higher confidence detections match first
        det_indices_sorted = sorted(range(len(detections)), key=lambda idx: detections[idx].get("confidence", 0.0), reverse=True)

        for det_idx in det_indices_sorted:
            det = detections[det_idx]
            det_box = det["bbox"]
            det_class = det["class_name"]

            best_track_idx = -1
            best_iou = -1.0

            for t_idx, track in enumerate(self.active_tracks):
                if t_idx in used_tracks:
                    continue
                # Require class match to prevent ID switching between cars/pedestrians
                if track.class_name != det_class:
                    continue

                iou = calculate_iou(track.bbox, det_box)
                if iou > best_iou:
                    best_iou = iou
                    best_track_idx = t_idx

            if best_iou >= self.iou_threshold and best_track_idx != -1:
                # We have a match! Update track credentials
                track = self.active_tracks[best_track_idx]
                track.bbox = det_box
                track.confidence = det.get("confidence", 0.0)
                track.lost_count = 0
                
                det["track_id"] = track.track_id
                used_tracks.add(best_track_idx)
                matched_dets_indices.add(det_idx)

        # Step 2: Handle unmatched active tracks (increment lost count)
        remaining_tracks = []
        for t_idx, track in enumerate(self.active_tracks):
            if t_idx not in used_tracks:
                track.lost_count += 1
                
            # Retain the track if it hasn't exceeded max_lost_frames limit
            if track.lost_count <= self.max_lost_frames:
                remaining_tracks.append(track)
                
        self.active_tracks = remaining_tracks

        # Step 3: Handle unmatched detections (spawn new tracks)
        for det_idx, det in enumerate(detections):
            if det_idx not in matched_dets_indices:
                track_id = self.next_track_id
                self.next_track_id += 1
                
                new_track = Track(
                    track_id=track_id,
                    bbox=det["bbox"],
                    class_name=det["class_name"],
                    confidence=det.get("confidence", 0.0)
                )
                self.active_tracks.append(new_track)
                det["track_id"] = track_id

        return detections
