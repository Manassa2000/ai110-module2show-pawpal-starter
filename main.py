from datetime import date, time

from pawpal_system import (
    Owner, Pet, Task,
    TaskType, Priority, Frequency,
    Scheduler,
)


# --- Setup Owner ---
owner = Owner(
    name="Alex",
    available_minutes=120,
    preferred_start_time=time(7, 0),
    preferred_end_time=time(21, 0),
)

# --- Setup Pets ---
buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3.0, weight=30.0)
whiskers = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5.0, weight=4.5)

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Add Tasks to Buddy ---
buddy.add_task(Task(
    name="Morning Walk",
    task_type=TaskType.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 0),
))

buddy.add_task(Task(
    name="Evening Walk",
    task_type=TaskType.WALK,
    duration_minutes=20,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
    preferred_time=time(18, 0),
))

buddy.add_task(Task(
    name="Flea Medication",
    task_type=TaskType.MEDS,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.WEEKLY,
    preferred_time=time(8, 0),
    notes="Apply between shoulder blades",
))

# --- Add Tasks to Whiskers ---
whiskers.add_task(Task(
    name="Breakfast",
    task_type=TaskType.FEED,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.TWICE_DAILY,
    preferred_time=time(7, 30),
))

whiskers.add_task(Task(
    name="Playtime",
    task_type=TaskType.ENRICHMENT,
    duration_minutes=15,
    priority=Priority.LOW,
    frequency=Frequency.DAILY,
))

whiskers.add_task(Task(
    name="Brushing",
    task_type=TaskType.GROOMING,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    frequency=Frequency.WEEKLY,
))

# --- Generate Plan ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan(date.today())

# --- Print Schedule ---
print("=" * 45)
print(f"  TODAY'S SCHEDULE — {plan.date.strftime('%A, %b %d %Y')}")
print(f"  Owner: {owner.name}  |  Budget: {owner.available_minutes} min")
print("=" * 45)

if plan.scheduled_tasks:
    for st in plan.scheduled_tasks:
        pet_name = st.task.pet.name if st.task.pet else "?"
        print(
            f"  {st.start_time.strftime('%I:%M %p')} → {st.end_time.strftime('%I:%M %p')}"
            f"  [{pet_name}] {st.task.name}"
            f"  ({st.task.duration_minutes} min, {st.task.priority.name})"
        )
else:
    print("  No tasks scheduled.")

print("-" * 45)
print(f"  Total scheduled: {plan.get_total_scheduled_time()} min")

if plan.unscheduled_tasks:
    print(f"\n  Skipped ({len(plan.unscheduled_tasks)} task(s) didn't fit):")
    for task in plan.unscheduled_tasks:
        pet_name = task.pet.name if task.pet else "?"
        print(f"    • [{pet_name}] {task.name} ({task.duration_minutes} min)")

print("\n--- Reasoning ---")
print(plan.get_explanation())
