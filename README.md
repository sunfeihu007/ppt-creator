# PPT Creator —— AI-Powered Presentation Generator

> **Powered by MrSuperOne**

A structured PPT generation assistant that creates professional presentations through conversational planning and AI image generation.

## Features

- **Conversational Planning**: Discuss outline, content, and style before generating
- **AI Image Generation**: Uses Gemini NanoBanana 2 (gemini-3.1-flash-image-preview) for high-quality slide images
- **Built-in Style System**: Includes "LianTong Red" style with 3D glass morphism effects
- **Speaker Notes**: Automatically generates detailed speaker notes for each slide
- **PPTX Assembly**: Combines generated images into a complete PowerPoint file

## Workflow

1. **Outline Discussion** — Determine the main sections and structure
2. **Content Planning** — Define key points for each section
3. **Page Allocation** — Assign content to specific pages
4. **Style Selection** — Choose visual style (default: LianTong Red)
5. **Framework Pages** — Generate cover, table of contents, and closing pages
6. **Content Pages** — Generate each content page with detailed prompts
7. **Assembly** — Combine all pages into a PPTX file with speaker notes

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ppt-creator.git
cd ppt-creator

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### 1. Set up your API Key

```bash
export GOOGLE_API_KEY='your_api_key_here'
```

#### 2. Generate slide images

Edit `generate_ppt_example.py` to define your slides, then run:

```bash
python generate_ppt_example.py
```

#### 3. Assemble into PPTX

```bash
python build_ppt_example.py
```

## Style System

### LianTong Red Style (Default)

A premium business-tech style featuring:
- **Background**: Light gray-white gradient with subtle geometric grid
- **Primary Color**: China Unicom Red (`#E60012`)
- **3D Effects**: Glass morphism, isometric layers, realistic shadows
- **Icons**: Unified red/gray color scheme, no colorful icons
- **Typography**: Clean modern fonts, professional layout

### Customizing Colors

To change the primary color while keeping all other style elements:

1. Replace `#E60012` with your desired color in the prompts
2. Keep all 3D effects, glass morphism, and layout elements unchanged
3. Regenerate the pages

## Project Structure

```
ppt-creator/
├── SKILL.md                          # Main skill definition
├── README.md                         # This file
├── generate_ppt_example.py           # Example image generation script
├── build_ppt_example.py              # Example PPTX assembly script
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore rules
├── references/
│   └── styles/
│       └── liantong-red.md          # LianTong Red style definition
└── evals/
    └── evals.json                    # Evaluation test cases
```

## Style Definition

The `references/styles/liantong-red.md` file contains the complete style specification:

- Color palette
- Visual elements (background, 3D effects, icons)
- Layout rules
- Typography guidelines
- Page type templates (cover, architecture, content, case study)

## API Reference

### Gemini NanoBanana 2

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent`
- **Authentication**: `x-goog-api-key` header
- **Image Size**: 2K or 4K, 16:9 aspect ratio
- **Retry Strategy**: Up to 8 attempts with exponential backoff

### PPTX Assembly

Uses `python-pptx` to create presentations with:
- 16:9 slide ratio (13.333 x 7.5 inches)
- Blank slide layout
- Full-bleed image placement
- Speaker notes support

## Best Practices

### Do's
- Plan outline before generating
- Use consistent style throughout
- Add speaker notes for each slide
- Review generated images before assembly

### Don'ts
- Don't include API keys in code (use environment variables)
- Don't use placeholder text ("internal use", "presenter name")
- Don't use colorful icons (maintain red/gray scheme)
- Don't make specific percentage promises in content

## Example Prompt Structure

```
Create a premium professional PPT slide, 16:9 ratio, 
light gray-white gradient background with subtle geometric grid.

Title: [Your Title]
Content:
- [Point 1]
- [Point 2]
- [Point 3]

Style requirements:
- Premium glass morphism design
- China Unicom red (#E60012) as primary accent
- Photorealistic 3D rendering
- Professional business style
- NO placeholder text
```

## License

MIT License — feel free to use and modify for your projects.

---

**Powered by MrSuperOne**
