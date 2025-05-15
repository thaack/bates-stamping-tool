# PDF Bates Stamper

A Python utility for batch Bates stamping of PDF documents. This tool allows you to apply sequential Bates numbering to individual PDF files or entire directories of PDFs (including subdirectories).

## Features

- **Recursive Directory Processing**: Automatically processes all PDFs in a directory and its subdirectories.
- **Customizable Bates Numbering**: Define your own prefix and starting number.
- **Flexible Positioning**: Position stamps at various locations on the page.
- **Color Options**: Customize the color of your Bates stamps.
- **PDF Flattening**: Both input and output flattening options for maximum compatibility with PDF viewers like Adobe Reader.
- **Robust Error Handling**: Continues processing even if individual files fail.
- **Detailed Reporting**: Provides comprehensive summary of processed files.

## Requirements

- Python 3.6+
- Required Python packages:
  - PyPDF2
  - reportlab

Optional but recommended:
- Ghostscript (for better PDF flattening)

## Installation

1. Clone or download this repository
2. Install required Python packages:

```bash
pip install PyPDF2 reportlab
```

3. (Optional) Install Ghostscript for better PDF flattening:

**On Ubuntu/Debian (or WSL):**
```bash
sudo apt-get update
sudo apt-get install ghostscript
```

**On Windows:**
Download and install from [Ghostscript official site](https://www.ghostscript.com/releases/gsdnld.html)

## Usage

### Basic Usage

```bash
python bates_stamper.py input_directory output_directory
```

This will process all PDFs in `input_directory` (including subdirectories), add default Bates numbers (BATES-000001, BATES-000002, etc.), and save the results in `output_directory` with the same directory structure.

### Advanced Options

```bash
python bates_stamper.py input_directory output_directory \
  --prefix "CASE-" \
  --start 1000 \
  --position top-right \
  --color "#FF0000" \
  --margin 20 \
  --size 14 \
  --flatten-input \
  --flatten-output
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input_directory` | Directory containing PDF files to stamp | (Required) |
| `output_directory` | Directory where stamped PDFs will be saved | (Required) |
| `--prefix` | Prefix for Bates numbers | BATES- |
| `--start` | Starting Bates number | 1 |
| `--position` | Position of the Bates stamp | bottom-right |
| `--color` | Hex color code for the Bates stamp | #000000 (black) |
| `--margin` | Margin from edge in points (1/72 inch) | 10 |
| `--size` | Font size for the Bates stamp | 12 |
| `--flatten-input` | Flatten input PDFs before stamping | (Disabled) |
| `--flatten-output` | Flatten output PDFs after stamping | (Disabled) |

#### Available Positions
- `bottom-right`
- `bottom-left`
- `top-right`
- `top-left`
- `center`

## Examples

### Example 1: Basic Bates Numbering

```bash
python bates_stamper.py ./documents ./stamped_documents
```

### Example 2: Custom Prefix and Starting Number

```bash
python bates_stamper.py ./evidence ./stamped_evidence --prefix "CASE123-" --start 5000
```

This will create Bates numbers like CASE123-005000, CASE123-005001, etc.

### Example 3: Red Stamps in Top-Left Corner

```bash
python bates_stamper.py ./contracts ./stamped_contracts --position top-left --color "#FF0000" --size 14
```

### Example 4: Handling Problematic PDFs with Flattening

If you encounter issues with blank pages in Adobe Reader:

```bash
python bates_stamper.py ./problematic_pdfs ./fixed_pdfs --flatten-input
```

### Example 5: Maximum Compatibility

For maximum compatibility with all PDF viewers:

```bash
python bates_stamper.py ./documents ./compatible_docs --flatten-input --flatten-output
```

## Troubleshooting

### Blank Pages in Adobe Reader

If the stamped PDFs appear blank in Adobe Reader:
1. Try using the `--flatten-input` option
2. If that doesn't work, try both `--flatten-input` and `--flatten-output`
3. Ensure Ghostscript is installed for better flattening results

### Incorrect Stamp Positioning

If stamps are not positioned correctly:
1. Try adjusting the `--margin` value
2. Use a different `--position` option

### Processing Errors

If specific files fail to process:
1. Check if the original PDF is valid and not password-protected
2. Try using the `--flatten-input` option for complex PDFs

## How It Works

The script:
1. Recursively finds all PDF files in the input directory
2. Optionally flattens input PDFs (if `--flatten-input` is used)
3. Creates a new PDF with the Bates stamp at the specified position
4. Merges the stamp with each page of the original PDF
5. Optionally flattens the output PDF (if `--flatten-output` is used)
6. Saves the result to the output directory, maintaining the original directory structure

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
