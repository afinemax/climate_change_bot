from atproto import Client, models
from pathlib import Path
from dotenv import load_dotenv
import os


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

        # Expected image files
        img_main = output_dir / f"{base_name}.png"
        img_anom = output_dir / f"{base_name}_anomaly.png"
        image_paths = [p for p in [img_main, img_anom] if p.exists()]

        if not image_paths:
            print(f"⚠️ No images found for {base_name}, skipping.")
            continue

        # Load image bytes
        images = []
        image_alts = []
        image_aspect_ratios = []

        for path in image_paths:
            with open(path, "rb") as f:
                images.append(f.read())
            image_alts.append(f"{path.stem.replace('_', ' ')}")
            # Assuming aspect ratio ~12:6 (2:1)
            image_aspect_ratios.append(models.AppBskyEmbedDefs.AspectRatio(height=6, width=12))

        # Send post
        post = client.send_images(
            text=caption,
            images=images,
            image_alts=image_alts,
            image_aspect_ratios=image_aspect_ratios,
        )

        print(f"✅ Posted {base_name}: {post.uri}")


if __name__ == "__main__":
    main()
