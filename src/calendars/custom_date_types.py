from typing import Union
from pandas import Timestamp
from datetime import date, datetime
import numpy as np

Date = Union[Timestamp, date, datetime, np.datetime64]
TODAY = Timestamp.today().date()
