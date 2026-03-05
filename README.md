## TAP (Teaching Analysis Program)
- The goal of this program is to aid/support the analysis of instructors and their lessons


### Outline
##### FRAMEWORK:
- Entire "file" will be stored as a JSON and exported as .md (or .docx/PDF document with .md formatted content)
    - User will have the option of creating a "section" and "sub-section" within the lesson
    - Each should have time stamps and titles so that they can be analyzed for composition/content  and/or ratio of teaching/exercise time/etc.
        - Could show a pie-chart for subject-type ratio and lesson-content ratio in a PDF export
- There should be a Main title section upon the file init (and perhaps a name of the teacher and assessor)
- Program will use a parent-child referencing system for "subjects" (referred to as "exercises" within these notes)
    - Ex. Lesson (main subject) -> Section -> Sub-section or exercise -> Sub-Sub-section or exercise -> …
- Following page should be a "exercise" title and content section where the assessor can write notes in .md format
- The "exercise" should start a timer when it is started (or have the option to record a timer somewhere on the page)
    - "sub-exercises" should have independent timer that is nested within their parent "exercise"

##### LAYOUT:
- File option dropdown
    - New
    - Save (ctrl + S)
    - Save as… (ctrl + shift + S)
        
- Section title (may be pre-formatted to ## in .md and then smaller ### for sub-sections)
- Text content text box
- Table of the sections in a scrollable box on the left side
- Timer in the top right with an add to clipboard option (ideally a hot-key to start/stop the timer)