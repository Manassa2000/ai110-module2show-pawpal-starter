from pawpal_system import Task, Pet, TaskType, Priority, Frequency


def make_task(name="Morning Walk") -> Task:
    return Task(
        name=name,
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3.0, weight=30.0)
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Morning Walk"))
    pet.add_task(make_task("Evening Walk"))
    assert len(pet.tasks) == 2
