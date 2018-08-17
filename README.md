# [ddcalls](https://github.com/EBazarov/ddcalls) - simple API calls for [DeepDetect](https://github.com/beniz/deepdetect)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
> ddcalls is a python library for simple configurable training and prediction API calls to DeepDetect server
## Introduction
[DeepDetect](https://github.com/beniz/deepdetect) is an open source Deep Learning Server & API for Caffe, Tensorflow, XGBoost and TSNE. It's very powerful and help us to build new DL & ML models or use them out of the box, but DeepDetect has a lack of support for simple python API usage. That's why I have started project [ddcalls](https://github.com/EBazarov/ddcalls).  

## Installation

ddcalls was tested on Python3.5+.

You can install it via pip
```
$ pip install git+https://github.com/Besedo/ddcalls
```

## Usage

Train and prediction scripts require a ddcalls config file to be passed.
DDcalls config file composed from 3 elements which is:
- service
- train
- predict

In each of them you define DeepDetect API structure for required task. 
In example below you will find MLP training and prediction config file.
```
{
	"service": {
		"sname": "classification_service",
		"description": "MLP classifier",
		"mllib": "caffe",
		"type": "supervised",
		"parameters": {
			"input": {
				"connector": "svm"
			},
			"mllib": {
				"gpu": true,
				"gpuid": 0,
				"template": "mlp",
				"nclasses": 2,
				"ntargets": null,
				"layers": [512, 256],
				"activation": "relu",
				"dropout": 0.5,
				"regression": false,
				"finetuning": false,
				"db": true
			},
			"output":{}
		},
		"model": {
			"repository": "path/to/MLP/model/folder",
			"templates": "../templates/caffe",
			"weights": null
		}
	},
	"train": {
		"async": true,
		"data": [
			"path/to/train.svm",
			"path/to/validation.svm"
		],
		"parameters":{
			"input": {
				"db": true
			},
			"mllib": {
				"gpu": true,
				"gpuid": 0,
				"resume": false,
				"class_weights": [1.0, 1.0],
				"ignore_label": null,
				"solver": {
					"iterations": 10000,
					"snapshot": 1500,
					"snapshot_prefix": null,
					"solver_type": "ADAM",
					"test_interval": 250,
					"test_initialization": true,
					"lr_policy": "step",
					"base_lr": 0.05,
					"gamma": 0.1,
					"stepsize": 4000,
					"momentum": 0.9,
					"weight_decay": 0.00001,
					"power": null,
					"iter_size": 1
				},
				"net": {
					"batch_size": 256,
					"test_batch_size": 64
				}
			},
			"output": {
				"best": 2,
				"measure": ["accp", "mcll", "f1", "mcc"]
			}
		}
	},
	"predict": {
		"data": [
			"path/to/train.lmdb",
			"path/to/test.lmdb",
			"path/to/val.lmdb"
		],
		"parameters": {
			"input": {},
			"mllib": {
				"gpu": true,
				"gpuid": 0,
				"net": {
					"test_batch_size": 512
				}
			},
			"output": {
				"best": 2
			}
		}
	}
}
```

### Train

Training model **ddcalls-train**:
```
❯ ddcalls-train -h
usage: DeepDetect training script [-h] [--path_dd_config PATH_DD_CONFIG]
                                  [--host HOST] [--port PORT]
                                  [--logdir_ddboard LOGDIR_DDBOARD]
                                  [--use_ddboard USE_DDBOARD] [--sname SNAME]
                                  [--data DATA] [--repository REPOSITORY]
                                  [--gpu GPU] [--gpuid GPUID]
                                  [--templates TEMPLATES] [--resume RESUME]

optional arguments:
  -h, --help            show this help message and exit
  --path_dd_config PATH_DD_CONFIG
                        path to ddcalls config file
  --host HOST           DeepDetect host, default localhost
  --port PORT           DeepDetect port, default 8080
  --logdir_ddboard LOGDIR_DDBOARD
                        path to ddboard logdir
  --use_ddboard USE_DDBOARD
                        save training metrics in tensorboard format
  --sname SNAME         DeepDetect service name
  --data DATA           comma separated path to data
  --repository REPOSITORY
                        path to model repository
  --gpu GPU             use GPU or CPU
  --gpuid GPUID         GPU id
  --templates TEMPLATES
                        path to DeepDetect templates
  --resume RESUME       resume training
```

### Predict

Prediction **ddcalls-predict**:
```
❯ ddcalls-predict -h
usage: DeepDetect prediction script [-h] [--path_dd_config PATH_DD_CONFIG]
                                    [--host HOST] [--port PORT]
                                    [--sname SNAME] [--data DATA]
                                    [--repository REPOSITORY] [--gpu GPU]
                                    [--gpuid GPUID] [--templates TEMPLATES]

optional arguments:
  -h, --help            show this help message and exit
  --path_dd_config PATH_DD_CONFIG
                        path to ddcalls config file
  --host HOST           DeepDetect host, default localhost
  --port PORT           DeepDetect port, default 8080
  --sname SNAME         DeepDetect service name
  --data DATA           comma separated path to data
  --repository REPOSITORY
                        path to model repository
  --gpu GPU             use GPU or CPU
  --gpuid GPUID         GPU id
  --templates TEMPLATES
                        path to DeepDetect templates
```

Predictions will be stored in JSON files under folder that will have prefix `predicitons_` and postfix the number of used weights (by default the last one).
