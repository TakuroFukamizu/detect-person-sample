#!/bin/bash

set -Ceu

eval "$(cat .env <(echo) <(declare -x))"

mkdir -p keras-yolo3/work
cp ${CONFIG_PATH} keras-yolo3/work/yolov3-tiny.predict.cfg
cp ${WEIGHTS_PATH} keras-yolo3/work/yolov3-tiny.weights
cp ${CLASS_PATH} keras-yolo3/work/labels.txt

cd keras-yolo3

pipenv run python3 convert.py \
    work/yolov3-tiny.predict.cfg \
    work/yolov3-tiny.weights \
    work/${OUTPUT_MODEL_NAME}

cd ../

cp keras-yolo3/work/${OUTPUT_MODEL_NAME} ${OUTPUT_DIR}/
echo ${OUTPUT_DIR}/${OUTPUT_MODEL_NAME}