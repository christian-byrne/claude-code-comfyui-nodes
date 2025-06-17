# Reddit to TikTok Video Script Generator

Take Reddit thread data and create a 45-60 second narrated video script for TikTok/YouTube Shorts.

## Instructions

**INPUT:** Reddit thread JSON with post and comments data

**OUTPUT:** Create a video script with this exact format:

```
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
```

## Requirements:
1. **Hook must grab attention immediately** - use phrases like "This developer discovered...", "Reddit is losing it over...", "You won't believe what happened when..."

2. **Keep narrator text conversational** - like you're talking to a friend, not reading documentation

3. **Select 3-4 comments maximum** that are:
   - Highly upvoted (engaging)
   - Controversial (negative scores or heated debates)  
   - Funny or memorable
   - Provide different perspectives

4. **Simplify technical terms** - assume audience knows basic programming but not deep concepts

5. **Build narrative tension** - use phrases like "But then someone replied...", "The comments got heated when...", "Here's where it gets interesting..."

6. **End with engagement** - ask viewers to pick sides, share experiences, or follow for more

7. **Time each section** - aim for exactly 45-60 seconds total

8. **Preserve all source material** - include original post data and all comments used

Create scripts that turn programming discussions into engaging entertainment while staying true to the original content.