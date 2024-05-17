from flask import Flask, request, render_template, send_file
from pptx import Presentation
from pptx.util import Inches
import openai
import os
import io
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_slide(prs, title, content, bullets=None, image_path=None):
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    
    title_placeholder = slide.shapes.title
    title_placeholder.text = title

    content_placeholder = slide.placeholders[1]
    content_placeholder.text = content

    if bullets:
        for bullet in bullets:
            p = content_placeholder.text_frame.add_paragraph()
            p.text = bullet
            p.level = 1
    
    if image_path:
        slide.shapes.add_picture(image_path, Inches(1), Inches(2), width=Inches(5))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_slides', methods=['POST'])
def generate_slides():
    document_text = request.form.get('document_text', '')
    prompt = request.form.get('prompt', '')
    theme = request.form.get('theme', 'default')
    
    # Call GPT-4 to generate slide content
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt + "\n\n" + document_text}
        ],
        max_tokens=1500
    )
    slide_content = response['choices'][0]['message']['content'].strip()
    
    # Log the entire slide content for debugging purposes
    print("Slide content from GPT-4:", flush=True)
    print(slide_content, flush=True)

    prs = Presentation()

    # Create slides based on GPT-4 output
    slides = slide_content.split("\n\n")  # Split content into slides
    for i, slide in enumerate(slides):
        print(f"Processing slide {i + 1}:", flush=True)
        print(slide, flush=True)
        
        if "\n" in slide:
            title, content = slide.split("\n", 1)
        else:
            title = "Untitled"
            content = slide
        
        print(f"Title: {title}", flush=True)
        print(f"Content: {content}", flush=True)
        
        create_slide(prs, title.strip(), content.strip())

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)

    return send_file(output, download_name='presentation.pptx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
