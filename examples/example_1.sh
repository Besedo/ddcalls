# Example based on this tutorial
# https://deepdetect.com/tutorials/csv-training/

path_ddcalls=$(pwd)

# Download data
mkdir models
mkdir models/covert
cd models/covert
# Train data
wget http://www.deepdetect.com/dd/examples/all/forest_type/train.csv.tar.bz2
tar xvjf train.csv.tar.bz2

# Test data
wget http://www.deepdetect.com/dd/examples/all/forest_type/test.csv.tar.bz2
tar xvjf test.csv.tar.bz2
head -n 11 test.csv > test10.csv

cd ${path_ddcalls}

# Launch DD
bash launch_dd.sh&

echo "Launch training"
# Launch training 
ddcalls-train \
    --path_dd_config "./dd_config.json" \
    --host "localhost" \
    --port 8080 \
    --repository "${path_ddcalls}/models/covert" \
    --data "${path_ddcalls}/models/covert/train.csv"

echo "Launch prediction"
# Launch prediction
ddcalls-predict \
    --path_dd_config "./dd_config.json" \
    --host "localhost" \
    --port 8080 \
    --repository "${path_ddcalls}/models/covert" \
    --data "${path_ddcalls}/models/covert/test10.csv" ;


echo "/home/yassine.bezza/ddcalls/examples"

# Free DeepDetect
killall dede
