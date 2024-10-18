import gradio as gr
import re
import tempfile
from lxml import etree as ET

def create_icon_sheet(svg_files, columns, padding, background_color, sheet_width, transparent_background):
    # Calculate dimensions
    icons = []
    max_icon_size = 0
    for svg_file in svg_files:
        # Verify the content is an SVG
        try:
            tree = ET.parse(svg_file.name)
            root = tree.getroot()
            if root.tag != '{http://www.w3.org/2000/svg}svg':
                raise ValueError("File is not a valid SVG")
        except ET.ParseError:
            raise ValueError("File is not a valid SVG")

        width = float(root.get('width', '0').replace('px', ''))
        height = float(root.get('height', '0').replace('px', ''))
        max_icon_size = max(max_icon_size, width, height)
        icons.append(svg_file.name)
    
    icon_size = max_icon_size + padding * 2
    rows = (len(icons) + columns - 1) // columns
    
    # Calculate scaling factor
    scale_factor = sheet_width / (columns * icon_size)
    
    # Adjust icon size and sheet height based on the scaling factor
    scaled_icon_size = icon_size * scale_factor
    sheet_height = rows * scaled_icon_size
    
    # Create SVG root element
    svg_ns = "http://www.w3.org/2000/svg"
    # No need to register the namespace manually with lxml
    svg = ET.Element("{%s}svg" % svg_ns, nsmap={None: svg_ns})
    svg.set("width", str(sheet_width))
    svg.set("height", str(sheet_height))
    
    # Add background if not transparent
    if not transparent_background:
        rect = ET.SubElement(svg, "{%s}rect" % svg_ns)
        rect.set("x", "0")
        rect.set("y", "0")
        rect.set("width", str(sheet_width))
        rect.set("height", str(sheet_height))
        rect.set("fill", background_color)
    
    # Place icons
    for i, svg_file in enumerate(icons):
        row = i // columns
        col = i % columns
        x = col * scaled_icon_size
        y = row * scaled_icon_size
        
        # Read SVG content
        with open(svg_file, 'r') as f:
            svg_content = f.read()
        
        # Remove XML declaration and DOCTYPE
        svg_content = re.sub(r'<\?xml[^>]+\?>', '', svg_content)
        svg_content = re.sub(r'<!DOCTYPE[^>]+>', '', svg_content)
        
        # Parse the SVG content
        icon_svg = ET.fromstring(svg_content)
        
        # Create a group with the appropriate transform
        icon_group = ET.SubElement(svg, "{%s}g" % svg_ns)
        
        # Adjust viewBox if necessary
        viewBox = icon_svg.get('viewBox')
        if viewBox:
            x_offset, y_offset, svg_width, svg_height = map(float, viewBox.split())
            icon_scale_x = (scaled_icon_size - padding * 2 * scale_factor) / svg_width
            icon_scale_y = (scaled_icon_size - padding * 2 * scale_factor) / svg_height
            icon_scale = min(icon_scale_x, icon_scale_y)
            translate_x = x + padding * scale_factor - x_offset * icon_scale
            translate_y = y + padding * scale_factor - y_offset * icon_scale
            transform = f"translate({translate_x},{translate_y}) scale({icon_scale})"
        else:
            width = float(icon_svg.get('width', '0').replace('px', ''))
            height = float(icon_svg.get('height', '0').replace('px', ''))
            icon_scale = min((scaled_icon_size - padding * 2 * scale_factor) / width, (scaled_icon_size - padding * 2 * scale_factor) / height)
            transform = f"translate({x + padding * scale_factor},{y + padding * scale_factor}) scale({icon_scale})"
        
        icon_group.set("transform", transform)
        
        # Move the children of icon_svg into icon_group
        for element in icon_svg.iterchildren():
            icon_group.append(element)
    
    # Write the SVG to a file
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.svg', mode='wb')
    tree = ET.ElementTree(svg)
    tree.write(output_file, xml_declaration=True, encoding='utf-8')
    output_file.close()
    
    return output_file.name


def icon_sheet_interface():
    with gr.Blocks() as icon_sheet_app:
        gr.Markdown("# Icon Sheet Generator")
        
        with gr.Row():
            svg_files = gr.File(label="Upload SVG Icons", file_count="multiple")
        
        with gr.Row():
            columns = gr.Slider(1, 10, value=4, step=1, label="Number of Columns")
            padding = gr.Slider(0, 50, value=10, step=1, label="Padding (px)")
            background_color = gr.ColorPicker(label="Background Color", value="#ffffff")
            sheet_width = gr.Slider(100, 2000, value=1000, step=10, label="Sheet Width (px)")
            transparent_background = gr.Checkbox(label="Transparent Background", value=False)
        
        generate_btn = gr.Button("Generate Icon Sheet")
        output = gr.File(label="Generated Icon Sheet")
        
        def process_and_return(svg_files, columns, padding, background_color, sheet_width, transparent_background):
            # Validate that all uploaded files are SVGs
            for svg_file in svg_files:
                if not svg_file.name.endswith('.svg'):
                    raise ValueError(f"Invalid file type: {svg_file.name}. Please upload only SVG files.")
            temp_file = create_icon_sheet(svg_files, columns, padding, background_color, sheet_width, transparent_background)
            return temp_file
    
        generate_btn.click(process_and_return, 
                           inputs=[svg_files, columns, padding, background_color, sheet_width, transparent_background],
                           outputs=output)
    
    return icon_sheet_app

if __name__ == "__main__":
    icon_sheet_app = icon_sheet_interface()
    icon_sheet_app.launch()
