from datetime import date

from pydantic import EmailStr, Field

from app.models.base import APIModel, Metadata, TimestampedModel


class UserProfile(TimestampedModel):
    id: str
    email: EmailStr
    full_name: str
    phone: str | None = None
    location: str | None = None
    date_of_birth: date | None = None
    education_level: str | None = None
    school_name: str | None = None
    graduation_year: int | None = Field(default=None, ge=1900, le=2200)
    fields_of_study: list[str] = Field(default_factory=list)
    career_goals: list[str] = Field(default_factory=list)
    citizenship_status: str | None = None
    funding_goals: list[str] = Field(default_factory=list)
    demographic_info: Metadata = Field(default_factory=dict)
    preferences: Metadata = Field(default_factory=dict)


class UserProfileUpdate(APIModel):
    email: EmailStr | None = None
    full_name: str | None = None
    phone: str | None = None
    location: str | None = None
    date_of_birth: date | None = None
    education_level: str | None = None
    school_name: str | None = None
    graduation_year: int | None = Field(default=None, ge=1900, le=2200)
    fields_of_study: list[str] | None = None
    career_goals: list[str] | None = None
    citizenship_status: str | None = None
    funding_goals: list[str] | None = None
    demographic_info: Metadata | None = None
    preferences: Metadata | None = None
