import requests
import base64

def send_data_and_save_image():
    url = "http://127.0.0.1:8000/create/"
    
    data = {
        "logo": "https://res.cloudinary.com/dmubfrefi/image/private/s--y0Ax_FO6--/c_crop,h_2813,w_5000,x_0,y_0/c_scale,w_3840/f_auto/q_auto/v1/dee-about-cms-prod-medias/cf68f541-fc92-4373-91cb-086ae0fe2f88/002-nike-logos-swoosh-white.jpg?_a=BAAAV6Bs",
        "template": "https://img.freepik.com/premium-vector/shoes-collection-sale-social-media-promotion-banner-template_122059-604.jpg?w=996",
        "name": "Stride Athletics",
        "colors": {
            "primary": "sky blue",
            "secondary": "white",
            "accent": "rose Gold"
        },
        "title_font": "Roboto",
        "subtitle_font": "Montserrat",
        "body_font": "Open Sans",
        "tagline": "Run Your World",
        "industry": "Footwear",
        "demographic": "Active individuals aged 18-35",
        "psychographic": "Fitness enthusiasts and athletes",
        "audience_interest": "Running, fitness, outdoor activities",
        "tone_of_voice": "playful",
        "message_style": "promote",
        "visual_style": "vibrant",
        "keywords": {
            "primary": ["athletic", "running", "comfort"],
            "secondary": ["style", "performance"]
        },
        "cta_required": True,
        "cta_text": "shop now!",
        "current_campaign": "Spring/Summer Collection 2024",
        "season": "Spring",
        "mood": "Energetic",
        "content_type": "Email Campaign"
    }

    try:
        # Send the POST request
        response = requests.post(url, json=data)

        # Check for successful response
        response.raise_for_status()

        # Assuming the response contains a base64 encoded image
        result = response.json()
        base64_image = result.get("generated_image")  # Change based on actual response structure

        if base64_image:
            # Decode the base64 string
            image_data = base64.b64decode(base64_image)

            # Save the image
            with open("generated_image.png", "wb") as image_file:
                image_file.write(image_data)
            print("Image saved as generated_image.png")
        else:
            print("No image found in the response.")

    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")

# Call the function
send_data_and_save_image()
