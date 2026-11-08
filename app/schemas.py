"""Esquemas de entrada con validaciones conservadoras para un experimento."""

from pydantic import BaseModel, ConfigDict, Field


class CreditApplication(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    LIMIT_BAL: float = Field(gt=0, le=1_000_000_000)
    PAY_0: int = Field(ge=-2, le=8)
    PAY_2: int = Field(ge=-2, le=8)
    PAY_3: int = Field(ge=-2, le=8)
    PAY_4: int = Field(ge=-2, le=8)
    PAY_5: int = Field(ge=-2, le=8)
    PAY_6: int = Field(ge=-2, le=8)
    BILL_AMT1: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    BILL_AMT2: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    BILL_AMT3: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    BILL_AMT4: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    BILL_AMT5: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    BILL_AMT6: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    PAY_AMT1: float = Field(ge=0, le=1_000_000_000)
    PAY_AMT2: float = Field(ge=0, le=1_000_000_000)
    PAY_AMT3: float = Field(ge=0, le=1_000_000_000)
    PAY_AMT4: float = Field(ge=0, le=1_000_000_000)
    PAY_AMT5: float = Field(ge=0, le=1_000_000_000)
    PAY_AMT6: float = Field(ge=0, le=1_000_000_000)
