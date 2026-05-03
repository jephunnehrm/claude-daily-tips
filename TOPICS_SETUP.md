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
    "2026-05-03": "specific topic for this date",
    "2026-05-04": "another scheduled topic"
  },
  "used_topics": ["topic already generated", "another used topic"],
  "available_topics": ["all possible topics to choose from"]
}
```

## How to Use

### 1. Schedule a Topic for a Specific Date

Edit `topics.json` and add an entry under `scheduled`:

```json
{
  "scheduled": {
    "2026-05-05": "advanced MCP server patterns",
    "2026-05-06": "optimizing Claude Code performance"
  }
}
```

When the script runs on 2026-05-05, it will use the scheduled topic instead of selecting randomly.

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

## Tips

- **Batch scheduling**: Add multiple dates at once in `scheduled` before a campaign
- **Avoid conflicts**: If a date has both scheduled and used topics, scheduled takes priority
- **Rollback**: If you want to reuse a topic, remove it from `used_topics` and re-run
- **Track cycles**: Check `used_topics` length to know where you are in the topic cycle

## Integration with CI/CD

The `generate_post.py` script automatically:
- Reads `topics.json` at runtime
- Updates `used_topics` after each generation
- Works seamlessly with GitHub Actions daily workflows

No additional setup required — just commit your `topics.json` changes and the workflow will use them.
