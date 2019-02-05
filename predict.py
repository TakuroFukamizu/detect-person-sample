# coding: UTF-8

import os
import sys
import traceback
import numpy as np
import argparse
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import csv
import base64
from io import BytesIO

from YoloUtils import KerasYOLO, YoloConfig
import cv2
import skimage.color

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.float32):
            return float(obj)
        else:
            return super(MyEncoder, self).default(obj)

def predict(yolo: KerasYOLO, config: YoloConfig, image_path: str, image: Image):
    r_boxes = yolo.detect_image(image)
    r_image = yolo.show_bboxs(image, r_boxes)
    return r_boxes, r_image


def detect_img(yolo: KerasYOLO, config: YoloConfig):
    while True:
        image_path = input('Input image filename:')
        image_path = image_path.strip()
        r_boxes, r_image = None, None
        try:
            image = Image.open(image_path)
            r_boxes, r_image = predict(yolo, config, image_path, image)
        except Exception as e:
            print('Open Error! Try again!')
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))
            continue
        else:
            # export predicted image and meta data
            import cv2
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            out_image_filename = "{}.jpg".format(timestamp)
            out_image_path = os.path.join(config.output_path, out_image_filename)
            cv2.imwrite(out_image_path, np.asarray(r_image)[...,::-1])

            out_meta_filename = "{}.json".format(timestamp)
            out_meta_path = os.path.join(config.output_path, out_meta_filename)
            meta = {
                'model_data' : {'model' : config.model_path, 'anchors' : config.anchors_path, 'classes' : config.classes_path},
                'original_image' : image_path,
                'bboxes' : r_boxes,
                'predicted' : [ '{} {:.2f}'.format(class_name, score) for _, class_name, score, _, _, _, _ in r_boxes ]
            }
            with open(out_meta_path, 'w') as f:
                json.dump(meta, f, indent=2, cls=MyEncoder)
            
            # show result
            r_image.show()
    yolo.close_session()


def detect_images_and_report(yolo: KerasYOLO, config: YoloConfig, report_target_list:str):
    report_html_template = open('template/report_body.html', 'r').read()
    report_html_row_template = open('template/report_row.html', 'r').read()

    num_of_ok = 0
    entities = []
    for image_path, class_labels in load_report_target_list(report_target_list):
        image = Image.open(image_path)
        # r_boxes, r_image, out_image_path, meta, out_meta_path = predict(model, config, image_path, image)
        r_boxes, r_image = predict(yolo, config, image_path, image)
        find_results = []
        for target_class_name in class_labels:
            find_classes = []
            for _, class_name, score, _, _, _, _ in r_boxes:
                if target_class_name == class_name[0:len(target_class_name)]:  # start with...
                    find_classes.append((class_name, score))
            if len(find_classes) > 0:
                find_results.append(target_class_name)
        if len(find_results) > 0:
            num_of_ok = num_of_ok + 1
        
        # バイナリデータをbase64でエンコードし、それをさらにutf-8でデコードしておく
        buf = BytesIO()
        r_image.save(buf,format="png")
        r_image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        
        entities.append(report_html_row_template.format(
            image=r_image_base64,
            classes=', '.join(class_labels),
            image_path=image_path,
            result='OK' if len(find_results) > 0 else 'NG',
            ditecteds=', '.join(find_results) if len(find_results) > 0 else 'N/A',
            score=config.score_threshold,
            iou=config.iou_threshold
        ))
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_filename = "report_{}.html".format(timestamp)
    with open(os.path.join(config.output_path, report_filename), 'w') as html_file:
        html_file.write(report_html_template.format(
            title='Report {timestamp}'.format(timestamp=timestamp),
            model_path=config.model_path,
            num_ok=num_of_ok,
            num_all=len(entities),
            score_threshold=config.score_threshold,
            iou_threshold=config.iou_threshold,
            contents='\n'.join(entities)
        ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--anchors_path", type=str, required=True)
    parser.add_argument("--classes_path", type=str, required=True)
    parser.add_argument("--out_path", type=str, required=True)
    parser.add_argument("--report_mode", action='store_true', required=False)
    parser.add_argument("--report_target_list", type=str, required=False)
    parser.add_argument("--iou_threshold", type=str, required=False, default=0.1)
    parser.add_argument("--score_threshold", type=str, required=False, default=0.1)
    args, unknown_args = parser.parse_known_args()

    #--------------------------------
    root_dir = os.path.abspath(os.path.dirname(__file__))
    config = YoloConfig()
    config.model_path = args.model_path
    config.anchors_path = args.anchors_path
    config.classes_path = args.classes_path
    # config.output_path = os.path.join(root_dir, 'predicted')
    config.output_path = args.out_path
    config.iou_threshold = args.iou_threshold
    config.score_threshold = args.score_threshold

    model = KerasYOLO(
        model_path=config.model_path,
        anchors_path=config.anchors_path,
        classes_path=config.classes_path,
        score=float(config.iou_threshold),
        iou=float(config.iou_threshold)
        )
        # score_threshold=self.score, iou_threshold=self.iou

    if not args.report_mode:
        detect_img(model, config)
    else:
        report_target_list = args.report_target_list
        detect_images_and_report(model, config, report_target_list)