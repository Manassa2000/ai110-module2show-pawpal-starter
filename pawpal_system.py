from dataclasses import dataclass, field
"""
This module defines a pet care scheduling system. It includes classes and methods to manage tasks for pets, 
prioritize them based on urgency and time sensitivity, and generate daily plans for pet owners. 

Classes:
    TaskType (Enum): Represents different types of tasks (e.g., walk, feed, meds, etc.).
    Priority (Enum): Represents task priority levels (HIGH, MEDIUM, LOW).
    Frequency (Enum): Represents task frequency (e.g., daily, weekly, as needed).
    Task (dataclass): Represents a task for a pet, including its type, priority, duration, and other details.
    Pet (dataclass): Represents a pet, including its details and associated tasks.
    Owner (dataclass): Represents a pet owner, including their available time and pets.
    ScheduledTask (dataclass): Represents a task scheduled at a specific time.
    DailyPlan (dataclass): Represents a daily plan for an owner, including scheduled and unscheduled tasks.
    Scheduler: Handles task prioritization, scheduling, and generating daily plans.

Key Features:
    - Task prioritization based on priority level and time sensitivity.
    - Scheduling tasks within the owner's available time budget.
    - Handling time-sensitive tasks with preferred times.
    - Generating reasoning logs for scheduling decisions.
    - Managing pets and their associated tasks.

Usage:
    - Create instances of `Pet`, `Task`, and `Owner`.
    - Use the `Scheduler` class to generate a `DailyPlan` for a specific date.
    - Access scheduled tasks, unscheduled tasks, and reasoning logs from the `DailyPlan`.
"""
from datetime import date, time, datetime, timedelta
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
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True

    def get_priority_score(self) -> int:
        """Return numeric score for sorting. Time-sensitive tasks get a bonus."""
        score = self.priority.value
        if self.is_time_sensitive():
            score += 1
        return score

    def is_time_sensitive(self) -> bool:
        """True if the task has a preferred time (e.g. meds at 8 AM)."""
        return self.preferred_time is not None


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
        """Add a task and link it back to this pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task by identity match."""
        self.tasks = [t for t in self.tasks if t is not task]

    def update_task(self, updated_task: Task) -> None:
        """Replace the first task with the same name as updated_task."""
        for i, t in enumerate(self.tasks):
            if t.name == updated_task.name:
                updated_task.pet = self
                self.tasks[i] = updated_task
                return

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted highest priority first, time-sensitive tasks first within tier."""
        return sorted(self.tasks, key=lambda t: t.get_priority_score(), reverse=True)

    def get_total_task_duration(self) -> int:
        """Total minutes needed for all tasks."""
        return sum(t.duration_minutes for t in self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: time
    preferred_end_time: time
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        self.pets = [p for p in self.pets if p is not pet]

    def get_total_available_time(self) -> int:
        """Return available_minutes (single source of truth for the scheduler)."""
        return self.available_minutes

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time

    def get_duration(self) -> int:
        """Duration in minutes derived from start/end times."""
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        return int((end_dt - start_dt).total_seconds() // 60)

    def overlaps_with(self, other: "ScheduledTask") -> bool:
        """True if this task's time window overlaps with another's."""
        return self.start_time < other.end_time and self.end_time > other.start_time


@dataclass
class DailyPlan:
    date: date
    owner: Owner
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)

    def get_total_scheduled_time(self) -> int:
        """Total minutes of all scheduled tasks."""
        return sum(st.get_duration() for st in self.scheduled_tasks)

    def get_explanation(self) -> str:
        """Human-readable reasoning log joined into a single string."""
        return "\n".join(self.reasoning)

    def is_feasible(self) -> bool:
        """True when every task fit within the available time budget."""
        return len(self.unscheduled_tasks) == 0


# --- Scheduler ---

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self, plan_date: date) -> DailyPlan:
        """Build and return a DailyPlan for the given date."""
        all_tasks = self.owner.get_all_tasks()
        prioritized = self._prioritize_tasks(all_tasks)
        scheduled_tasks, unscheduled_tasks = self._fit_tasks(
            prioritized, self.owner.get_total_available_time()
        )
        scheduled_task_slots = self._assign_times(scheduled_tasks)
        reasoning = self._build_reasoning(scheduled_tasks, unscheduled_tasks)

        return DailyPlan(
            date=plan_date,
            owner=self.owner,
            scheduled_tasks=scheduled_task_slots,
            unscheduled_tasks=unscheduled_tasks,
            reasoning=reasoning,
        )

    def _prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks: time-sensitive HIGH first, then by priority score descending."""
        return sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)

    def _fit_tasks(
        self, tasks: list[Task], available_minutes: int
    ) -> tuple[list[Task], list[Task]]:
        """Greedily include tasks until the time budget is exhausted."""
        scheduled, unscheduled = [], []
        remaining = available_minutes

        for task in tasks:
            if task.duration_minutes <= remaining:
                scheduled.append(task)
                remaining -= task.duration_minutes
            else:
                unscheduled.append(task)

        return scheduled, unscheduled

    def _assign_times(self, tasks: list[Task]) -> list[ScheduledTask]:
        """
        Place tasks sequentially starting from the owner's preferred start time.
        Time-sensitive tasks are pinned to their preferred_time when possible.
        """
        slots: list[ScheduledTask] = []
        # Split into pinned (preferred_time set) and free tasks
        pinned = sorted([t for t in tasks if t.is_time_sensitive()], key=lambda t: t.preferred_time)
        free = [t for t in tasks if not t.is_time_sensitive()]

        # Schedule pinned tasks first
        for task in pinned:
            start = task.preferred_time
            start_dt = datetime.combine(date.today(), start)
            end_dt = start_dt + timedelta(minutes=task.duration_minutes)
            slots.append(ScheduledTask(task=task, start_time=start, end_time=end_dt.time()))

        # Schedule free tasks sequentially after start time, skipping over pinned windows
        cursor_dt = datetime.combine(date.today(), self.owner.preferred_start_time)

        for task in free:
            # Advance cursor past any pinned tasks that overlap
            for slot in sorted(slots, key=lambda s: s.start_time):
                slot_start = datetime.combine(date.today(), slot.start_time)
                slot_end = datetime.combine(date.today(), slot.end_time)
                if cursor_dt < slot_end and cursor_dt + timedelta(minutes=task.duration_minutes) > slot_start:
                    cursor_dt = slot_end

            end_dt = cursor_dt + timedelta(minutes=task.duration_minutes)
            slots.append(ScheduledTask(task=task, start_time=cursor_dt.time(), end_time=end_dt.time()))
            cursor_dt = end_dt

        # Return all slots sorted by start time
        return sorted(slots, key=lambda s: s.start_time)

    def _build_reasoning(
        self, scheduled: list[Task], unscheduled: list[Task]
    ) -> list[str]:
        """Generate a plain-English explanation of scheduling decisions."""
        lines = []
        total = sum(t.duration_minutes for t in scheduled)
        budget = self.owner.get_total_available_time()

        lines.append(f"Scheduled {len(scheduled)} task(s) using {total} of {budget} available minutes.")

        for task in scheduled:
            pet_name = task.pet.name if task.pet else "Unknown"
            reason = "time-sensitive" if task.is_time_sensitive() else f"priority={task.priority.name}"
            lines.append(f"  ✓ [{pet_name}] {task.name} ({task.duration_minutes} min) — {reason}")

        if unscheduled:
            lines.append(f"Skipped {len(unscheduled)} task(s) due to time constraints:")
            for task in unscheduled:
                pet_name = task.pet.name if task.pet else "Unknown"
                lines.append(f"  ✗ [{pet_name}] {task.name} ({task.duration_minutes} min) — insufficient time remaining")

        return lines
