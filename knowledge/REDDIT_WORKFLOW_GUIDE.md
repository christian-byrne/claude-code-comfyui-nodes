# Reddit to Video Workflow Guide

This guide shows how to create TikTok/YouTube Shorts scripts from Reddit threads using the Claude Code ComfyUI nodes.

## Workflow Steps

### Step 1: Scrape Reddit Comments

Use the **Claude Reddit Scraper** node:

1. **Source Type**: `subreddit` 
2. **Source**: `programming` (or any subreddit)
3. **Scrape Mode**: `comments` (default)
4. **Max Items**: `10` (number of posts to check)
5. **Sort By**: `hot` (most active discussions)
6. **Max Comment Depth**: `3` (deep enough for good threads)

The node will:
- Find posts with the most comments (20+)
- Click into the most active thread
- Scrape all comments with full hierarchy
- Save structured JSON data

### Step 2: Convert to Video Script

Use the **Claude Code Execute** node with the video script command:

1. Connect the Reddit scraper output to the Execute node
2. Use this command in the Execute node:

```markdown
# Reddit to TikTok Video Script Generator

Take Reddit thread data and create a 45-60 second narrated video script for TikTok/YouTube Shorts.

**INPUT:** Use the Reddit thread data from the previous node

**OUTPUT:** Create a video script with this exact format:

# VIDEO SCRIPT: [Post Title - First 50 chars]

## HOOK (0-5 seconds)
[Dramatic opener that grabs attention]

## SETUP (5-18 seconds)  
NARRATOR: [Explain the post/question in simple terms]

## COMMENTS (18-50 seconds)
NARRATOR: [Transition to comments]

**TOP COMMENT** (Score: XXX)
"[Quote most upvoted comment - max 2 sentences]"

NARRATOR: [Brief reaction/transition]

**SPICY TAKE** (Score: XXX)  
"[Quote controversial or surprising comment]"

NARRATOR: [Another transition]

**FINAL WORD** (Score: XXX)
"[Quote insightful/funny closing comment]"

## WRAP-UP (50-60 seconds)
NARRATOR: [Quick conclusion + engagement question]

---
ORIGINAL POST: [Title] by u/[author] ([score] upvotes)
COMMENTS USED: [count] comments, [depth] levels deep
TONE: [dramatic/funny/educational/controversial]

## Requirements:
1. Hook must grab attention immediately
2. Keep narrator text conversational 
3. Select 3-4 comments maximum that are highly upvoted, controversial, or funny
4. Simplify technical terms for general audience
5. Build narrative tension with transitions
6. End with viewer engagement
7. Time each section for 45-60 seconds total
```

### Step 3: Output

The workflow will produce:

1. **Scraped Reddit Data** (JSON format):
   - Complete thread hierarchy
   - Post and comment metadata
   - Engagement metrics

2. **Video Script** (Markdown format):
   - Timed narration segments
   - Selected quotes from top comments
   - Production notes and source material

## Example Output

```
# VIDEO SCRIPT: My boss told me to make the website load faster

## HOOK (0-5 seconds)
Developer accidentally becomes a GENIUS by doing the WRONG thing!

## SETUP (5-18 seconds)  
NARRATOR: So this programmer's boss was complaining their website was too slow...

## COMMENTS (18-50 seconds)
**TOP COMMENT** (Score: 892)
"This is actually brilliant. Half of web development is just removing unnecessary stuff."

NARRATOR: Wait, so they accidentally did the RIGHT thing?

**SPICY TAKE** (Score: 567)  
"Found the guy who adds 17 different animation libraries to display a button"

## WRAP-UP (50-60 seconds)
NARRATOR: Sometimes the best code is NO code. Have YOU ever fixed something by breaking it?
```

## Tips for Best Results

### Reddit Source Selection
- Choose active subreddits (r/programming, r/webdev, r/ProgrammerHumor)
- Look for posts with 50+ comments for rich discussions
- Controversial topics generate more engaging content

### Script Optimization
- Focus on drama, conflict, and surprising twists
- Use conversational tone, not technical documentation
- Include humor when comments are naturally funny
- End with questions to drive engagement

### Production Notes
- Each script includes timing estimates
- Source material is preserved for fact-checking
- Suggested tone and hashtags provided
- Visual cues noted for video editing

## Command Files

Pre-made command files are available in `/commands/`:
- `reddit-to-video-script.md` - Detailed version with full instructions
- `reddit-video-script-simple.md` - Concise version for quick use

Use these with the Claude Code Execute node by copying the content into the command field.