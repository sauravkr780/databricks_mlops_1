"""
This module contains logical models, not the machine learning ones
"""
from typing import Dict, Any

import pandas as pd
from pydantic import BaseModel

SearchSpace = Dict[str, Dict[str, Any]]


class FlexibleBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class TrainData(FlexibleBaseModel):
    X: pd.DataFrame
    y: pd.Series


class TestData(FlexibleBaseModel):
    X: pd.DataFrame
    y: pd.Series


class ModelData(FlexibleBaseModel):
    train: TrainData
    test: TestData


class MlflowInfo(BaseModel):
    registry_uri: str
    tracking_uri: str
