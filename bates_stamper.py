import os
import argparse
import subprocess
import shutil
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from io import BytesIO

def create_stamp(text, x, y, size=12, color="#000000", width=None, height=None):
    """Create a PDF with a text stamp at the specified position"""
    # Use provided dimensions or default to letter size
    pagesize = (width, height) if width and height else letter
    
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=pagesize)
    try:
        # Convert hex color to RGB
        c.setFillColor(HexColor(color))
    except:
        # Fallback to black if color is invalid
        print(f"Warning: Invalid color '{color}', using black instead")
        c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text)
    c.save()
    packet.seek(0)
    return packet

def flatten_pdf(input_path, output_path):
    """Flatten a PDF using Ghostscript if available, otherwise use a PyPDF2 fallback method"""
    try:
        # Try using Ghostscript for best results
        gs_command = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", 
                     "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                     "-dPDFSETTINGS=/prepress", f"-sOutputFile={output_path}", 
                     input_path]
        
        subprocess.run(gs_command, check=True)
        print(f"  -> Flattened PDF using Ghostscript")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print(f"  -> Ghostscript not available, using PyPDF2 fallback for flattening")
        
        # PyPDF2 fallback method
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                # Force content stream compression to help with flattening
                writer.add_page(page)
                
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True
        except Exception as e:
            print(f"  -> Error in PyPDF2 fallback flattening: {e}")
            # If flattening fails, copy the original file to output
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                outfile.write(infile.read())
            return False

def apply_bates_stamp(input_path, output_path, bates_prefix, start_number, position='bottom-right', 
                     color="#000000", margin=10, size=12, flatten_output=False):
    """Apply Bates stamp to a PDF file"""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Process each page
    for i, page in enumerate(reader.pages):
        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # Calculate text width (approximate)
        bates_number = f"{bates_prefix}{start_number + i:06d}"
        text_width = len(bates_number) * size * 0.6  # Rough estimate for character width
        
        # Define positions based on actual page dimensions
        positions = {
            'bottom-right': (page_width - margin - text_width, margin),
            'bottom-left': (margin, margin),
            'top-right': (page_width - margin - text_width, page_height - margin - size),
            'top-left': (margin, page_height - margin - size),
            'center': (page_width / 2 - text_width / 2, page_height / 2)
        }
        x, y = positions.get(position, positions['bottom-right'])
        
        # Create stamp for this page with correct page size
        stamp_packet = create_stamp(bates_number, x, y, size=size, color=color, 
                                  width=page_width, height=page_height)
        
        # Create a new reader for the stamp
        stamp_pdf = PdfReader(stamp_packet)
        stamp_page = stamp_pdf.pages[0]
        
        # Create a temporary page object
        output_page = page
        
        # Apply stamp as an overlay
        output_page.merge_page(stamp_page)
        
        # Add the merged page to writer
        writer.add_page(output_page)
    
    temp_output_path = output_path
    
    # Write the output file (either final or temporary)
    if flatten_output:
        temp_output_path = output_path + ".temp.pdf"
    
    with open(temp_output_path, 'wb') as output_file:
        writer.write(output_file)
    
    # If flattening is requested, perform the flattening operation
    if flatten_output:
        flatten_pdf(temp_output_path, output_path)
        try:
            os.remove(temp_output_path)  # Clean up temp file
        except:
            pass  # Ignore errors in cleanup
    
    return start_number + len(reader.pages)

def process_directory(input_dir, output_dir, bates_prefix, start_number, position='bottom-right', 
                     color="#000000", margin=10, size=12, flatten_input=False, flatten_output=False):
    """Process all PDF files in a directory and its subdirectories"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    current_number = start_number
    total_files_processed = 0
    total_files_failed = 0
    
    # Create temp directory for flattened input files if needed
    temp_dir = None
    if flatten_input:
        temp_dir = tempfile.mkdtemp(prefix="bates_temp_")
    
    # Walk through the directory
    for root, _, files in os.walk(input_dir):
        # Create corresponding output subdirectory
        rel_path = os.path.relpath(root, input_dir)
        current_output_dir = os.path.join(output_dir, rel_path) if rel_path != '.' else output_dir
        
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)
        
        # Process PDF files
        for file in files:
            if file.lower().endswith('.pdf'):
                input_path = os.path.join(root, file)
                output_path = os.path.join(current_output_dir, file)
                
                print(f"Processing: {input_path}")
                
                # Flatten input if requested
                if flatten_input:
                    flattened_input_path = os.path.join(temp_dir, file)
                    print(f"  -> Pre-flattening input PDF...")
                    try:
                        flatten_pdf(input_path, flattened_input_path)
                        input_path = flattened_input_path
                    except Exception as e:
                        print(f"  -> Error flattening input: {e}, using original file")
                
                try:
                    # Check if PDF is readable
                    try:
                        test_reader = PdfReader(input_path)
                        num_pages = len(test_reader.pages)
                        print(f"  -> Found {num_pages} pages")
                    except Exception as e:
                        print(f"  -> Warning: Could not read PDF structure: {e}")
                        print(f"  -> Will attempt processing anyway")
                    
                    current_number = apply_bates_stamp(
                        input_path, output_path, bates_prefix, current_number, 
                        position=position, color=color, margin=margin, size=size,
                        flatten_output=flatten_output
                    )
                    print(f"  -> Successfully saved to: {output_path}")
                    total_files_processed += 1
                    
                except Exception as e:
                    print(f"  -> Error processing {input_path}: {e}")
                    total_files_failed += 1
    
    # Clean up temp directory if created
    if temp_dir:
        try:
            shutil.rmtree(temp_dir)
        except:
            print(f"  -> Note: Could not remove temporary directory: {temp_dir}")
    
    total_pages = current_number - start_number
    
    # Print summary
    print(f"\nBates stamping summary:")
    print(f"  - Files successfully processed: {total_files_processed}")
    print(f"  - Files failed: {total_files_failed}")
    print(f"  - Total pages stamped: {total_pages}")
    
    return total_pages

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch Bates stamp PDF files recursively')
    parser.add_argument('input_directory', help='Input directory containing PDF files')
    parser.add_argument('output_directory', help='Output directory for stamped PDF files')
    parser.add_argument('--prefix', default='BATES-', help='Prefix for Bates numbers')
    parser.add_argument('--start', type=int, default=1, help='Starting Bates number')
    parser.add_argument('--position', default='bottom-right', 
                        choices=['bottom-right', 'bottom-left', 'top-right', 'top-left', 'center'],
                        help='Position of the Bates stamp')
    parser.add_argument('--color', default='#000000', help='Hex color code for the Bates stamp (e.g., #FF0000 for red)')
    parser.add_argument('--margin', type=int, default=10, help='Margin from edge in points (1/72 inch)')
    parser.add_argument('--size', type=int, default=12, help='Font size for the Bates stamp')
    parser.add_argument('--flatten-input', action='store_true', 
                       help='Flatten input PDFs before stamping (recommended for complex PDFs with images)')
    parser.add_argument('--flatten-output', action='store_true', 
                       help='Flatten output PDFs after stamping (for better Adobe Reader compatibility)')
    
    args = parser.parse_args()
    
    print(f"Starting Bates stamping with prefix '{args.prefix}' from number {args.start}")
    print(f"Position: {args.position}, Color: {args.color}, Font size: {args.size}")
    
    if args.flatten_input:
        print(f"Input PDF flattening: Enabled (for better processing of complex PDFs)")
    if args.flatten_output:
        print(f"Output PDF flattening: Enabled (for better Adobe Reader compatibility)")
    
    pages_stamped = process_directory(
        args.input_directory, 
        args.output_directory,
        args.prefix,
        args.start,
        args.position,
        args.color,
        args.margin,
        args.size,
        args.flatten_input,
        args.flatten_output
    )
    
    print(f"\nBates stamping complete!")
    print(f"Total pages stamped: {pages_stamped}")
    print(f"Last Bates number: {args.prefix}{args.start + pages_stamped - 1:06d}")
