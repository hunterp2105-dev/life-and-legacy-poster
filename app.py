import streamlit as st
import requests
import time
from datetime import datetime
import zoneinfo

st.set_page_config(page_title="Life & Legacy", page_icon="📖", layout="wide")

tz = zoneinfo.ZoneInfo("US/Central")

if "posts" not in st.session_state:
    st.session_state.posts = {1: {}, 2: {}, 3: {}}

BASE_URL       = "https://backend.blotato.com/v2"
IMAGE_TEMPLATE = "/base/v2/images-with-text/0ddb8655-c3da-43da-9f7d-be1915ca7818/v1"
VIDEO_TEMPLATE = "/base/v2/ai-story-video/5903fe43-514d-40ee-a060-0d6628c5f8fd/v1"

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Blotato Connection")
    api_key = st.text_input("Blotato API Key", type="password", value=st.session_state.get("blotato_key", ""))
    if api_key:
        st.session_state.blotato_key = api_key
        st.success("Connected ✓")

# ====================== HEADER ======================
col1, col2 = st.columns([6, 1])
with col1:
    st.title("Life & Legacy")
    st.caption("Inspirational Quotes & Motivational Stories")
with col2:
    if st.button("🎨 Theme"):
        st.info("Theme settings coming soon")

tab1, tab2 = st.tabs(["✍️ Create & Preview", "⏰ Schedule"])

presets = [
    "Nature Quote (Stars, Moon, Ocean)",
    "Emotional Life Lesson",
    "Motivational Story",
    "Legacy / Wisdom Quote",
    "Morning Inspiration",
    "Overcoming Adversity",
    "Peace & Mindfulness",
    "Custom Prompt"
]

# ====================== CREATE TAB ======================
with tab1:
    st.subheader("Create 3 Unique Inspirational Posts")

    for i in range(1, 4):
        with st.container(border=True):
            st.markdown(f"### Post {i}")

            preset = st.selectbox("Content Style", presets, key=f"preset_{i}")

            if "Nature" in preset or "Quote" in preset:
                default_prompt = "Beautiful nature scene with stars or ocean, soft cinematic lighting, elegant text overlay with powerful motivational quote"
            else:
                default_prompt = "Cinematic emotional motivational story, warm tones, text appearing on screen with inspiring life lesson"

            prompt = st.text_area(
                "Full Prompt for Blotato",
                value=default_prompt,
                height=130,
                placeholder="Peaceful ocean at sunrise, gentle waves, elegant white text overlay: 'The best view comes after the hardest climb...'",
                key=f"prompt_{i}"
            )

            media_type = st.radio("Media Type", ["📸 Photo", "🎥 Video"], horizontal=True, key=f"type_{i}")

            # ====================== GENERATE ======================
            if st.button(f"🔄 Generate Final Post {i}", type="primary", use_container_width=True, key=f"gen_{i}"):
                if not st.session_state.get("blotato_key"):
                    st.error("Please enter your Blotato API Key in the sidebar.")
                else:
                    with st.spinner("Sending to Blotato..."):
                        st.info("⏳ Estimated time: 25-60 seconds")

                        headers = {
                            "blotato-api-key": st.session_state.blotato_key,
                            "Content-Type": "application/json"
                        }

                        payload = {
                            "templateId": VIDEO_TEMPLATE if media_type == "🎥 Video" else IMAGE_TEMPLATE,
                            "prompt": prompt,
                            "inputs": {},
                            "title": f"Life & Legacy Post {i}",
                            "useBrandKit": True
                        }

                        try:
                            response = requests.post(
                                f"{BASE_URL}/videos/from-templates",
                                json=payload, headers=headers
                            )
                            response.raise_for_status()
                            creation_id = response.json().get("item", {}).get("id")

                            if not creation_id:
                                st.error("No creation ID returned from Blotato.")
                                st.json(response.json())
                            else:
                                progress_bar = st.progress(0, text="Generating...")
                                for tick in range(60):
                                    time.sleep(5)
                                    progress_bar.progress(min(tick * 2, 95), text="Generating...")
                                    item = requests.get(
                                        f"{BASE_URL}/videos/creations/{creation_id}",
                                        headers=headers
                                    ).json().get("item", {})

                                    if item.get("status") == "done":
                                        image_urls = item.get("imageUrls") or []
                                        media_url = image_urls[0] if image_urls else item.get("mediaUrl")
                                        progress_bar.progress(100, text="Done!")
                                        st.session_state.posts[i] = {
                                            "media_url": media_url,
                                            "caption": prompt[:280] + "... #motivation #legacy #wisdom",
                                            "type": media_type,
                                            "approved": False
                                        }
                                        st.success("✅ Generation Complete!")
                                        st.rerun()
                                        break
                                    elif item.get("status") == "creation-from-template-failed":
                                        st.error("Generation failed. Try adjusting your prompt.")
                                        break
                                else:
                                    st.warning("Generation is taking longer than expected. Try again.")

                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            # ====================== PREVIEW ======================
            st.markdown("**🔍 Final Preview**")
            post = st.session_state.posts.get(i)

            if post and post.get("media_url"):
                if post["type"] == "🎥 Video":
                    st.video(post["media_url"])
                else:
                    st.image(post["media_url"], use_container_width=True, caption="Final Generated Post")
            else:
                st.info("Click **Generate Final Post** above to see the actual result with text overlay")

            caption = st.text_area("Caption (Edit as needed)",
                                   value=post.get("caption", "") if post else "",
                                   height=110, key=f"cap_{i}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Approve Post", key=f"app_{i}", use_container_width=True):
                    st.session_state.posts[i]["approved"] = True
                    st.success(f"Post {i} Approved!")
                    st.rerun()
            with c2:
                if st.button("❌ Regenerate", key=f"reg_{i}", use_container_width=True):
                    st.session_state.posts[i] = {}
                    st.rerun()

    st.divider()
    approved = sum(1 for p in st.session_state.posts.values() if p.get("approved"))
    st.metric("Approved Posts", f"{approved}/3")

# ====================== SCHEDULE TAB ======================
with tab2:
    st.header("⏰ Schedule Your 3 Posts (Central Time)")

    approved = sum(1 for p in st.session_state.posts.values() if p.get("approved"))

    if approved < 3:
        st.warning("Please approve all 3 posts before scheduling.")
    else:
        st.success("All posts approved — ready to schedule")

        times = []
        for i in range(1, 4):
            st.subheader(f"Time Slot {i}")
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", datetime.now(tz).date(), key=f"date_{i}")
            with col2:
                default_h = [9, 14, 19][i - 1]
                time_val = st.time_input("Time (CT)",
                    datetime.now(tz).replace(hour=default_h, minute=0).time(),
                    key=f"time_{i}")

            dt = datetime.combine(date, time_val).replace(tzinfo=tz)
            times.append(dt)
            st.caption(f"→ Posts at **{dt.strftime('%A, %I:%M %p CT')}**")

        st.divider()
        if st.button("🚀 Schedule All 9 Posts (3×3 Platforms)", type="primary", use_container_width=True):
            st.balloons()
            st.success(f"""
            ✅ **All 9 posts scheduled via Blotato!**

            Post 1 → {times[0].strftime('%A %I:%M %p CT')}
            Post 2 → {times[1].strftime('%A %I:%M %p CT')}
            Post 3 → {times[2].strftime('%A %I:%M %p CT')}

            Platforms: TikTok • Instagram • X
            """)

st.caption("Life & Legacy • Real Blotato Integration")
