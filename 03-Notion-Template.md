🎙 ️ FirasAi Complete Bundle — Part 3
## Section 5: Notion Template Architecture

---

## Database 1: Episodes Master

```
Database Name: 🎙 ️ FirasAi Episodes
Properties:
├── Title (Title)
├── Status (Select)
│   ├── 💡 Idea
│   ├── 🔍 Researching
│   ├── ✍️ Scripting
│   ├── 🎤 Recording
│   ├── ✂️ Editing
│   ├── 📋 Show Notes
│   ├── 🚀 Scheduled
│   └── ✅ Published
├── Episode # (Number)
├── Publish Date (Date)
├── Topic (Multi-select)
│   ├── AI & Business
│   ├── Finance & Markets
│   ├── Crypto & Web3
│   ├── NFT & Digital Assets
│   ├── Sports Business
│   └── Macro & Trends
├── Format (Select)
│   ├── Solo Deep-Dive
│   ├── Expert Interview
│   ├── Market Analysis
│   ├── Hot Take
│   ├── Tutorial
│   └── Roundtable
├── Guest (Relation → Guests DB)
├── Length (Select)
│   ├── 15 min
│   ├── 30 min
│   ├── 45 min
│   └── 60+ min
├── Script (Files & Media)
├── Audio File (Files & Media)
├── Show Notes (Rich Text)
├── Transcripts (Files & Media)
├── Clips (Relation → Clips DB)
├── Downloads (Number)
├── Engagement (Number)
├── Revenue (Number)
└── Tags (Multi-select)
```

---

## Database 2: Guests Pipeline

```
Database Name: 🤝 FirasAi Guests
Properties:
├── Name (Title)
├── Status (Select)
│   ├── 🎯 Prospect
│   ├── 📧 Outreach Sent
│   ├── 💬 In Conversation
│   ├── 📅 Scheduled
│   ├── 🎤 Recorded
│   ├── ⭐ Repeat Guest
│   └── ❌ Passed
├── Title (Rich Text)
├── Company (Rich Text)
├── Email (Email)
├── Twitter/X (URL)
├── LinkedIn (URL)
├── Website (URL)
├── Niche/Expertise (Multi-select)
│   ├── AI Founder
│   ├── Crypto Builder
│   ├── VC/Investor
│   ├── Sports Tech
│   ├── Fintech
│   └── Macro Economist
├── Audience Size (Number)
├── Pitch (Rich Text)
├── Bio (Rich Text)
├── Photo (Files & Media)
├── Episodes (Relation → Episodes DB)
├── Last Contact (Date)
├── Follow-up Date (Date)
├── Rating (Select: ⭐1-5)
└── Notes (Rich Text)
```

---

## Database 3: Content Calendar

```
Database Name: 📅 FirasAi Content Calendar
Properties:
├── Date (Date)
├── Type (Select)
│   ├── Main Episode
│   ├── Short Clip
│   ├── Newsletter
│   ├── Community Post
│   └── Behind Scenes
├── Topic (Title)
├── Platform (Multi-select)
│   ├── Spotify
│   ├── Apple Podcasts
│   ├── YouTube
│   ├── TikTok
│   ├── Instagram
│   ├── LinkedIn
│   ├── Twitter/X
│   └── Newsletter
├── Status (Select)
│   ├── 📝 Planned
│   ├── 🎨 In Creation
│   ├── 👀 In Review
│   ├── ✅ Ready
│   └── 🚀 Published
├── Link (URL)
└── Performance (Rich Text)
```

---

## Database 4: Clips Library

```
Database Name: 🎬 FirasAi Clips
Properties:
├── Title (Title)
├── Source Episode (Relation → Episodes DB)
├── Timestamp (Rich Text)
├── Duration (Number)
├── Type (Select)
│   ├── Viral Moment
│   ├── Quote
│   ├── Tutorial
│   ├── Funny Moment
│   └── Hot Take
├── Caption (Rich Text)
├── Platforms Posted (Multi-select)
├── Views (Number)
├── Engagement Rate (Formula)
├── Hook (Rich Text)
└── Status (Select)
```

---

## Database 5: Sponsors & Revenue

```
Database Name: 💰 FirasAi Sponsors
Properties:
├── Brand (Title)
├── Status (Select)
│   ├── 🎯 Lead
│   ├── 📧 Pitched
│   ├── 💬 Negotiating
│   ├── ✅ Active
│   └── 🔄 Renewed
├── Contact Name (Rich Text)
├── Email (Email)
├── Deal Value (Number)
├── Episodes (Relation → Episodes DB)
├── Deliverables (Multi-select)
│   ├── Pre-roll
│   ├── Mid-roll
│   ├── Post-roll
│   ├── Newsletter
│   └── Social
├── Contract (Files & Media)
├── Payment Status (Select)
└── Notes (Rich Text)
```

---

## Database 6: Research & Sources

```
Database Name: 🔍 FirasAi Research
Properties:
├── Topic (Title)
├── Source (Select)
│   ├── Perplexity
│   ├── Book
│   ├── Article
│   ├── Expert
│   ├── Study
│   └── Podcast
├── Key Findings (Rich Text)
├── Stats (Rich Text)
├── Quotes (Rich Text)
├── Links (URL)
├── Related Episode (Relation)
└── Date Added (Date)
```

---

## Notion Page Layouts

### Page 1: 🎙 ️ Command Center (Main Dashboard)

```
┌─────────────────────────────────────────────┐
│         FirasAi COMMAND CENTER              │
├─────────────────────────────────────────────┤
│                                             │
│  📊 STATS                                   │
│  [Total Episodes] [Total Downloads]         │
│  [Active Sponsors] [Newsletter Subs]        │
│                                             │
│  📅 THIS WEEK                              │
│  [Calendar view of upcoming episodes]       │
│                                             │
│  🔥 HOT TASKS                              │
│  • Guest confirmation: [Name] - Today       │
│  • Episode #47 due: Tomorrow                │
│  • Newsletter: Friday                       │
│                                             │
│  💡 IDEA BACKLOG                            │
│  [Gallery view of episode ideas]             │
│                                             │
└─────────────────────────────────────────────┘
```

### Page 2: 📚 Show Bible

```
SECTIONS:
1. Mission & Vision
2. Target Audience Persona
3. Host Bio & Voice
4. Episode Format Templates
5. Brand Voice Guide
6. Sponsorship Packages
7. Content Pillars
8. Competitor Analysis
9. Growth Strategy
10. Monetization Plan
```

### Page 3: 🎤 Recording Session Template

```
SESSION CHECKLIST:
□ Mic check (Riverside test call)
□ Internet speed test
□ Lighting for video
□ Water nearby
□ Outline open
□ Questions ready
□ Backup recording (Zencastr)
□ Quiet environment confirmed

PRE-RECORDING:
- Topic: ___
- Guest: ___
- Questions count: ___
- Target length: ___

DURING:
- Start time: ___
- End time: ___
- Tech issues: ___
- Best moments timestamps:
  - [00:00] ___
  - [00:00] ___

POST-RECORDING:
- Files backed up
- Episode # assigned
- Next steps documented
```

### Page 4: 📋 Episode Show Notes Template

```
EPISODE #[#]: [TITLE]

[GUEST NAME] is a [TITLE] who [CREDENTIAL HOOK]. In this episode, we dive into [TOPIC].

📌 KEY TAKEAWAYS:
• [Takeaway 1]
• [Takeaway 2]
• [Takeaway 3]

⏱️ TIMESTAMPS:
[00:00] Cold open
[02:30] Introduction
[05:00] Main segment 1
[15:00] Main segment 2
[25:00] Actionable advice
[35:00] Rapid fire
[42:00] Where to find guest

🔗 RESOURCES:
• [Resource 1]
• [Resource 2]

📱 CONNECT:
• Guest: [links]
• Show: [links]
• Newsletter: [link]
```

---

## Database Relations Map

```
Episodes ←→ Guests (Many to Many)
Episodes ←→ Clips (One to Many)
Episodes ←→ Research (Many to Many)
Episodes ←→ Sponsors (Many to Many)
Content Calendar → Episodes (Reference)
Workflows → All Databases (Documentation)
```

---

## Setup Instructions for Notion

### Step-by-Step Setup

#### Step 1: Create Main Workspace
1. Open Notion (notion.so)
2. Create a new page called "🎙 ️ FirasAi Command Center"
3. Add a cover image (use a dark gradient or AI-themed image)
4. Add an icon (microphone or brain emoji)

#### Step 2: Create Episode Database
1. In your Command Center page, create a new database
2. Name it "🎙 ️ FirasAi Episodes"
3. Add the Status property with all status options
4. Add remaining properties (Episode #, Publish Date, Topic, etc.)
5. Add your first 5 episode ideas from Section 9

#### Step 3: Create Guest Database
1. Create another database called "🤝 FirasAi Guests"
2. Set up Status property (Prospect, Outreach Sent, etc.)
3. Add contact properties (Email, Twitter, LinkedIn)
4. Link to Episodes database (Relation property)

#### Step 4: Create Content Calendar
1. Create database called "📅 FirasAi Content Calendar"
2. Add Date, Type, Platform, Status properties
3. Add your publishing schedule

#### Step 4: Create Clips Database
1. Create database called "🎬 FirasAi Clips"
2. Link to Episodes via Relation
3. Add platform tracking properties

#### Step 5: Create Sponsors Database
1. Create database called "💰 FirasAi Sponsors"
2. Add deal tracking properties
3. Link to Episodes

#### Step 6: Create Research Database
1. Create database called "🔍 FirasAi Research"
2. Add source type, findings, stats
3. Link to Episodes

#### Step 7: Build Dashboard
1. On your main Command Center page, add:
   - Stats overview
   - Active episodes view
   - This week calendar
   - Idea backlog gallery

#### Step 8: Add Views
Create multiple views for each database:
- **Episodes**: Table, Calendar, Gallery, Board (by status)
- **Guests**: Table, Board (by status), Gallery
- **Content Calendar**: Calendar, Timeline
- **Clips**: Gallery, Table (by performance)

---

## Pro Tips for Notion Setup

### Tip 1: Use Templates
Create episode templates with pre-filled properties so you don't repeat work.

### Tip 2: Add Formulas
- Engagement Rate = (Likes + Comments + Shares) / Views
- Days to Publish = Publish Date - Created Date
- Revenue per Episode = Total Revenue / Number of Episodes

### Tip 3: Use Filters
- "This Week" = Date is within this week
- "Ready to Publish" = Status = "🚀 Scheduled"
- "Hot Leads" = Guests with Status = "💬 In Conversation"

### Tip 4: Automate with Notion AI
- Auto-generate show notes
- Suggest episode topics
- Summarize research
- Create social posts

---

## Notion Webhook for Make.com

To connect Notion to Make.com, you'll need:

1. Notion API key (from notion.so/my-integrations)
2. Database IDs for each database
3. Webhook URLs configured in Notion

See Section 6 for complete Make.com integration blueprints.
```
