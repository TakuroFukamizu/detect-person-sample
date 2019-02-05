



## Crate Config files

### model config

- classes はクラス数。  
- filtersの計算式は `filters=(クラス数+5)*3` で計算する。

yolo3の場合:  
```sh
$ set -x; \
  export CLASS_NUM=28; \
  export CFG_TRAIN=yolov3.train.cfg; \
  export CFG_PREDI=yolov3.predict.cfg; \
  export FILTERS=`expr \( $CLASS_NUM + 5 \) \* 3`; \
  cp cfg/yolov3.template.cfg cfg/${CFG_TRAIN}; \
    sed -i.bak 's/^classes=80/classes='${CLASS_NUM}'/g' cfg/${CFG_TRAIN}; \
    sed -i.bak 's/^filters=255/filters='${FILTERS}'/g' cfg/${CFG_TRAIN}; \
  cp cfg/yolov3.template.cfg cfg/${CFG_PREDI}; \
    sed -i.bak 's/^batch=64/batch=1/g' cfg/${CFG_PREDI}; \
    sed -i.bak 's/^subdivisions=16/subdivisions=1/g' cfg/${CFG_PREDI}; \
    sed -i.bak 's/^classes=80/classes='${CLASS_NUM}'/g' cfg/${CFG_PREDI}; \
    sed -i.bak 's/^filters=255/filters='${FILTERS}'/g' cfg/${CFG_PREDI}; \
  rm cfg/${CFG_TRAIN}.bak; \
  rm cfg/${CFG_PREDI}.bak
```

tiny-yolo3の場合:  
```sh
$ set -x; \
  export CLASS_NUM=1; \
  export CFG_TRAIN=yolov3-tiny.train.cfg; \
  export CFG_PREDI=yolov3-tiny.predict.cfg; \
  export FILTERS=`expr \( $CLASS_NUM + 5 \) \* 3`; \
  cp cfg/yolov3-tiny.template.cfg cfg/${CFG_TRAIN}; \
    sed -i.bak 's/^batch=64/batch=32/g' cfg/${CFG_TRAIN}; \
    sed -i.bak 's/^classes=80/classes='${CLASS_NUM}'/g' cfg/${CFG_TRAIN}; \
    sed -i.bak 's/^filters=255/filters='${FILTERS}'/g' cfg/${CFG_TRAIN}; \
  cp cfg/yolov3-tiny.template.cfg cfg/${CFG_PREDI}; \
    sed -i.bak 's/^batch=64/batch=1/g' cfg/${CFG_PREDI}; \
    sed -i.bak 's/^subdivisions=16/subdivisions=1/g' cfg/${CFG_PREDI}; \
    sed -i.bak 's/^classes=80/classes='${CLASS_NUM}'/g' cfg/${CFG_PREDI}; \
    sed -i.bak 's/^filters=255/filters='${FILTERS}'/g' cfg/${CFG_PREDI}; \
  rm cfg/${CFG_TRAIN}.bak; \
  rm cfg/${CFG_PREDI}.bak
```

### make or copy label file

教師データのラベルファイルを `cfg` ディレクトリ配下にコピーする。

### make dataset file

```sh
$ set -x; \
  export CLASS_NUM=1; \
  export FILE_DB=cfg/dataset.txt; \
  export FILE_LBL=cfg/labels.txt; \
cat << EOT > ${FILE_DB}
classes=${CLASS_NUM}
train=temp/train/index.txt
valid=temp/val/index.txt
backup=backup/
names=${FILE_LBL}
EOT
```


## Training

学習を実行するGPUマシン/サーバにログインして本リポジトリをチェックアウトする。  

dockerコンテナを起動する。  

```sh
docker run \
    --name manakamera-ai-training \
    --runtime=nvidia \
    -v $PWD:/opt/app \
    -it fkmy/nvidia-docker-darknet:latest
```

または、既にコンテナを作成済みの場合は runしてアタッチする。

```sh
$ docker start manakamera-ai-training && docker attach manakamera-ai-training
```

コンテナに入ったら、以下のように学習を実行する。  
(TRAIN_DATA, VAL_DATA, FILE_DB, FILE_CFG は自分が学習させたいデータに合わせて適宜変更する)

yolo3の場合:  
```sh
$ cd /opt/app
$ set -x; \
  export TRAIN_DATA=dataset/train_data; \
  export VAL_DATA=dataset/val_data; \
  export FILE_DB=cfg/dataset.txt; \
  export FILE_CFG=cfg/yolov3.train.cfg; \
  export PATH=/opt/darknet:$PATH; \
  ./prep.sh; \
  darknet detector train ${FILE_DB} ${FILE_CFG} /opt/darknet/darknet53.conv.74
```

tiny-yolo3の場合:  
```sh
$ cd /opt/app
$ set -x; \
  export TRAIN_DATA=dataset/train_data; \
  export VAL_DATA=dataset/val_data; \
  export FILE_DB=cfg/dataset.txt; \
  export FILE_CFG=cfg/yolov3-tiny.train.cfg; \
  export PATH=/opt/darknet:$PATH; \
  ./prep.sh; \
  darknet detector train ${FILE_DB} ${FILE_CFG} /opt/app/yolov3-tiny.conv.15
```

----

