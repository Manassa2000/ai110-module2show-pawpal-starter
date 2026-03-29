from datetime import date, time

from pawpal_system import (
    Owner, Pet, Task, ScheduledTask,
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
buddy    = Pet(name="Buddy",    species="Dog", breed="Labrador", age=3.0, weight=30.0)
whiskers = Pet(name="Whiskers", species="Cat", breed="Siamese",  age=5.0, weight=4.5)

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Add Tasks OUT OF ORDER (intentionally scrambled times) ---
buddy.add_task(Task(
    name="Evening Walk",
    task_type=TaskType.WALK,
    duration_minutes=20,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
    preferred_time=time(18, 0),       # 6:00 PM — added first
))

whiskers.add_task(Task(
    name="Playtime",
    task_type=TaskType.ENRICHMENT,
    duration_minutes=15,
    priority=Priority.LOW,
    frequency=Frequency.DAILY,
                                      # no preferred_time — should sink to bottom
))

buddy.add_task(Task(
    name="Flea Medication",
    task_type=TaskType.MEDS,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.WEEKLY,
    preferred_time=time(8, 0),        # 8:00 AM — added second
    notes="Apply between shoulder blades",
    completed=True,                   # already done — for filter demo
))

whiskers.add_task(Task(
    name="Breakfast",
    task_type=TaskType.FEED,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.TWICE_DAILY,
    preferred_time=time(7, 30),       # 7:30 AM — added third
))

buddy.add_task(Task(
    name="Morning Walk",
    task_type=TaskType.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 0),        # 7:00 AM — added last
))

whiskers.add_task(Task(
    name="Brushing",
    task_type=TaskType.GROOMING,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    frequency=Frequency.WEEKLY,
                                      # no preferred_time
))

scheduler = Scheduler(owner)

# Give tasks explicit due dates so next-occurrence math is clear
morning_walk = buddy.tasks[-1]          # Morning Walk (added last)
morning_walk.due_date = date.today()

breakfast = whiskers.tasks[1]           # Breakfast
breakfast.due_date = date.today()

flea_med = buddy.tasks[1]              # Flea Medication (weekly)
flea_med.due_date = date.today()

all_tasks = owner.get_all_tasks()

# ------------------------------------------------------------------ #
# DEMO 1: sort_by_time()
# ------------------------------------------------------------------ #
print("=" * 50)
print("  SORT BY TIME (tasks added out of order)")
print("=" * 50)
sorted_tasks = scheduler.sort_by_time(all_tasks)
for t in sorted_tasks:
    pin = t.preferred_time.strftime("%I:%M %p") if t.preferred_time else "no time set"
    pet = t.pet.name if t.pet else "?"
    print(f"  {pin:<12}  [{pet}] {t.name}")

# ------------------------------------------------------------------ #
# DEMO 2: filter_tasks() — incomplete tasks only
# ------------------------------------------------------------------ #
print("\n" + "=" * 50)
print("  FILTER: incomplete tasks only (completed=False)")
print("=" * 50)
incomplete = scheduler.filter_tasks(all_tasks, completed=False)
for t in incomplete:
    pet = t.pet.name if t.pet else "?"
    print(f"  [{pet}] {t.name}  (done={t.completed})")

# ------------------------------------------------------------------ #
# DEMO 3: filter_tasks() — Buddy's tasks only
# ------------------------------------------------------------------ #
print("\n" + "=" * 50)
print("  FILTER: Buddy's tasks only (pet_name='Buddy')")
print("=" * 50)
buddy_tasks = scheduler.filter_tasks(all_tasks, pet_name="Buddy")
for t in buddy_tasks:
    print(f"  {t.name}  |  priority={t.priority.name}  |  done={t.completed}")

# ------------------------------------------------------------------ #
# DEMO 4: filter_tasks() — Buddy's incomplete tasks (both filters)
# ------------------------------------------------------------------ #
print("\n" + "=" * 50)
print("  FILTER: Buddy's incomplete tasks (both filters)")
print("=" * 50)
buddy_incomplete = scheduler.filter_tasks(all_tasks, completed=False, pet_name="Buddy")
for t in buddy_incomplete:
    print(f"  {t.name}  |  priority={t.priority.name}")

# ------------------------------------------------------------------ #
# DEMO 5: Full daily schedule
# ------------------------------------------------------------------ #
print("\n" + "=" * 50)
print(f"  TODAY'S SCHEDULE — {date.today().strftime('%A, %b %d %Y')}")
print(f"  Owner: {owner.name}  |  Budget: {owner.available_minutes} min")
print("=" * 50)
plan = scheduler.generate_plan(date.today())
for st in plan.scheduled_tasks:
    pet_name = st.task.pet.name if st.task.pet else "?"
    print(
        f"  {st.start_time.strftime('%I:%M %p')} → {st.end_time.strftime('%I:%M %p')}"
        f"  [{pet_name}] {st.task.name}"
        f"  ({st.task.duration_minutes} min, {st.task.priority.name})"
    )
print("-" * 50)
print(f"  Total scheduled: {plan.get_total_scheduled_time()} min")

# ------------------------------------------------------------------ #
# DEMO 6: mark_task_complete() — auto-creates next occurrence
# ------------------------------------------------------------------ #
print("\n" + "=" * 50)
print("  MARK COMPLETE + AUTO-RECURRENCE")
print("=" * 50)

for task_to_complete, label in [
    (morning_walk, "Morning Walk (DAILY)"),
    (flea_med,     "Flea Medication (WEEKLY)"),
]:
    print(f"\nCompleting: {label}")
    print(f"  Before — tasks for {task_to_complete.pet.name}: {[t.name for t in task_to_complete.pet.tasks]}")
    next_task = scheduler.mark_task_complete(task_to_complete)
    print(f"  After  — tasks for {task_to_complete.pet.name}: {[t.name for t in task_to_complete.pet.tasks]}")
    if next_task:
        print(f"  Next occurrence: '{next_task.name}' due on {next_task.due_date} (completed={next_task.completed})")

# ------------------------------------------------------------------ #
# DEMO 7: detect_conflicts() — two tasks pinned to the same time
# ------------------------------------------------------------------ #
print("\n" + "=" * 50)
print("  CONFLICT DETECTION")
print("=" * 50)

# Manually build two ScheduledTasks that overlap: both start at 7:00 AM
walk_slot = ScheduledTask(
    task=morning_walk,
    start_time=time(7, 0),
    end_time=time(7, 30),   # 30 min walk
)
feed_slot = ScheduledTask(
    task=breakfast,
    start_time=time(7, 15), # starts mid-walk → conflict
    end_time=time(7, 20),
)
no_overlap_slot = ScheduledTask(
    task=flea_med,
    start_time=time(8, 0),  # after the walk → no conflict
    end_time=time(8, 5),
)

conflicting_slots = [walk_slot, feed_slot, no_overlap_slot]
warnings = scheduler.detect_conflicts(conflicting_slots)

if warnings:
    for w in warnings:
        print(f"  ⚠️  {w}")
else:
    print("  No conflicts found.")

# Verify clean schedule produces no warnings
print("\nChecking today's generated plan for conflicts...")
plan_warnings = scheduler.detect_conflicts(plan.scheduled_tasks)
if plan_warnings:
    for w in plan_warnings:
        print(f"  ⚠️  {w}")
else:
    print("  No conflicts in today's plan.")
