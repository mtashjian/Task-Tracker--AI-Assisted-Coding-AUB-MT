# Mid-course reflection

I completed the midcourse project in Cursor IDE, using the Cursor Grok 4.6 agent. I followed the course loop of ask, inspect, run, test, and refine.

I started by letting Cursor inspect the actual repository and summarize what currently existed. I then corrected the AI assumptions that needed human intervention. After that I drafted three to six user stories per feature, confirmed their acceptance criteria, and prepared the related markdown file. Before writing code, I prepared an incremental plan for each feature. I then prepared the backend and the frontend.

AI helped me write the user stories, acceptance criteria, frontend, backend, and pytest scenarios. That was the main stretch where the agent carried the drafting. I let it create pytest scenarios for both features. I tested those scenarios in pytest, let them break, and reset the production code. Before refactoring, I asked for a contract to be locked. I then refactored the UI so the New Task button and validation errors display properly.

AI slowed me down when it directly accepted my assumption on due date, without warning me about in-memory storage and what the consequences might be. During initial browser tests I realized due date cannot be handled server-side, because we cannot have Overdue when storage is in memory. I was obliged to change the UI to accept overdue on create and edit of cards, and only color the card red. For that change, AI suggested seeding the application with overdue cards so I could test the red cards. I rejected that suggestion.

My review of the drag-and-drop logic changed the result. The case I reviewed was when status did not change, but the card was updated.
