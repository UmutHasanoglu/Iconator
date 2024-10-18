# SVG Maker

This application converts raster images to SVG format and allows for basic styling of the resulting SVGs.

## Installation and Setup

1. Navigate to the SVGmaker directory:
   ```bash
   cd flux_icon_generator/SVGmaker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Node.js if not already installed (https://nodejs.org/)

5. Install potrace globally using npm:
   ```bash
   npm install -g potrace
   ```

6. Install SVGO for SVG optimization:
   ```bash
   npm install svgo
   ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Upload one or more image files.
3. Adjust the stroke width, fill color, stroke color, and opacity as desired.
4. Set the desired output size.
5. Specify the output directory where you want the SVG files to be saved.
6. Click "Vectorize" to convert the images to SVG format.
7. The SVG files will be saved in the specified output directory, and you can also download them directly from the interface.

## Troubleshooting

If you encounter any issues:
1. Ensure Node.js and potrace are correctly installed.
2. Check that all Python dependencies are installed.
3. Make sure you're running the app from the correct directory.
4. Check the `svgmaker.log` file for error messages and debugging information.

## Log File

The application generates a log file (`svgmaker.log`) in the project directory. This file contains important information about the app's operation, including any errors that occur. If you encounter issues, please check this log file for more details.

## License

[Add your license information here]