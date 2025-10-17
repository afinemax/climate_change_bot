from atproto import Client, models       # Needed for Client and AppBskyEmbedDefs/Facets
from pathlib import Path                  # Needed for output_dir and glob
from dotenv import load_dotenv            # Needed to load credentials
import os                                 # Needed to read env variables
import re                                 # Needed for hashtag regex


def make_hashtag_facets(text: str):
    """Generate facets as dictionaries for all hashtags in the text."""
    facets = []
    # Match hashtags with letters, numbers, underscores, and optional dashes
    for match in re.finditer(r"#([\w-]+)", text):
        start, end = match.span()
        tag = match.group(1)
        facets.append({
            "$type": "app.bsky.richtext.facet",
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": tag}],
        })
    return facets


def main():
    # Load BlueSky credentials
    load_dotenv("env.env")
    handle = os.getenv("BSKY_HANDLE")
    password = os.getenv("BSKY_PASSWORD")

    if not handle or not password:
        raise ValueError("Missing BSKY_HANDLE or BSKY_PASSWORD in env.env")

    # Log in
    client = Client()
    profile = client.login(handle, password)
    print(f"✅ Logged in as {profile.display_name or handle}")

    output_dir = Path("output")

    # Process each caption file
    for md_path in output_dir.glob("*.md"):
        base_name = md_path.stem
        caption = md_path.read_text().strip()

        # Remove line breaks so hashtags stay in same paragraph
        caption = ' '.join(caption.split())

        # Expected image files
        img_main = output_dir / f"{base_name}.png"
        img_anom = output_dir / f"{base_name}_anomaly.png"
        image_paths = [p for p in [img_main, img_anom] if p.exists()]

        if not image_paths:
            print(f"⚠️ No images found for {base_name}, skipping.")
            continue

        # Load image bytes and prepare metadata
        images = []
        image_alts = []
        image_aspect_ratios = []

        for path in image_paths:
            with open(path, "rb") as f:
                images.append(f.read())
            image_alts.append(path.stem.replace('_', ' '))
            # Assuming aspect ratio ~12:6 (2:1)
            image_aspect_ratios.append(
                models.AppBskyEmbedDefs.AspectRatio(height=6, width=12)
            )

        # Generate hashtag facets as dictionaries
        facets = make_hashtag_facets(caption)

        # Send post with images and hashtag facets
        post = client.send_images(
            text=caption,
            images=images,
            image_alts=image_alts,
            image_aspect_ratios=image_aspect_ratios,
            facets=facets
        )

        print(f"✅ Posted {base_name}: {post.uri}")


if __name__ == "__main__":
    main()
