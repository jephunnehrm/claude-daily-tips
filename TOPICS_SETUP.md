# Topic Generation Configuration

This guide explains how to prepare and schedule topics for daily post generation.

## Overview

The post generation system now supports:
- **Scheduled topics**: Pre-plan specific topics for specific dates
- **Auto-generation**: Randomly select from available topics when no schedule exists
- **Uniqueness tracking**: Prevents topic repetition across generations
- **Manual control**: Edit `topics.json` to add/modify topics anytime

## File Structure

### `topics.json`

```json
{
  "scheduled": {
    "2026-05-03": ["topic 1", "topic 2"],
    "2026-05-04": ["single topic for this day"]
  },
  "used_topics": ["topic already generated", "another used topic"],
  "available_topics": ["all possible topics to choose from"]
}
```

**Note:** `scheduled` topics can be:
- A **string** (single topic): `"2026-05-03": "specific topic"`
- An **array** (multiple topics): `"2026-05-03": ["topic 1", "topic 2"]`

## How to Use

### 1. Schedule Topics for Specific Dates

Edit `topics.json` and add an entry under `scheduled`. You can schedule:

**Single topic per day:**
```json
{
  "scheduled": {
    "2026-05-05": ["advanced MCP server patterns"],
    "2026-05-06": ["optimizing Claude Code performance"]
  }
}
```

**Multiple topics per day:**
```json
{
  "scheduled": {
    "2026-05-05": [
      "advanced MCP server patterns",
      "basic MCP troubleshooting"
    ]
  }
}
```

**How it works:**
- When the script runs on 2026-05-05 with multiple topics, it generates the first topic
- Run the script again on the same day to generate the second topic
- Each run uses the next topic in the list that doesn't have a post yet
- Once all scheduled topics for that day have posts, subsequent runs skip

### 2. Add New Available Topics

Add topics to the `available_topics` list:

```json
{
  "available_topics": [
    "existing topics...",
    "my new topic idea here"
  ]
}
```

### 3. How the Script Works

**Flow for each run:**

1. Check if today's date has a scheduled topic → use it
2. If no scheduled topic:
   - Pick a random topic from `available_topics` that's not in `used_topics`
   - Add it to `used_topics`
   - Save the updated `topics.json`
3. If all topics are used, reset the cycle and start from the full list

### 4. Example Workflow

**Day 1 (2026-05-03)**: Scheduled topic exists
```
Input:  scheduled["2026-05-03"] = "Claude Code for documentation"
Output: Uses that topic, doesn't mark as "used"
```

**Day 2 (2026-05-04)**: No scheduled topic
```
Input:  available_topics has 30 items, used_topics has 20
Output: Picks 1 of the 10 unused topics randomly
        Adds it to used_topics
        Saves updated topics.json
```

**Day 30+**: All topics exhausted
```
Input:  available_topics has 30 items, used_topics has 30
Output: Warns "All topics used, resetting for new cycle"
        Resets used_topics to empty
        Picks a random topic from all 30
```

## Multiple Posts Per Day

If you want to generate multiple posts on the same day:

1. Add multiple topics to the `scheduled` entry for that date:
```json
{
  "scheduled": {
    "2026-05-10": [
      "topic for first post",
      "topic for second post",
      "topic for third post"
    ]
  }
}
```

2. Run the script multiple times on that day:
```bash
# First run: generates post for "topic for first post"
python scripts/generate_post.py

# Second run: generates post for "topic for second post"
python scripts/generate_post.py

# Third run: generates post for "topic for third post"
python scripts/generate_post.py

# Fourth run: skips (all scheduled topics done)
python scripts/generate_post.py
```

## Tips

- **Batch scheduling**: Add multiple dates at once in `scheduled` before a campaign
- **Multiple posts same day**: Use an array of topics for the same date
- **Avoid conflicts**: Scheduled topics always take priority over auto-generated ones
- **Rollback**: If you want to reuse a topic, remove it from `used_topics` and re-run
- **Track cycles**: Check `used_topics` length to know where you are in the topic cycle

## Integration with CI/CD

The `generate_post.py` script automatically:
- Reads `topics.json` at runtime
- Updates `used_topics` after each generation
- Works seamlessly with GitHub Actions daily workflows

No additional setup required — just commit your `topics.json` changes and the workflow will use them.
