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

def generate_image_with_person(
    prompt,
    person_image_path,
    filename,
    gender="person"
):
    """
    Generate a cinematic image using an uploaded reference photo and ensure
    the same person appears consistently in every generated scene.

    Parameters
    ----------
    prompt : str
        The scene description or image prompt.
    person_image_path : str or Path
        Path to the uploaded reference image.
    filename : str
        Output filename for the generated image.
    gender : str
        "man", "woman", "him", "her", or "person".
        This is used to make the prompt read naturally.
    """

    # Normalize gender text
    gender = gender.lower().strip()

    if gender in ["man", "male", "him"]:
        subject = "the same man"
        pronoun = "him"
        possessive = "his"
    elif gender in ["woman", "female", "her"]:
        subject = "the same woman"
        pronoun = "her"
        possessive = "her"
    else:
        subject = "the same person"
        pronoun = "them"
        possessive = "their"

    final_prompt = f"""
Use the uploaded reference photo as the main character.

Create a cinematic, ultra-realistic image based on this scene:
{prompt}

IMPORTANT CHARACTER CONSISTENCY RULES:
- Include {subject} from the uploaded photo in this scene.
- Preserve {possessive} face, hairstyle, age, body type, and overall appearance.
- Do not replace {pronoun} with a different person.
- Keep the same identity across all generated images.
- Place {pronoun} naturally into the environment described in the scene.
- Maintain photorealistic quality, cinematic lighting, and highly detailed textures.
- The uploaded person must be the central character of the image.
"""

    result = client.images.edit(
        model="gpt-image-1",
        image=open(person_image_path, "rb"),
        prompt=final_prompt,
        size="1024x1024",
        input_fidelity="high"
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    file_path = OUTPUT_DIR / filename
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return file_path