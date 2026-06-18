import json
import re
from anthropic import Anthropic

BRAND_VOICE = """
Brand voice: Warm, uplifting, peaceful, and gently inspiring. Like a quiet moment by a forest stream.
- Never rushed or corporate
- Wisdom over information — distill feelings, not facts
- Nature as healer and teacher
- Warmth without saccharine sweetness
- Short sentences. Let each word breathe.
- No exclamation marks on quotes
"""


def _parse_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {}


def generate_daily_content(niche: str, tone: str, api_key: str) -> dict:
    """Generate morning image quote, midday video content, evening video quote."""
    client = Anthropic(api_key=api_key)

    prompt = f"""You are writing social media content for a {niche} brand.
{BRAND_VOICE}
Tone for today: {tone}

Generate three pieces of content:
1. MORNING_QUOTE: A single poetic 1-2 line nature quote. Short, timeless. The kind someone saves to their phone.
2. MIDDAY_CONTENT: Either a fresh nature quote OR a 2-4 sentence heartwarming micro-story (a bird, a child, an old tree, a quiet human moment in nature). Alternate style from morning.
3. EVENING_QUOTE: A different, more reflective nature quote. Wise, meditative. Different theme from morning.

Output ONLY valid JSON, no other text:
{{"morning": "...", "midday": "...", "evening": "..."}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(response.content[0].text)


def generate_from_youtube(transcript: str, title: str, niche: str, tone: str, api_key: str) -> dict:
    """Repurpose a YouTube transcript into multi-platform social content."""
    client = Anthropic(api_key=api_key)

    prompt = f"""You are repurposing a YouTube video called "{title}" for a {niche} social media brand.
{BRAND_VOICE}
Tone: {tone}

Video transcript (excerpt):
{transcript[:3000]}

Generate platform-optimized content:
1. LINKEDIN_POST: 150-300 words. Thoughtful, professional, nature-wisdom. Hook → 3-4 short paragraphs → closing reflection. End with 5-8 hashtags.
2. INSTAGRAM_CAPTION: 1-3 poetic lines distilling the video's soul. Then 4-6 hashtags.
3. X_POST: Under 220 chars + 2-3 hashtags. Sharp, high-wonder, screenshot-worthy.
4. CAROUSEL_SLIDES: 6 slide texts. Slide 1 = hook, slides 2-5 = insights, slide 6 = CTA. Each slide 1-3 lines max.
5. IMAGE_PROMPT: One detailed visual prompt for generating a nature background image that matches this content.

Output ONLY valid JSON:
{{"linkedin": "...", "instagram": "...", "x_post": "...", "carousel": ["...", "...", "...", "...", "...", "..."], "image_prompt": "..."}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(response.content[0].text)


def build_caption(text: str, niche: str, platform: str) -> str:
    """Add platform-appropriate hashtags to content."""
    hashtag_map = {
        "Nature":         "#nature #naturequotes #peaceful #heartwarming #outdoors #naturalbeauty",
        "Wildlife":       "#wildlife #animals #naturephotography #wildernessheals #wildanimals",
        "Hiking":         "#hiking #traillife #findyourwild #outdoorlife #hikingadventures",
        "Forest Bathing": "#forestbathing #shinrinyoku #naturetherapy #slowliving #forestlife",
        "Eco-Travel":     "#ecotravel #sustainabletravel #naturelover #ecotourism #greentravel",
        "Ocean & Coast":  "#ocean #coastline #seaside #oceanquotes #serenity #beachlife",
        "Mountains":      "#mountains #mountainlife #alpineglow #peakseeker #mountainquotes",
        "Seasons":        "#seasons #naturequotes #slowliving #seasonalbeauty #naturelover",
    }
    tags = hashtag_map.get(niche, "#nature #naturequotes #peaceful #heartwarming")

    if platform == "twitter":
        # X: keep it short — pick first 3 tags
        short_tags = " ".join(tags.split()[:3])
        return f"{text} {short_tags}"
    elif platform == "tiktok":
        short_tags = " ".join(tags.split()[:4])
        return f"{text} {short_tags}"
    else:
        return f"{text}\n\n{tags}"
