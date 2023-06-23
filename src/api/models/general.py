from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from bson import ObjectId
from typing import Optional, Union, List, Dict, Literal, Any
from utilities import datestring_to_datetime
import itertools
import datetime
import numpy as np
from utilities import datetime_to_datestring, datestring_to_datetime
from utilities import generate_list_of_supported_dates_in_year
from copy import deepcopy
import itertools


# todo: ensure that validator names are unique

# ------------------------------- UTILITIES --------------------------------- #

# define class to handle serialization of ObjectId, that is required for object ids but is
# not natively supported by MongoDb (see https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class IlliquidValueModel(BaseModel):
    metric_type: Literal['reported', 'estimated']
    value: float