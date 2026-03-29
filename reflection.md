# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The UML design consists of 6 classes and 3 enums.

Owner — holds the pet owner's profile and daily time budget (available_minutes, preferred_start_time, preferred_end_time). Responsible for managing the list of pets.
Pet — stores an individual animal's details (species, breed, age, weight, health notes) and owns a list of Task objects. Responsible for task management per pet.
Task — represents a single care activity (walk, feed, meds, etc.). Holds scheduling-relevant data: duration_minutes, priority, frequency, and an optional preferred_time for time-sensitive tasks like medications.
ScheduledTask — a decorator around Task that adds a concrete start_time and end_time. Keeps the original Task data clean while representing placement in the day.
DailyPlan — the output of the scheduler. Holds two lists: tasks that were successfully scheduled and tasks that couldn't fit. Also stores a reasoning log explaining decisions.
Scheduler — the only class with real algorithmic logic. Takes an Owner and produces a DailyPlan by prioritizing tasks, fitting them within available time, assigning time slots, and building a human-readable explanation.
The three enums (TaskType, Priority, Frequency) keep allowed values explicit and prevent invalid inputs like typos in strings.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
