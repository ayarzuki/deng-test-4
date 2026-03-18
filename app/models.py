from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class EffectEntry(Base):
    __tablename__ = "effect_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_id = Column(String(13), nullable=False)
    user_id = Column(String(7), nullable=False)
    pokemon_ability_id = Column(String(10), nullable=False)
    effect = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    short_effect = Column(Text, nullable=False)
