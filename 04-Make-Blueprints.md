# 🎙 ️ FirasAi Complete Bundle — Part 4
## Section 6: Make.com Automation Blueprints

---

## Blueprint 1: Episode Publishing Pipeline

### Scenario Flow

```
MODULE 1: Webhook Trigger
├── Webhook Name: "FirasAi Episode Ready to Publish"
└── Trigger: POST request with episode data

MODULE 2: Iterator
├── Iterates through: Episode metadata
└── Creates variables for next steps

MODULE 3: Buzzsprout - Upload Episode
├── API: POST https://api.buzzsprout.com/v2/podcasts/{podcast_id}/episodes
├── Headers:
│   └── Authorization: Token token={{BUZZSPROUT_API_KEY}}
├── Body (JSON):
│   {
│     "title": "{{1.title}}",
│     "audio_url": "{{1.audio_url}}",
│     "description": "{{1.show_notes}}",
│     "published_at": "{{1.publish_date}}",
│     "episode_number": "{{1.episode_number}}",
│     "season_number": 1,
│     "explicit": false
│   }
└── Save: episode_id → Variable

MODULE 4: Captivate - Schedule Distribution
├── API: POST https://api.captivate.fm/v1/episodes
├── Headers:
│   ├── Authorization: Bearer {{CAPTIVATE_API_KEY}}
│   └── Content-Type: application/json
├── Body (JSON):
│   {
│     "title": "{{1.title}}",
│     "show_notes": "{{1.show_notes}}",
│     "audio_file": "{{1.audio_url}}",
│     "status": "scheduled",
│     "publish_date": "{{1.publish_date}}"
│   }
└── Distributes to: Spotify, Apple, Google, YouTube

MODULE 5: Beehiiv - Create Email
├── API: POST https://api.beehiiv.com/v2/publications/{pub_id}/posts
├── Headers:
│   ├── Authorization: Bearer {{BEEHIIV_API_KEY}}
│   └── Content-Type: application/json
├── Body (JSON):
│   {
│     "title": "New FirasAi Episode: {{1.title}}",
│     "content": "{{1.newsletter_content}}",
│     "status": "draft",
│     "email_subject_line": "{{1.subject_line}}",
│     "email_preview_text": "{{1.preview_text}}",
│     "send_at": "{{1.publish_date}}"
│   }

MODULE 6: Buffer - Schedule Social Posts
├── API: POST https://api.bufferapp.com/1/updates/create.json
├── Headers:
│   └── Authorization: Bearer {{BUFFER_ACCESS_TOKEN}}
├── For each platform (loop):
│   {
│     "profile_ids": ["{{PLATFORM_ID}}"],
│     "text": "{{1.social_post}}",
│     "scheduled_at": "{{1.publish_date}}",
│     "media": {
│       "link": "{{1.episode_link}}",
│       "thumbnail": "{{1.cover_image}}"
│     }
│   }

MODULE 7: Notion - Update Episode Status
├── API: PATCH https://api.notion.com/v1/pages/{page_id}
├── Headers:
│   ├── Authorization: Bearer {{NOTION_API_KEY}}
│   ├── Notion-Version: 2022-06-28
│   └── Content-Type: application/json
├── Body (JSON):
│   {
│     "properties": {
│       "Status": {
│         "select": { "name": "✅ Published" }
│       },
│       "Downloads": { "number": { "value": 0 } }
│     }
│   }

MODULE 8: Slack - Send Notification
├── Webhook URL: {{SLACK_WEBHOOK}}
├── Message:
│   "🎉 New FirasAi episode published!"
│   "Title: {{1.title}}"
│   "Links: {{1.all_links}}"
│   "Performance: Coming soon 📊"

MODULE 9: Error Handler
├── Catches: HTTP errors, API failures
├── Sends: Alert to admin email
└── Logs: To Google Sheet "Make Errors"
```

---

## Blueprint 2: AI Content Generation Engine

### Scenario Flow

```
MODULE 1: Schedule Trigger
├── Frequency: Every Monday 9:00 AM
└── Timezone: User's timezone

MODULE 2: HTTP - Perplexity Research
├── Method: POST
├── URL: https://api.perplexity.ai/chat/completions
├── Headers:
│   └── Authorization: Bearer {{PERPLEXITY_API_KEY}}
├── Body (JSON):
│   {
│     "model": "llama-3.1-sonar-large-128k-online",
│     "messages": [{
│       "role": "user",
│       "content": "Find 5 trending topics in AI, crypto, finance, and sports with unique angles for FirasAi podcast episodes"
│     }]
│   }
└── Save: response to variable

MODULE 3: HTTP - OpenAI Script Generation
├── Method: POST
├── URL: https://api.openai.com/v1/chat/completions
├── Headers:
│   └── Authorization: Bearer {{OPENAI_API_KEY}}
├── Body (JSON):
│   {
│     "model": "gpt-4",
│     "messages": [{
│       "role": "system",
│       "content": "You are the FirasAi podcast scriptwriter..."
│     }, {
│       "role": "user",
│       "content": "Based on these topics: {{2.response}}, create 5 episode outlines with hooks, talking points, and a 15-min script for topic #1"
│     }],
│     "temperature": 0.7
│   }

MODULE 4: Notion - Create Episode Pages
├── For each of 5 topics:
│   ├── POST to Notion API
│   ├── URL: https://api.notion.com/v1/pages
│   ├── Headers: Bearer + Notion-Version
│   ├── Parent: { "database_id": "{{EPISODES_DB_ID}}" }
│   ├── Properties:
│   │   {
│   │     "Title": { "title": [{ "text": { "content": "{{topic_title}}" } }] },
│   │     "Status": { "select": { "name": "💡 Idea" } },
│   │     "Topic": { "multi_select": [{ "name": "{{topic_tag}}" }] }
│   │   }
│   └── Body: { "children": [outline blocks] }

MODULE 5: Gmail - Send Summary
├── To: {{HOST_EMAIL}}
├── Subject: "🎙 ️ Your 5 New FirasAi Episode Ideas for This Week"
├── Body: HTML with clickable Notion links
└── Attach: Notion database URL

MODULE 6: Slack Notification
└── Posts in #firasai-content channel
```

---

## Blueprint 3: Guest Outreach Automation

### Scenario Flow

```
MODULE 1: Notion Trigger
├── Watch: Guests Database
├── Event: New item added
└── Condition: Status = "🎯 Prospect"

MODULE 2: HTTP - AI Personalization
├── Method: POST
├── URL: https://api.openai.com/v1/chat/completions
├── Body:
│   {
│     "model": "gpt-4",
│     "messages": [{
│       "role": "user",
│       "content": "Write personalized FirasAi outreach email to {{1.Name}}, {{1.Title}} at {{1.Company}}. Reference their work on {{1.recent_work}}. Podcast:
FirasAi, audience: entrepreneurs and investors interested in AI, crypto, finance, sports, downloads: {{DOWNLOADS}}. Keep under 200 words."
│     }]
│   }
└── Save: email_body variable

MODULE 3: Gmail - Send Email
├── To: {{1.Email}}
├── From: {{HOST_EMAIL}}
├── Subject: {{1.pitch_subject}}
├── Body: {{2.email_body}}
├── Tracking: Enable
└── Save: sent timestamp

MODULE 4: Notion - Update Guest
├── PATCH page {{1.Page_ID}}
├── Properties:
│   {
│     "Status": { "select": { "name": "📧 Outreach Sent" } },
│     "Last Contact": { "date": { "start": "{{now}}" } }
│   }

MODULE 5: Delay + Follow-up Scheduler
├── Wait: 5 days
├── Condition: Guest hasn't replied
└── If no reply: Create follow-up email draft

MODULE 6: Notion - Update with Reminder
├── Add to "This Week" view
└── Set Follow-up Date: +5 days from now
```

---

## Blueprint 4: Clip Generation & Distribution

### Scenario Flow

```
MODULE 1: Webhook - New Episode
├── Source: Buzzsprout webhook
└── Data: episode_id, audio_url, title

MODULE 2: HTTP - Transcribe with Whisper
├── Method: POST
├── URL: https://api.openai.com/v1/audio/transcriptions
├── Form Data:
│   ├── file: {{1.audio_url}}
│   ├── model: whisper-1
│   └── response_format: verbose_json
└── Save: full transcript with timestamps

MODULE 3: HTTP - Find Viral Moments
├── Method: POST
├── URL: https://api.openai.com/v1/chat/completions
├── Body:
│   {
│     "model": "gpt-4",
│     "messages": [{
│       "role": "user",
│       "content": "Analyze this FirasAi transcript and find 10 moments that would make great 30-90 second viral clips. Return JSON array with: {start_time,
end_time, hook, virality_score (1-10), suggested_caption}. Transcript: {{2.text}}"
│     }]
│   }
└── Parse: JSON array

MODULE 4: Iterator - For Each Clip
└── Loops through 10 clips

MODULE 5: HTTP - Opus Clip API
├── Method: POST
├── URL: https://api.opus.pro/v1/clips
├── Body:
│   {
│     "video_url": "{{1.video_url}}",
│     "start_time": "{{clip.start_time}}",
│     "end_time": "{{clip.end_time}}",
│     "aspect_ratio": "9:16",
│     "captions": true
│   }
└── Save: clip_url

MODULE 6: HTTP - Generate Social Captions
├── Method: POST
├── URL: https://api.openai.com/v1/chat/completions
├── Body:
│   {
│     "model": "gpt-4",
│     "messages": [{
│       "role": "user",
│       "content": "Write 3 social captions for this FirasAi podcast clip. Platforms: TikTok, Instagram, LinkedIn. Hook: {{clip.hook}}. Transcript: {{clip.text}}"
│     }]
│   }

MODULE 7: Google Drive - Save Clip
├── Upload to: /FirasAi/Clips/{{Episode_Title}}/
└── Name: clip_{{index}}.mp4

MODULE 8: Buffer - Schedule Posts
├── For each platform:
│   ├── POST to Buffer API
│   ├── Text: {{6.captions}}
│   ├── Media: {{5.clip_url}}
│   ├── Scheduled: staggered times (9am, 12pm, 3pm, 6pm)
│   └── Platforms: TikTok, Reels, Shorts, LinkedIn

MODULE 9: Notion - Log Clip
└── Create entry in Clips Database
```

---

## Blueprint 5: Weekly Analytics Report

### Scenario Flow

```
MODULE 1: Schedule - Every Sunday 8 PM
└── Triggers weekly review

MODULE 2: HTTP - Buzzsprout Stats
├── GET https://api.buzzsprout.com/v2/podcasts/{id}/episodes
├── Get last 7 days
└── Extract: downloads, completion, ratings

MODULE 3: HTTP - Captivate Analytics
├── GET https://api.captivate.fm/v1/analytics
├── Period: last_week
└── Save: list_performance

MODULE 4: HTTP - Buffer Performance
├── GET https://api.bufferapp.com/1/updates?profile_ids={{id}}
└── Extract: reach, engagement, clicks

MODULE 5: HTTP - Beehiiv Stats
├── GET https://api.beehiiv.com/v2/publications/{id}/stats
└── Save: open_rate, click_rate, new_subscribers

MODULE 6: Aggregate Data
├── Combine all metrics
├── Calculate: growth %, best episode, top clip
└── Format: JSON report

MODULE 7: HTTP - AI Analysis
├── OpenAI GPT-4 prompt:
│   "Analyze this week's FirasAi podcast data and provide:
│   1. 3 wins
│   2. 3 improvements
│   3. 2 experiments for next week
│   4. Predicted next week performance
│   Data: {{6.json}}"
└── Save: insights

MODULE 8: Notion - Create Report Page
├── Database: Performance Reports
├── Properties: Week, Date, Total Downloads, Growth
├── Body: Full report with insights
└── Share: Host only

MODULE 9: Email + Slack
├── Send full report via email
├── Post summary in #firasai-analytics
└── Include: "Top 3 actions for next week"
```

---

## Blueprint 6: Newsletter Automation

### Scenario Flow

```
MODULE 1: Schedule - Every Friday 10 AM
└── Sends weekly digest

MODULE 2: Notion - Query This Week's Episodes
├── Filter: Status = "✅ Published" AND Publish Date = This Week
└── Save: list of episodes

MODULE 3: HTTP - Generate Newsletter
├── OpenAI prompt:
│   "Create a FirasAi newsletter for these episodes: {{2.episodes}}.
│   Include: intro, episode summaries, 1 behind-scenes story, CTA.
│   Tone: Personal, like a friend, bold and insightful."
└── Save: html_content

MODULE 4: Beehiiv - Create & Schedule
├── POST to /posts
├── Status: scheduled
├── Send at: Friday 6 PM
└── Returns: post_id

MODULE 5: Track in Notion
└── Log newsletter in Content Calendar
```

---

## Required API Keys & Setup

### API Keys You Need

```
1. OpenAI API Key
   - Get from: platform.openai.com
   - Used for: Script generation, content creation, analysis
   - Cost: Pay per use (~$20-50/month for active podcast)

2. Perplexity API Key
   - Get from: perplexity.ai/settings/api
   - Used for: Research, fact-checking
   - Cost: $20/month for Pro

3. Notion API Key
   - Get from: notion.so/my-integrations
   - Used for: Database operations
   - Cost: Free

4. Buzzsprout API Key
   - Get from: buzzsprout.com/settings/integrations
   - Used for: Podcast hosting and distribution
   - Cost: $12/month (included in plan)

5. Beehiiv API Key
   - Get from: beehiiv.com/settings/integrations
   - Used for: Newsletter sending
   - Cost: Free-$99/month

6. Buffer Access Token
   - Get from: buffer.com/settings/apps
   - Used for: Social media scheduling
   - Cost: Free-$6/month

7. Slack Webhook URL
   - Get from: api.slack.com/messaging/webhooks
   - Used for: Team notifications
   - Cost: Free

8. ElevenLabs API Key
   - Get from: elevenlabs.io/settings
   - Used for: AI voice generation
   - Cost: $5-22/month
```

### Environment Variables to Set

```bash
# Make.com Environment Variables
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
NOTION_API_KEY=secret_...
BUZZSPROUT_API_KEY=...
BUZZSPROUT_PODCAST_ID=...
BEEHIIV_API_KEY=...
BEEHIIV_PUBLICATION_ID=...
BUFFER_ACCESS_TOKEN=...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
ELEVENLABS_API_KEY=...
```

---

## Make.com Setup Instructions

### Step 1: Create Free Account
1. Go to make.com
2. Sign up (free tier includes 1,000 operations/month)
3. Verify email

### Step 2: Create First Scenario
1. Click "Create a new scenario"
2. Click the big "+" button to add first module
3. Search for "Webhook" → Select "Custom webhook"
4. Name it: "FirasAi Episode Ready"
5. Copy the webhook URL
6. This URL will be triggered when an episode is ready

### Step 3: Add Modules
1. Click "+" to add next module
2. Search for "HTTP" → Select "Make a request"
3. Configure with the API call details from Blueprints above
4. Add your API key in the Headers section
5. Test the connection

### Step 4: Connect Modules
1. Drag from one module's output to next module's input
2. Map variables using {{1.variable_name}} syntax
3. Use the Iterator module for loops

### Step 5: Add Error Handling
1. Right-click any module
2. Add error handler
3. Configure to send email on failure
4. Log errors to Google Sheet

### Step 6: Schedule Triggers
1. For time-based scenarios, use "Schedule" module
2. Set frequency (daily, weekly, etc.)
3. Set time and timezone

### Step 7: Test & Activate
1. Click "Run once" to test
2. Check execution log for errors
3. Fix any issues
4. Toggle "Scheduling" to ON
5. Scenario runs automatically

---

## Pro Tips for Make.com

### Tip 1: Use Bundles
When iterating through arrays, use the Iterator module to process items one at a time.

### Tip 2: Add Filters
Use Filter modules to only continue if conditions are met (e.g., only send email if email is valid).

### Tip 3: Use Webhooks
Instead of polling, use webhooks for real-time triggers from Notion, Stripe, etc.

### Tip 4: Error Handling
Always add error handlers to critical workflows. Better to know about failures than have silent broken processes.

### Tip 5: Documentation
Add notes to each module explaining what it does. You'll thank yourself later.

### Tip 6: Start Simple
Don't try to automate everything at once. Start with one workflow, get it working, then add more.

---

## Cost Estimate for Make.com

### Free Tier
- 1,000 operations/month
- 2 active scenarios
- 15-minute scheduling intervals
- Good for: Testing, small podcasts

### Core Plan ($9/month)
- 10,000 operations/month
- 10 active scenarios
- 1-minute scheduling intervals
- Good for: Most podcasts

### Pro Plan ($16/month)
- 10,000 operations/month
- 50 active scenarios
- Webhooks, unlimited scheduling
- Good for: Growing podcasts

### Teams Plan ($29/month)
- 10,000 operations/month
- 500 active scenarios
- Team collaboration
- Good for: Large operations

### Operations Usage Estimate
For FirasAi:
- Publishing pipeline: ~15 operations per episode
- AI content generation: ~10 operations per week
- Guest outreach: ~5 operations per outreach
- Clip generation: ~30 operations per episode
- Analytics report: ~8 operations per week
- Newsletter: ~5 operations per week

**Total: ~100-150 operations per week = 400-600 per month**

The Core plan ($9/month) is perfect for starting out.
```