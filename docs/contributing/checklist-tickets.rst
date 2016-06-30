.. _checklist-tickets:

=================
Ticket Checklists
=================


Ticket Description
==================

In general these things really matter in the description:

- Reasoning / Rationale. Explain "WHY" it makes sense and is important.

- How to reproduce. Easy to follow steps, that’s important.

  - Observation: The problem (short)

  - Expectation: How it should be (short)

- Specs: It is fine to draft them as good as it works.

  If anything is unclear, please ask for a review or help on this via the
  Community Portal or Slack channel.


Checklists for Tickets
======================

BUG
---

Definition: An existing function that does not work as expected for the user.

- Problem description
- Steps needed to recreate (gherkin)
- Link to the screen in question and/or description of how to find it via 
  navigation
- Explanation of what the expected outcome is
- Any hints into the source of the problem
- Information about platform/browser/db/etc. where applicable
- Examples of other similar cases which have different behaviour

DESIGN
------

Definition: Styling and user interface issues, including cosmetic improvements
or appearance and behaviour of frontend functionality.

- Screenshot/animation of existing page/behaviour
- Sketches or wireframes if available
- Link to the screen in question and/or description of how to find it via 
  navigation
- Problem description
- Explanation of what the expected outcome is
- Since this may be examined by a designer; it should be written in a way that a
  non-developer can understand

EPIC
----

Definition: A collection of tickets which together complete a larger overall
project.

- Benefit explanation
- Clear objective - when is this complete?
- Explanations of exceptions/corner cases
- Documentation subtask
- Comprehensive wireframes and/or design subtasks
- Links to subtasks

FEATURE
-------

Definition: A new function in the software which previously did not exist.

- Benefit explanation
- Clear objective
- Explanations of exceptions/corner cases
- Documentation subtask
- Comprehensive wireframes and/or design subtasks

SUPPORT
-------

Definition: An issue related to a customer report.

- Link to support ticket, if available
- Problem description
- Steps needed to recreate (gherkin)
- Link to the screen in question and/or description of how to find it via 
  navigation
- Explanation of what the expected outcome is
- Any hints into the source of the problem
- Information about platform/browser/db/etc. where applicable
- Examples of other similar cases which have different behaviour

TASK
----

Definition: An improvement or step towards implementing a feature or fixing
a bug. Includes refactoring and other tech debt.

- Clear objective
- Benefit explanation
- Links to parent/related tickets


All details below.


External links:

- Avoid linking to external images; they disappear over time. Please attach any
  relevant images to the ticket itself.

- External links in general: They also disappear over time, consider copying the
  relevant bit of information into a comment or write a paragraph to sum up the
  general idea.


Hints
=====

Change Description
------------------

It can be tricky to figure out how to change the description of a ticket. There
is a very small pencil which has to be clicked once you see the edit form of a
ticket.


.. figure:: images/redmine-description.png
   :alt: Example of pencil to change the ticket description

   Shows an example of the pencil which lets you change the description.

