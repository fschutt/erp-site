# ERP System Static Site Generator

A sophisticated, multilingual static site generator for your ERP system with an intellectual aesthetic inspired by high-quality editorial sites.

## Features

- **Multilingual Support**: Easy translation management with JSON files
- **Fully Configurable**: Control sections, ordering, and visibility via `config.json`
- **Language-Specific Configuration**: Different phone numbers and settings per language
- **Modern Design**: Clean, editorial-style design with serif and sans-serif typography
- **Responsive**: Works perfectly on all devices
- **Static Output**: Fast, secure, and easy to deploy

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions workflow
├── translations/
│   ├── en.json                 # English translations
│   └── de.json                 # German translations
├── config.json                 # Site configuration
├── template.html               # HTML template
├── styles.css                  # Stylesheet
├── generate.py                 # Site generator script
└── dist/                       # Generated output (created by script)
```

## Configuration

### config.json

```json
{
  "demo_url": "https://demo.yourerp.com",
  "default_language": "en",
  "languages": {
    "en": {
      "name": "English",
      "phone": "+1-555-0123"
    },
    "de": {
      "name": "Deutsch",
      "phone": "+49-621-123456"
    }
  },
  "sections": [...]
}
```

**Key Options:**
- `demo_url`: URL for the "View Demo" button
- `default_language`: Language for the root index.html
- `languages`: Each language must have `name` and `phone`
- `sections`: Array of section configurations

**Section Types:**
- `hero`: Main header with CTA buttons
- `features`: Grid of feature cards
- `testimonial`: Customer quote
- `cta`: Call-to-action section

Each section can be enabled/disabled with the `enabled` flag and reordered by changing array position.

### Translation Files

Create one JSON file per language in the `translations/` directory:

```json
{
  "site_title": "Your Site Title",
  "hero_title": "Main Headline",
  "view_demo": "View Demo",
  "contact_sales": "Contact Sales",
  ...
}
```

## Usage

### Local Development

```bash
# Generate the site
python generate.py

# View output in dist/ folder
# Open dist/index.html or dist/en/index.html in your browser
```

### GitHub Pages Deployment

1. Push your repository to GitHub
2. Enable GitHub Pages in repository settings
3. Set source to "GitHub Actions"
4. The workflow will automatically run on push to main

The site will be available at `https://yourusername.github.io/your-repo/`

## Customization

### Adding a New Language

1. Create `translations/[lang].json` with all translation keys
2. Add language to `config.json`:
   ```json
   "languages": {
     "fr": {
       "name": "Français",
       "phone": "+33-1-23-45-67-89"
     }
   }
   ```

### Adding New Sections

Edit `config.json` and add to the `sections` array:

```json
{
  "type": "cta",
  "enabled": true,
  "title": "cta_new_title",
  "description": "cta_new_description"
}
```

Then add the translation keys to all language files.

### Reordering Sections

Simply rearrange the order in the `sections` array in `config.json`.

### Disabling Sections

Set `"enabled": false` for any section you want to hide.

### Styling Changes

Edit `styles.css` to customize:
- Colors: Change CSS variables in `:root`
- Fonts: Update Google Fonts link in `template.html`
- Layout: Modify grid and spacing values

## Design Philosophy

The design follows an intellectual, editorial aesthetic inspired by publications like The New Yorker:

- **Typography**: Crimson Pro serif for headlines, Inter sans-serif for body
- **Layout**: Generous whitespace and readable line lengths
- **Color**: Muted, sophisticated palette with subtle borders
- **Hierarchy**: Clear visual hierarchy with varied font sizes
- **Restraint**: Minimal decoration, focus on content

## License

Customize this section with your license information.
