from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Emotion:
    name: str
    percent: float
    count: Optional[int] = None

@dataclass
class EmotionStats:
    emotions: List[Emotion]
    total_messages: int
    year: Optional[str] = None

@dataclass
class EmotionStatsByYear:
    all_years: EmotionStats
    by_year: Dict[str, EmotionStats] 