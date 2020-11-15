Clone including submodule (we need the tensorflow object detection API, which is contained in the tensorflow/models repo):
`git submodule update --init --recursive`

Get the images:
`git lfs install` (just need to run this once)
`git lfs pull`

Install tensorflow:
https://www.tensorflow.org/install/pip#virtual-environment-install

Enable GPU support:
https://www.tensorflow.org/install/gpu

Protobuf Installation/Compilation:
https://github.com/protocolbuffers/protobuf/releases
(protoc-3.14.0-win64.zip)

`cd models\research`
`for /f %i in ('dir /b object_detection\protos\*.proto') do protoc object_detection\protos\%i --python_out=.`

COCO API installation:
(could do it in the virtual environment)
`pip install cython`
`pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI`

Install the Object Detection API
(could do it in the virtual environment)
`cd models\research`
`copy object_detection\packages\tf2\setup.py .`
`pip install --use-feature=2020-resolver .`

Test installation:
`cd models\research`
`python object_detection/builders/model_builder_tf2_test.py`

Overall reference:
Installations
https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md

Object detection API, Models:
(You would need to download them on your own and put inside a NNs directory)
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md

Objecti detection API, examples:
https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/object_detection_camera.html
https://heartbeat.fritz.ai/real-time-object-detection-using-ssd-mobilenet-v2-on-video-streams-3bfc1577399c