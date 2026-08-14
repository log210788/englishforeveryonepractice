import enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ExerciseType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    SENTENCE_ORDERING = "sentence_ordering"
    TRUE_FALSE = "true_false"
    AUDIO_LISTEN = "audio_listen"


class QuestionItem(BaseModel):
    item_number: int = Field(
        description="Item or question number within the exercise (e.g., 1, 2, 3)."
    )
    prompt_text: Optional[str] = Field(
        default=None,
        description="Given visual context, sample sentence, starting phrase, or visual prompt text if applicable."
    )
    question: str = Field(
        description="The main question text, text with blank, or target sentence to reorder/correct."
    )
    options: Optional[List[str]] = Field(
        default=None,
        description="List of choices/options available for multiple choice or matching exercises."
    )
    correct_answer: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Correct answer or filled blank string, or list of strings if multiple answers exist. Can be inferred if answer key or sample answer is shown."
    )
    audio_icon_present: bool = Field(
        default=False,
        description="True if an audio track icon (headphone symbol) is shown near this item or exercise."
    )
    audio_track_ref: Optional[str] = Field(
        default=None,
        description="Audio track reference number if an audio icon shows a track number (e.g. '1.4' or '23')."
    )
    audio_file_path: Optional[str] = Field(
        default=None,
        description="Relative file path to local audio track file (e.g. 'audio/track_1.4.mp3')."
    )


class Exercise(BaseModel):
    exercise_id: str = Field(
        description="Identifier of the exercise, e.g. '1.1', '2.3', 'A', 'B'."
    )
    exercise_type: ExerciseType = Field(
        description="Type of language exercise on the page."
    )
    instruction: str = Field(
        description="Full instruction header text for the exercise (e.g., 'REWRITE THE SENTENCES, CORRECTING THE ERRORS')."
    )
    items: List[QuestionItem] = Field(
        default_factory=list,
        description="List of question items in this exercise."
    )


class PageExtraction(BaseModel):
    page_number: int = Field(
        description="Page number of the book."
    )
    unit_number: Optional[int] = Field(
        default=None,
        description="Unit number if this page belongs to a specific unit (e.g., 1)."
    )
    unit_title: Optional[str] = Field(
        default=None,
        description="Title of the unit (e.g., 'Making friends', 'Introductions')."
    )
    exercises: List[Exercise] = Field(
        default_factory=list,
        description="List of exercises found on this page."
    )
