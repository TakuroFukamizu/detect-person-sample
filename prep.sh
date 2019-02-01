#!/bin/sh -x

# eval "$(cat .env <(echo) <(declare -x))"

rm -rf temp/train
rm -rf temp/val

mkdir -p temp/train/images
mkdir -p temp/train/labels
mkdir -p temp/val/images
mkdir -p temp/val/labels

cp -r ${TRAIN_DATA}/Images/* temp/train/images/
cp -r ${TRAIN_DATA}/BBoxes/* temp/train/labels/
# cp -r train_data/train.txt temp/train/index.txt

cp -r ${VAL_DATA}/Images/* temp/val/images/
cp -r ${VAL_DATA}/BBoxes/* temp/val/labels/
# # cp -r val_data/train.txt temp/val/index.txt

ls temp/train/images/**/*.jpg > temp/train/index.txt
ls temp/val/images/**/*.jpg > temp/val/index.txt

echo "darknet detector train ${FILE_DB} ${FILE_CFG} /opt/app/yolov3-tiny.conv.15"
