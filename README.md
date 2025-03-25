# Line-dose Analyzer (Range & SOBP)

A Python GUI application for analyzing depth-dose curves from radiation therapy planning (from Raystation) and measurement data (Zebra, IBA).

## Features

- **Data Import**: Load and analyze TXT (Raystation) and CSV (Zebra, IBA) files
- **Depth-Dose Visualization**: Plot normalized depth-dose curves with automatic color coding
- **Key Metrics**: Calculate and display important dosimetric parameters:
  - D90 (range): Depth of distal 90% dose
  - SOBP (Spread-Out Bragg Peak): Width between proximal 95% and distal 90%
  - D50: Depth of distal 50% dose
  - D20: Depth of distal 20% dose 
  - D10: Depth of distal 10% dose
- **Data Comparison**: Compare planned vs. measured depth-dose curves
- **Export Options**: Save screen captures and data

## Requirements

- Python 3.6+
- tkinter
- matplotlib
- numpy
- Pillow (for screen capture)

## Usage

1. Run the application:
   ```
   python Line_dose.py
   ```

2. Click "Open files" to select your depth-dose data files:
   - TXT files: Treatment planning system output
   - CSV files: Measurement data

3. View the normalized depth-dose curves and analysis results:
   - Left panel: Depth-dose curve visualization
   - Right panel: Range and SOBP metrics table

4. Use "Save screen" to capture the entire application window

## Key Functions

- **Data Normalization**: Doses normalized to 100% at SOBP center
- **Interpolation**: Uses linear interpolation to find exact depth values for key metrics
- **Visualization**: Different line styles for plan (solid) vs. measurement (dashed)

## License

[MIT License](LICENSE)

## Contact

For questions or support, please [open an issue](https://github.com/yourusername/line-dose-analyzer/issues) or contact [your-email@example.com].
