from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Optional


# --- Enums ---

class TaskType(Enum):
    WALK = "walk"
    FEED = "feed"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"
    VET = "vet"
    OTHER = "other"


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class Frequency(Enum):
    DAILY = "daily"
    TWICE_DAILY = "twice_daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


# --- Dataclasses ---

@dataclass
class Task:
    name: str
    task_type: TaskType
    duration_minutes: int
    priority: Priority
    frequency: Frequency
    pet: Optional["Pet"] = None
    preferred_time: Optional[time] = None
    notes: str = ""

    def get_priority_score(self) -> int:
        pass

    def is_time_sensitive(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: float
    weight: float
    health_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def update_task(self, task: Task) -> None:
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        pass

    def get_total_task_duration(self) -> int:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: time
    preferred_end_time: time
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_total_available_time(self) -> int:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time

    def get_duration(self) -> int:
        pass

    def overlaps_with(self, other: "ScheduledTask") -> bool:
        pass


@dataclass
class DailyPlan:
    date: date
    owner: Owner
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)

    def get_total_scheduled_time(self) -> int:
        pass

    def get_explanation(self) -> str:
        pass

    def is_feasible(self) -> bool:
        pass


# --- Scheduler (plain class, not a dataclass) ---

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self, plan_date: date) -> DailyPlan:
        pass

    def _prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fit_tasks(self, tasks: list[Task], available_minutes: int) -> tuple[list[Task], list[Task]]:
        pass

    def _assign_times(self, tasks: list[Task]) -> list[ScheduledTask]:
        pass

    def _build_reasoning(self, scheduled: list[Task], unscheduled: list[Task]) -> list[str]:
        pass
