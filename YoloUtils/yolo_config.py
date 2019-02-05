
class YoloConfig():
    def __init__(self):
        self.model_path = None
        self.anchors_path = None
        self.classes_path = None
        self.iou_threshold = 0.5
        self.score_threshold = 0.1