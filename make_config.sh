#!/bin/sh -x

set -x

eval "$(cat .env <(echo) <(declare -x))"


# CLASS_NUM=1
# TRAIN_DATA=dataset/train_data
# VAL_DATA=dataset/val_data
# FILE_DB=cfg/dataset.txt
# FILE_LBL=cfg/labels.txt
# CFG_TRAIN=yolov3-tiny.train.cfg
# CFG_PREDI=yolov3-tiny.predict.cfg


### make model config
FILTERS=`expr \( $CLASS_NUM + 5 \) \* 3`

cp cfg/yolov3-tiny.template.cfg cfg/${CFG_TRAIN}
sed -i.bak 's/^batch=64/batch=32/g' cfg/${CFG_TRAIN}
sed -i.bak 's/^classes=80/classes='${CLASS_NUM}'/g' cfg/${CFG_TRAIN}
sed -i.bak 's/^filters=255/filters='${FILTERS}'/g' cfg/${CFG_TRAIN}
rm cfg/${CFG_TRAIN}.bak

cp cfg/yolov3-tiny.template.cfg cfg/${CFG_PREDI}
sed -i.bak 's/^batch=64/batch=1/g' cfg/${CFG_PREDI}
sed -i.bak 's/^subdivisions=16/subdivisions=1/g' cfg/${CFG_PREDI}
sed -i.bak 's/^classes=80/classes='${CLASS_NUM}'/g' cfg/${CFG_TRAIN}
sed -i.bak 's/^filters=255/filters='${FILTERS}'/g' cfg/${CFG_TRAIN}
rm cfg/${CFG_PREDI}.bak



### copy label file

cp ${TRAIN_DATA}/labels.txt ${FILE_LBL}


### make dataset file

cat << EOT > ${FILE_DB}
classes=${CLASS_NUM}
train=temp/train/index.txt
valid=temp/val/index.txt
backup=backup/
names=${FILE_LBL}
EOT