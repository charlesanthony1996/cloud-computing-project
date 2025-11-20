import numpy as np
import os
import time
import math
import random
import requests

TARGET_URL = os.getenv("TARGET_URL", "http://localhost:8081/ingest")
SESSION_ID = os.getenv("SESSION_ID", "s1")
RATE_HZ = float(os.getenv("RATE_HZ", "10"))
DT = 1.0 / RATE_HZ


def sample(t):
    f = 1.8
    pass