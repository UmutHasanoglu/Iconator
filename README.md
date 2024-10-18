# Iconator

This application converts raster images to SVG format, allows for basic styling of the resulting SVGs, and can create Icon sheets using single SVG Icons.

## Installation and Setup
1. Clone the repository
2. Run "install.bat" file
It will create a virtual environment and install dependencies.
3. After the installation, run the "start-app.bat" file

## Prerequisites
Potrace (https://potrace.sourceforge.net/)
Python

## Usage

SVG Maker:
1. Run the application
2. Upload one or more image files.
3. Adjust the stroke width, fill color, stroke color, and opacity as desired.
4. Set the desired output size.
5. Specify the output directory where you want the SVG files to be saved.
6. Click "Vectorize" to convert the images to SVG format.
7. The SVG files will be saved in the specified output directory, and you can also download them directly from the interface.

Icon Sheet:
1. Upload SVG icons.
2. Select the number of columns, padding, background color, and sheet width.
3. Specify if you want a transparent background.
4. Click "Generate Icon Sheet".

## Log File

The application generates a log file (`svgmaker.log`) in the project directory. This file contains important information about the app's operation, including any errors that occur. If you encounter issues, please check this log file for more details.

## License

Apache-2.0 license
