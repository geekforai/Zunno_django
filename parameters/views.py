from colors import get_color_rgb
import os
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from yolo_prediction import getBoxes
import cv2
from rest_framework import status
import base64
from .models import BrandCreation
from parameters.serializers import BrandCreationSerializer
import matplotlib.pyplot as plt
from PIL import Image
import requests
from io import BytesIO
from model import Model
import numpy as np
import random
from image_utils import draw_multiline_text_in_bbox,draw_multiline_text_in_bbox_center,remove_text_with_easyocr,create_button
import io
from ollamma import ollama_generate
import gc
import torch
#from finegrane.src.app import inhance
from enhancer.services import enhance
import subprocess
from parameters.models import get_string

from clip import ImageTextMatcher
template_matcher=ImageTextMatcher()
template_matcher.load_images_and_create_embeddings()
def clear_cuda_cache():
    """Clear CUDA cache to free up memory."""
    gc.collect()
    torch.cuda.empty_cache()
def find_and_kill_process_by_name(process_name):
    try:
        # Get the list of all process IDs matching the process name
        result = subprocess.run(['pgrep', process_name], stdout=subprocess.PIPE, text=True)
        
        # Split the output into a list of process IDs
        process_ids = result.stdout.strip().splitlines()

        if not process_ids:
            print(f"No processes found with the name: {process_name}")
            return

        # Kill each process ID
        for pid in process_ids:
            subprocess.run(['sudo','kill','-9' ,pid])
            print(f"Killed process {pid} ({process_name})")

    except Exception as e:
        print(f"An error occurred: {e}")
def draw_all_text(instance, ollama_data, boxes, image):
    predicted_class = boxes.keys()
    primary_color=instance.colors['primary']
    secondary_color=instance.colors['secondary']
    print(predicted_class)
    if 'title' in predicted_class:
        print("Drawing title...")
        image = draw_multiline_text_in_bbox(image=image, text=ollama_data['title'], bbox=boxes['title'][0]
                                            ,gradient_start=get_color_rgb(primary_color),gradient_end=get_color_rgb(secondary_color))
        
    if 'action button' in predicted_class:
        print("Drawing action button...")
        image = create_button(image=image, text=instance.cta_text, bbox=boxes['action button'][0]
                                      ,font_color=get_color_rgb(primary_color),fill_color=secondary_color)
        
    if 'Subheading' in predicted_class:
        print("Drawing subheading...")
        image = draw_multiline_text_in_bbox(image=image, text=ollama_data['description'], bbox=boxes['Subheading'][0]
                                       ,gradient_start=get_color_rgb(primary_color),gradient_end=get_color_rgb(secondary_color))
    
    return image

          
     

def resize_image(image, max_size_kb=300):
    
    """Resize image to ensure it is under the specified size."""
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    while img_bytes.tell() / 1024 > max_size_kb:
        new_size = (int(image.width * 0.9), int(image.height * 0.9))
        image = image.resize(new_size, Image.LANCZOS)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')

    return image

def get_boxes(template):
        name='untitled'+str(random.choice(range(0,10000)))
        template.save(name+'.png')
        boxes,empty_template_image=getBoxes(name+'.png')
        return boxes,empty_template_image,name+'.png'

class BrandCreationAPIView(APIView):
    def get(self, request):
        clear_cuda_cache()
        brand_creations = BrandCreation.objects.all()
        serializer = BrandCreationSerializer(brand_creations, many=True)
        return Response(serializer.data)
    def post(self, request):
        clear_cuda_cache()
        serializer = BrandCreationSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            logo_url = instance.logo
            empty_template = Image.open(template_matcher.fetch_images_based_on_text(get_string(instance=instance)))
            boxes, empty_template,image_name = get_boxes(empty_template)
            empty_template=remove_text_with_easyocr(empty_template)
            
            prompt = f"""
                Design a vibrant poster for {instance.name} 
                in the {instance.industry} industry, using 
                {instance.colors}. Capture a {instance.tone_of_voice} 
                tone with {instance.title_font} for the title. Highlight 
                the campaign: '{instance.current_campaign}', include the 
                tagline: '{instance.tagline}', and a call-to-action: 
                '{instance.cta_text}', appealing to {instance.audience_interest}.
            """
            data = ollama_generate(instance=instance)
            find_and_kill_process_by_name('ollama_llama_se')
            clear_cuda_cache()
            #final_template =draw_multiline_text_in_bbox(image=empty_template, text=data['title'], bbox=boxes['title'][0]) 
            final_template=empty_template
            if 'logo' in boxes.keys():
             image = Image.open(BytesIO(requests.get(logo_url).content)).convert("RGB")
             image = resize_image(image, 50)  # Assuming resize_image is defined elsewhere
# Extract bounding box coordinates
             x, y, w, h = boxes['logo'][0]
# Calculate the size to paste (width and height)
             paste_size = (int(w - x), int(h - y))
# Resize the image to fit within the bounding box using BICUBIC filter
             image = image.resize(paste_size, Image.BICUBIC)
# Paste the image onto the final template
             final_template.paste(image, (int(x), int(y)))
            model = Model(base_model_id='ashllay/stable-diffusion-v1-5-archive')
            seed = random.choice(range(0, 2147483647))
            additional_prompt = "best quality, extremely detailed"
            negative_prompt = "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality"
            num_images = 1
            image_resolution = 768
            num_steps = 5
            guidance_scale = 10
            low_threshold = 100
            high_threshold = 200
            generated_image = model.process_canny(
                image=final_template,
                prompt=prompt,
                additional_prompt=additional_prompt,
                negative_prompt=negative_prompt,
                num_images=num_images,
                image_resolution=image_resolution,
                num_steps=num_steps,
                guidance_scale=guidance_scale,
                seed=seed,
                low_threshold=low_threshold,
                high_threshold=high_threshold,
            )[1]
            generated_image=generated_image.resize(final_template.size)
            generated_image=enhance(image=generated_image)
#            generated_image.paste(image, (int(x), int(y)))
            generated_image = draw_all_text(instance=instance, ollama_data=data, boxes=boxes, image=generated_image)
 #           generated_image = inhance(input_image=generated_image)[1]
            # Convert generated image to Base64
            buffered = BytesIO()
            generated_image.save(buffered, format="PNG")
            generated_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            response_data = {
                'brand_creation': serializer.data,
                'generated_image': generated_image_base64,
            }
            os.remove(image_name)
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
