import gradio as gr
import os
import tempfile
from PIL import Image
import subprocess
import logging
import base64
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from iconsheet import icon_sheet_interface
import mimetypes

# Set up logging
logging.basicConfig(filename='svgmaker.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def process_single_image(image_file, stroke_width, fill, stroke, opacity, output_size, output_dir):
    try:
        logging.info(f"Processing image: {image_file.name}")
        with Image.open(image_file.name) as image:
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = image.width / image.height
            if aspect_ratio > 1:
                new_width = output_size
                new_height = int(output_size / aspect_ratio)
            else:
                new_height = output_size
                new_width = int(output_size * aspect_ratio)
            
            logging.info(f"Resizing image to {new_width}x{new_height}")
            # Resize image
            image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Save as temporary PGM file
            with tempfile.NamedTemporaryFile(suffix='.pgm', delete=False) as temp_pgm:
                image.save(temp_pgm.name)
                temp_pgm_path = temp_pgm.name

        # Run potrace with improved settings
        output_svg = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_file.name))[0]}.svg")
        subprocess.run([
            "potrace",
            "--svg",
            "--output", output_svg,
            "--turdsize", "2",
            "--alphamax", "1",
            "--opttolerance", "0.2",
            "--unit", "10",
            temp_pgm_path
        ], check=True)

        # Clean up temporary PGM
        os.unlink(temp_pgm_path)

        # Modify SVG with user-specified styles and remove unnecessary elements
        with open(output_svg, 'r') as f:
            svg_content = f.read()

        # Remove namespace prefixes and metadata
        svg_content = re.sub(r'<ns0:', '<', svg_content)
        svg_content = re.sub(r'</ns0:', '</', svg_content)
        svg_content = re.sub(r'xmlns:ns0="[^"]+"', '', svg_content)
        svg_content = re.sub(r'<metadata>.*?</metadata>', '', svg_content, flags=re.DOTALL)
        
        # Remove unnecessary group transformation
        svg_content = re.sub(r'<g transform="[^"]+">', '<g>', svg_content)

        # Update SVG attributes
        svg_tree = ET.fromstring(svg_content)
        svg_tree.set('width', str(new_width))
        svg_tree.set('height', str(new_height))
        svg_tree.set('viewBox', f"0 0 {new_width} {new_height}")
        for path in svg_tree.findall('.//{http://www.w3.org/2000/svg}path'):
            path.set('fill', fill)
            path.set('fill-opacity', str(opacity))
            path.set('stroke', stroke)
            path.set('stroke-width', str(stroke_width))
            path.set('stroke-opacity', str(opacity))
        
        svg_content = ET.tostring(svg_tree, encoding='unicode')

        # Final cleanup
        svg_content = re.sub(r'\s+', ' ', svg_content)  # Remove excess whitespace
        svg_content = re.sub(r'> <', '><', svg_content)  # Remove space between tags

        with open(output_svg, 'w') as f:
            f.write(svg_content)

        # Create a base64 encoded version of the SVG for preview
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        preview = f"data:image/svg+xml;base64,{svg_base64}"

        return output_svg, preview
    except Exception as e:
        logging.error(f"Error processing image {image_file.name}: {str(e)}")
        return None, None

def vectorize_icons(images, stroke_width, fill, stroke, opacity, output_size, output_dir, progress=gr.Progress()):
    vectorized_icons = []
    svg_previews = []
    total_images = len(images)
    logging.info(f"Vectorizing {total_images} images")

    os.makedirs(output_dir, exist_ok=True)

    with ThreadPoolExecutor() as executor:
        future_to_image = {executor.submit(process_single_image, image, stroke_width, fill, stroke, opacity, output_size, output_dir): image for image in images}
        for i, future in enumerate(as_completed(future_to_image)):
            image = future_to_image[future]
            progress((i + 1) / total_images, f"Vectorizing image {i+1}/{total_images}")
            try:
                result, preview = future.result()
                vectorized_icons.append(result)
                svg_previews.append(preview)
                logging.info(f"Successfully vectorized image {i+1}")
                progress((i + 1) / total_images, f"Vectorized image {i+1}/{total_images}")
            except Exception as e:
                logging.error(f"Error vectorizing icon {image.name}: {str(e)}")
                vectorized_icons.append(None)
                svg_previews.append(None)
                progress((i + 1) / total_images, f"Failed to vectorize image {i+1}/{total_images}: {str(e)}")

    progress(1.0, "Vectorization complete")
    logging.info(f"Vectorization complete. Successful: {len([i for i in vectorized_icons if i is not None])}, Failed: {len([i for i in vectorized_icons if i is None])}")
    return vectorized_icons, svg_previews

def create_preview_grid(svg_previews):
    # Dynamically create grid based on number of SVG previews
    num_images = len([preview for preview in svg_previews if preview is not None])
    
    # Define the number of columns for the grid
    columns = 4
    grid_html = f'<div style="display: grid; grid-template-columns: repeat({columns}, 1fr); gap: 10px; background-color: #f0f0f0; padding: 20px; border-radius: 10px;">'
    
    for preview in svg_previews:
        if preview:
            grid_html += f'''
                <div style="background-color: white; padding: 10px; border-radius: 5px;">
                    <img src="{preview}" style="width: 100%; height: auto;" onclick="this.classList.toggle('zoomed')" class="zoomable">
                </div>
            '''
        else:
            grid_html += '<div style="background-color: white; padding: 10px; border-radius: 5px;"><p>Error</p></div>'
    
    grid_html += '</div>'
    
    # Add CSS for zoom functionality
    grid_html += '''
    <style>
        .zoomable { transition: transform 0.3s ease; }
        .zoomable.zoomed { transform: scale(2.5); z-index: 1000; position: relative; }
    </style>
    '''
    
    return grid_html


with gr.Blocks() as app:
    gr.Markdown("# SVG Maker and Icon Sheet Generator")
    
    with gr.Tabs():
        with gr.TabItem("SVG Maker"):
            gr.Markdown("# SVG Maker")
    
            with gr.Row():
                image_input = gr.File(label="Upload Images", file_count="multiple")
            
            with gr.Row():
                stroke_width = gr.Slider(0, 10, label="Stroke Width", value=1)
                fill = gr.ColorPicker(label="Fill Color", value="#000000")
                stroke = gr.ColorPicker(label="Stroke Color", value="#000000")
                opacity = gr.Slider(0, 1, label="Opacity", value=1, step=0.1)
            
            with gr.Row():
                output_size = gr.Slider(32, 1024, label="Output Size (px)", value=512, step=32)
                output_dir = gr.Textbox(label="Output Directory", value="output", placeholder="Enter output directory path")
            
            vectorize_btn = gr.Button("Vectorize")
            svg_output = gr.File(label="Vectorized Icons", file_count="multiple")
            svg_preview = gr.HTML(label="SVG Previews")
            
            def process_and_display(images, stroke_width, fill, stroke, opacity, output_size, output_dir):
                vectorized_icons, svg_previews = vectorize_icons(images, stroke_width, fill, stroke, opacity, output_size, output_dir)
                preview_html = create_preview_grid(svg_previews)
                # Filter out None values from vectorized_icons
                valid_icons = [icon for icon in vectorized_icons if icon is not None]
                return valid_icons, preview_html

            vectorize_btn.click(process_and_display, 
                        inputs=[image_input, stroke_width, fill, stroke, opacity, output_size, output_dir], 
                        outputs=[svg_output, svg_preview])
                
        with gr.TabItem("Icon Sheet"):
            mimetypes.add_type('image/svg+xml', '.svg')
            icon_sheet_interface()

if __name__ == "__main__":
    try:
        app.launch()
    except Exception as e:
        logging.error(f"Failed to launch app: {str(e)}")
        raise