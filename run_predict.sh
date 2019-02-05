#!/bin/bash

set -Ceu

eval "$(cat .env <(echo) <(declare -x))"

pipenv run python3 predict.py \
  --model_path ${OUTPUT_DIR}/${OUTPUT_MODEL_NAME} \
  --anchors_path keras-yolo3/model_data/tiny_yolo_anchors.txt \
  --classes_path ${CLASS_PATH} \
  --out_path ${OUTPUT_DIR}/predicted \
  --iou_threshold $IOU_THRESHOLD \
  --score_threshold $SCORE_THRESHOLD