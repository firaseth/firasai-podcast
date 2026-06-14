from pydantic import BaseModel, Field
from typing import List, Dict

class TopicSuggestion(BaseModel):
    title: str = Field(description="The suggested trending title for the episode")
    hook: str = Field(description="An attention-grabbing hook for the cold open")
    angle: str = Field(description="The unique angle or perspective of the episode")
    talking_points: List[str] = Field(description="List of 3-5 main talking points to cover")
    reason: str = Field(description="The rationale behind why this is currently trending or valuable")

class EpisodeIdea(BaseModel):
    title: str = Field(description="The proposed title of the episode")
    hook: str = Field(description="The key hook or angle")
    format: str = Field(description="Format of the episode (e.g. solo, interview, case study, reaction)")
    why_now: str = Field(description="Why this topic is timely or trending right now")

class WeeklyIdeas(BaseModel):
    ideas: List[EpisodeIdea] = Field(description="A list of 5 episode ideas for the week")

class StructuredResearch(BaseModel):
    stats: List[str] = Field(description="List of surprising statistics with sources")
    quotes: List[str] = Field(description="List of expert quotes")
    examples: List[str] = Field(description="List of real-world examples or case studies")
    key_takeaways: List[str] = Field(description="List of main insights or takeaways")

class ShowNotes(BaseModel):
    title: str = Field(description="Episode Title")
    hook: str = Field(description="1-sentence episode hook/summary")
    takeaways: List[str] = Field(description="3-bullet key takeaways")
    timestamps: List[str] = Field(description="Timestamped chapters in format [MM:SS] Title")
    keywords: List[str] = Field(description="5 highly relevant SEO keywords")

class SocialPosts(BaseModel):
    twitter: List[str] = Field(description="3 ready-to-post tweets under 280 characters")
    linkedin: List[str] = Field(description="2 LinkedIn-optimized professional posts")
    instagram: List[str] = Field(description="2 engaging Instagram captions with hashtags")

class NewsletterDraft(BaseModel):
    subject_lines: List[str] = Field(description="3 catchy subject line options")
    opening: str = Field(description="Engaging email newsletter opening hook")
    summary: List[str] = Field(description="3-bullet bulleted summary of the episode")
    cta: str = Field(description="Clear and compelling Call To Action")

class TwitterThread(BaseModel):
    tweets: List[str] = Field(description="Array of exactly 10 tweets forming an insightful thread")

class ClipScriptItem(BaseModel):
    timestamp: str = Field(description="Estimated or exact timestamp in the episode")
    hook: str = Field(description="The hook to start the clip")
    script: str = Field(description="60-second video script")
    caption: str = Field(description="Social media caption for the clip")
    hashtags: List[str] = Field(description="Relevant hashtags")

class ClipScripts(BaseModel):
    clips: List[ClipScriptItem] = Field(description="Array of 5 short-form clip ideas")

class WeeklyReport(BaseModel):
    wins: List[str] = Field(description="3 performance wins or milestones from this week")
    improvements: List[str] = Field(description="3 areas or metrics that need improvement")
    experiments: List[str] = Field(description="3 new experiments to try next week")
    predicted_next_week_performance: str = Field(description="Narrative forecasting of next week's performance")
    action_items: List[str] = Field(description="Prioritized list of actionable next steps")
