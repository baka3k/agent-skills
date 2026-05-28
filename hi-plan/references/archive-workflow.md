# Archive Workflow

## Step 1: Read Plans
Read plan.md + first 20 lines of each phase-*.md.

## Step 2: Journal (optional)
Ask user: document plans with /hi:journal? If yes -> journal-writer agent -> ./docs/journals/

## Step 3: Confirm
Ask user: archive specific plans or all completed? Delete or move to ./plans/archive?

## Step 4: Archive
- Move to ./plans/archive, OR
- Delete permanently: rm -rf

## Step 5: Git (optional)
Ask user: stage+commit or stage+commit+push via /hi:git

## Output
- Plans archived/deleted count
- Table: title, status, created date
- Journal entries created
