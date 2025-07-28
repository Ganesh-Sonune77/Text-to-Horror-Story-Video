import requests
import os
import uuid
import time

def generate_images_from_deepai(prompt, save_dir="static/images/", num_images=5, delay=2):
    print(f"🔄 Generating images from DeepAI for: {prompt}")
    os.makedirs(save_dir, exist_ok=True)
    image_paths = []

    for i in range(num_images):
        try:
            response = requests.post(
                "https://api.deepai.org/api/text2img",
                data={'text': prompt},
                headers={'api-key': 'Replace here your deepai key'}  # 👈 Replace with your current key
            )

            print(f"🧾 Response {i+1}:", response.text)  # Log entire response

            data = response.json()
            output_url = data.get('output_url')

            if not output_url:
                raise Exception(f"🚫 No output_url. DeepAI says: {data.get('status', 'Unknown error')}")

            img_data = requests.get(output_url).content
            img_path = os.path.join(save_dir, f"{uuid.uuid4()}.jpg")

            with open(img_path, 'wb') as f:
                f.write(img_data)

            image_paths.append(img_path)

            time.sleep(delay)  # ⏱ Avoid hitting rate limit

        except Exception as e:
            print(f"❌ Error in image {i+1}: {e}")
            continue  # Skip to next image

    print(f"✅ Total images saved: {len(image_paths)}")
    return image_paths
