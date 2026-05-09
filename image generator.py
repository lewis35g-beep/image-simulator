import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="YouTube Script Image Generator", layout="wide")

st.title("YouTube Script Image Generator")
st.write("Paste a YouTube script and generate cinematic scene images.")

script = st.text_area("Paste your YouTube script here:", height=300)

style = st.selectbox(
    "Image Style",
    [
        "cinematic ultra realistic",
        "dark documentary realism",
        "first-person POV cinematic",
        "YouTube thumbnail style",
        "historical realistic",
        "horror cinematic",
        "luxury finance cinematic",
    ]
)

num_scenes = st.slider("How many images/scenes?", 3, 20, 8)

def create_scene_prompts(script_text, scene_count, visual_style):
    prompt = f"""
You are a cinematic YouTube visual director.

Break this YouTube script into {scene_count} image scenes.

For each scene, return:
- scene_number
- scene_summary
- image_prompt

The image prompts should be highly visual, cinematic, detailed, and ready for AI image generation.

Style: {visual_style}

Script:
{script_text}

Return only valid JSON in this format:
[
  {{
    "scene_number": 1,
    "scene_summary": "...",
    "image_prompt": "..."
  }}
]
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt
    )

    text = response.output_text
    return json.loads(text)

def generate_image(prompt, filename):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    file_path = OUTPUT_DIR / filename
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return file_path

if "scenes" not in st.session_state:
    st.session_state.scenes = []

if st.button("Create Scene Prompts"):
    if not script.strip():
        st.warning("Paste a script first.")
    else:
        with st.spinner("Breaking script into cinematic image scenes..."):
            st.session_state.scenes = create_scene_prompts(script, num_scenes, style)
        st.success("Scene prompts created.")

if st.session_state.scenes:
    st.subheader("Generated Scene Prompts")

    for scene in st.session_state.scenes:
        scene_num = scene["scene_number"]
        scene_summary = scene["scene_summary"]
        image_prompt = scene["image_prompt"]

        with st.expander(f"Scene {scene_num}: {scene_summary}", expanded=True):
            edited_prompt = st.text_area(
                f"Prompt for Scene {scene_num}",
                value=image_prompt,
                height=160,
                key=f"prompt_{scene_num}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Generate Image {scene_num}", key=f"generate_{scene_num}"):
                    with st.spinner(f"Generating image for Scene {scene_num}..."):
                        filename = f"scene_{scene_num}.png"
                        image_path = generate_image(edited_prompt, filename)
                        st.image(str(image_path), caption=f"Scene {scene_num}", use_container_width=True)
                        st.success(f"Saved: {image_path}")

            with col2:
                if st.button(f"Generate More Like Scene {scene_num}", key=f"more_{scene_num}"):
                    variation_prompt = edited_prompt + """
Create a new version of this same scene with different camera angle, lighting, composition, and emotional intensity.
Keep the same story moment, but make it visually fresh.
"""
                    with st.spinner(f"Generating another version of Scene {scene_num}..."):
                        filename = f"scene_{scene_num}_more.png"
                        image_path = generate_image(variation_prompt, filename)
                        st.image(str(image_path), caption=f"More Like Scene {scene_num}", use_container_width=True)
                        st.success(f"Saved: {image_path}")