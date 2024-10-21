import re
import ollama
def get_title_prompt(instance):
  
    # Create the structured output format prompt
    prompt = f"""
You are tasked with creating a poster for a brand. Please provide the output in the following format:

Title: 
[Your title here]

Description: 
[Your description here]

Call to Action: 
[Your CTA here]

Hashtags: 
[Your hashtags here]

---

Using the following details:
- Brand Name: {instance.name}
- Tagline: {instance.tagline}
- Target Audience: {instance.audience_interest}
- Industry: {instance.industry}
- Demographic: {instance.demographic}
- Psychographic: {instance.psychographic}
- Audience Interest: {instance.audience_interest}
- Keywords: {', '.join(instance.keywords['primary'])}, {', '.join(instance.keywords['secondary'])}
- Visual Style: {instance.visual_style}
- Tone of Voice: {instance.tone_of_voice}
- Current Campaign: {instance.current_campaign}
- Season: {instance.season}
- Mood: {instance.mood}

Please generate an eye-catching title for a poster promoting {instance.name}. The title (maximum only 4 words) should convey energy and enthusiasm, aligning with the brand’s identity.

Write a brief description (maximum only 8 words) that highlights the essence of {instance.name}, emphasizing its tagline, "{instance.tagline}". Mention how the brand enhances the lifestyle of {instance.audience_interest} through innovative footwear designed for running and outdoor activities.

Include a strong call to action that encourages engagement, such as "{instance.cta_text}."

Generate relevant hashtags that resonate with fitness enthusiasts and outdoor adventurers, including keywords from the brand's identity, such as #AthleticStyle, #Fitness, and #{instance.name.replace(" ", "")}.
"""

    return prompt


def extract_poster_details(llm_response):
    # Define regex patterns to extract each section
    llm_response=llm_response.replace("**","")
    title_pattern = r"^Title:\s*(.*?)(?=\n\n|$)"
    description_pattern = r"^Description:\s*(.*?)(?=\n\n|$)"
    hashtags_pattern = r"^Hashtags:\s*(.*?)(?=\n\n|$)"
    # Use regex to search for the patterns
    title_match = re.search(title_pattern, llm_response, re.MULTILINE | re.DOTALL)
    description_match = re.search(description_pattern, llm_response, re.MULTILINE | re.DOTALL)
    hashtags_match = re.search(hashtags_pattern, llm_response, re.MULTILINE | re.DOTALL)
    # Extract and clean the results
    title = title_match.group(1).strip() if title_match else None
    description = description_match.group(1).strip() if description_match else None
    hashtags = hashtags_match.group(1).strip() if hashtags_match else None
    return {
        "title": title,
        "description": description,
        "hashtags": hashtags.split() if hashtags else []
    }

def ollama_generate(instance,type='prompt'):
    prompt=get_title_prompt(instance=instance)
    res=ollama.generate(model='llama3.1',prompt=prompt)
    return extract_poster_details(llm_response=res['response'])
    

