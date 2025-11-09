# Live2D Models

## Shizuka Model Setup

This directory should contain the Live2D Shizuka model files.

### Required Files

Place the Shizuka Live2D model in the `shizuku/` folder with the following structure:

```
live2d-models/
└── shizuku/
    ├── shizuku.model.json       # Main model configuration file
    ├── shizuku.moc              # Model data file
    ├── *.png                    # Texture files
    ├── motions/                 # Animation files (optional)
    └── expressions/             # Expression files (optional)
```

### How to Get the Shizuka Model

#### Option 1: From Live2D Official Samples
1. Visit https://www.live2d.com/en/download/sample-data/
2. Download the "Shizuku" sample model
3. Extract the files into `public/live2d-models/shizuku/`

#### Option 2: From Open-LLM-VTuber Repository
1. Visit https://github.com/Open-LLM-VTuber/Open-LLM-VTuber
2. Navigate to their live2d-models directory
3. Download the Shizuku model files
4. Place them in this directory

### Model License

The Shizuka model is provided by Live2D Inc. under their Free Material License Agreement.
Please ensure you comply with their licensing terms when using the model.

**Important:** Do not commit the model files to Git if you're using a public repository.
Add `live2d-models/*` to your `.gitignore` file.

### Troubleshooting

If the model doesn't load:
1. Check the browser console for error messages
2. Verify the model.json path is correct
3. Ensure all texture files (.png) are in the same directory
4. Check that the file names match exactly (case-sensitive)
