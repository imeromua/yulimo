from sqlalchemy import Column, Integer, String, Text

from database import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id           = Column(Integer, primary_key=True, index=True)
    key          = Column(String(100), unique=True, nullable=False)
    value        = Column(Text, nullable=False, default="")
    label        = Column(String(200), nullable=False)
    group        = Column(String(50), nullable=False, default="general")
    setting_type = Column(String(20), default="text")  # text|boolean|color|url
