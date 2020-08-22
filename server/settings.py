VERSION = 1.0
ALS_LOG = "Als_server: "
# initialize Redis connection settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# initialize constants used to control image spatial dimensions and
# data type
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
IMAGE_CHANS = 1
IMAGE_DTYPE = "float16"

# initialize constants used for server queuing
IMAGE_QUEUE = "image_queue"
PREDICT_QUEUE = "predict_queue"
BATCH_SIZE = 32
MIN_BATCH_SIZE = 5
SERVER_SLEEP = 0.01
CLIENT_SLEEP = 0.005

FOCAL_LENGTH = 12
CONFIDENCE_THRESHOLD = 0.96
