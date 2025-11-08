#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil
import base64
import re

def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_foam_svg() -> str:
    """Load foam.svg content for inline use"""
    foam_path = Path('assets/foam.svg')
    if foam_path.exists():
        with open(foam_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
            # Remove XML declaration and adjust style for inline use
            svg_content = svg_content.replace('<?xml version="1.0" encoding="utf-8"?>', '')
            svg_content = svg_content.replace('style="margin: auto; background: none; display: block; z-index: 1; position: relative; shape-rendering: auto;"', 
                                             'style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; opacity: 0.5; transform: scale(2); pointer-events: none;"')
            return svg_content
    return ''

def simple_markdown_to_html(md_text: str) -> str:
    """Convert basic markdown to HTML"""
    html = md_text
    
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Lists
    lines = html.split('\n')
    in_list = False
    result = []
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    if in_list:
        result.append('</ul>')
    html = '\n'.join(result)
    
    # Paragraphs
    html = re.sub(r'\n\n+', '</p><p>', html)
    html = f'<p>{html}</p>'
    
    # Clean up empty paragraphs and extra tags
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>\s*(<h[1-6]>)', r'\1', html)
    html = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*(<ul>)', r'\1', html)
    html = re.sub(r'(</ul>)\s*</p>', r'\1', html)
    
    return html


def load_svg_as_base64(path: str) -> Optional[str]:
    """Load an SVG file and return it as a base64 data URI."""
    try:
        svg_path = Path(path)
        if svg_path.exists():
            with open(svg_path, 'rb') as f:
                svg_data = f.read()
                b64_data = base64.b64encode(svg_data).decode('utf-8')
                return f"data:image/svg+xml;base64,{b64_data}"
    except Exception as e:
        print(f"Warning: Could not load SVG {path}: {e}")
    return None

def translate(key: str, lang_data: Dict[str, str]) -> str:
    return lang_data.get(key, key)

def get_image_url(section: Dict[str, Any], lang: str) -> str:
    images = section.get('image', {})
    if isinstance(images, dict):
        return images.get(lang, images.get('default', ''))
    return images if images else ''

def render_nav_logo(config: Dict[str, Any], lang_data: Dict[str, str], has_gradient: bool) -> str:
    """Render the navigation logo, trying SVG first, then falling back to text."""
    # Determine which logo to use based on background
    logo_file = 'assets/logo-dark.svg' if has_gradient else 'assets/logo-light.svg'
    logo_data = load_svg_as_base64(logo_file)
    
    if logo_data:
        brand_text = translate('site_brand', lang_data)
        return f'<img src="{logo_data}" alt="{brand_text}" aria-label="{brand_text}">'
    else:
        # Fallback to text
        return translate('site_brand', lang_data)

def render_nav(config: Dict[str, Any], lang_data: Dict[str, str], current_page: str, lang: str) -> str:
    base_url = config.get('base_url', '')
    links = []
    for page in config['pages']:
        slug = page['slug']
        # Skip "home" nav item when we're on the home page
        if slug == 'home' and current_page == 'home':
            continue
        title = translate(page['nav_title'], lang_data)
        active = 'active' if slug == current_page else ''
        url = f"{base_url}/{lang}/{slug}.html" if slug != 'home' else f"{base_url}/{lang}/"
        links.append(f'<a href="{url}" class="{active}" role="menuitem">{title}</a>')
    
    # Add docs link (external, language-specific)
    docs_url_config = config.get('docs_url', '#')
    if isinstance(docs_url_config, dict):
        docs_url = docs_url_config.get(lang, docs_url_config.get('en', '#'))
    else:
        docs_url = docs_url_config
    docs_title = translate('nav_docs', lang_data)
    docs_label = translate('nav_docs_label', lang_data)
    links.append(f'<a href="{docs_url}" target="_blank" rel="noopener noreferrer" role="menuitem" aria-label="{docs_label}">{docs_title}</a>')
    
    return ' '.join(links)

def render_lang_switcher(config: Dict[str, Any], current_page: str, current_lang: str) -> str:
    base_url = config.get('base_url', '')
    links = []
    for l, ldata in config['languages'].items():
        # Only show languages that are NOT the current language
        if l != current_lang:
            url = f"{base_url}/{l}/{current_page}.html" if current_page != 'home' else f"{base_url}/{l}/"
            links.append(f'<a href="{url}" role="menuitem" lang="{l}">{ldata["name"]}</a>')
    return ' '.join(links)  # Join without divider

def render_hero(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    demo_url = config['demo_url']
    calendly_url = config.get('calendly_url', '')
    phone = config['languages'][lang].get('phone', '')
    base_url = config.get('base_url', '')
    
    # Handle gradient background
    gradient = section.get('gradient', config.get('default_gradient', ''))
    has_gradient = bool(gradient)
    gradient_style = f' style="background: {gradient};"' if gradient else ''
    gradient_class = ' has-gradient' if has_gradient else ''
    
    # Handle media (image or video)
    media_config = section.get('media', section.get('image', {}))
    media_type = section.get('media_type', 'image')
    
    if isinstance(media_config, dict):
        media_url = media_config.get(lang, media_config.get('default', ''))
        width = media_config.get('width', '')
        height = media_config.get('height', '')
    else:
        media_url = media_config if media_config else ''
        width = ''
        height = ''
    
    if media_url and not media_url.startswith('http'):
        media_url = base_url + media_url
    
    size_attrs = ''
    if width:
        size_attrs += f' width="{width}"'
    if height:
        size_attrs += f' height="{height}"'
    
    # Load foam SVG inline
    foam_svg = load_foam_svg()
    
    # Generate media HTML (image or video with foam.svg behind)
    media_html = ''
    if media_url:
        if media_type == 'video':
            media_html = f'''<div class="hero-image-wrapper">
                {foam_svg}
                <video src="{media_url}" class="hero-video" autoplay loop muted playsinline{size_attrs} aria-label="{title}"></video>
            </div>'''
        else:
            media_html = f'''<div class="hero-image-wrapper">
                {foam_svg}
                <img src="{media_url}" alt="{title}" class="hero-image"{size_attrs}>
            </div>'''
    
    # Generate CTA buttons
    cta_buttons = f'<a href="{demo_url}" class="btn btn-primary btn-hero-primary">{translate("online_demo", lang_data)}</a>'
    
    if calendly_url:
        cta_buttons += f'<a href="{calendly_url}" class="btn btn-secondary btn-hero-secondary" target="_blank" rel="noopener">{translate("book_demo", lang_data)}</a>'
    
    # Generate Google Reviews section (inline in hero)
    google_reviews_html = ''
    if config.get('google_reviews_rating'):
        rating = config.get('google_reviews_rating', 5.0)
        review_count = config.get('google_reviews_count', 0)
        
        reviews_url_config = config.get('google_reviews_url', '')
        if isinstance(reviews_url_config, dict):
            reviews_url = reviews_url_config.get(lang, reviews_url_config.get('en', ''))
        else:
            reviews_url = reviews_url_config
        
        # Generate stars (round down to avoid half-star rendering issues)
        full_stars = int(rating)
        stars_html = '★' * full_stars
        empty_stars = 5 - full_stars
        stars_html += '☆' * empty_stars
        
        rating_text = f"{rating} {translate('google_reviews_text', lang_data)}"
        if review_count > 0:
            rating_text += f" ({review_count} {translate('reviews', lang_data)})"
        
        # Full text for screen readers
        stars_aria = f"{rating} {translate('google_reviews_text', lang_data)}"
        if review_count > 0:
            stars_aria += f", {review_count} {translate('reviews', lang_data)}"
        
        google_reviews_html = f'''
                <div class="hero-google-reviews">
                    <div class="hero-google-reviews-stars" role="img" aria-label="{stars_aria}">
                        <span class="stars" aria-hidden="true">{stars_html}</span>
                        <span class="rating-text" aria-hidden="true">{rating_text}</span>
                    </div>
                    <a href="{reviews_url}" target="_blank" rel="noopener" class="hero-reviews-link">{translate('see_all_reviews', lang_data)} →</a>
                </div>'''
    
    return f'''
    <section class="hero{gradient_class}"{gradient_style} aria-labelledby="hero-heading">
        <div class="container">
            <div class="hero-content">
                <h1 id="hero-heading" tabindex="0" role="heading" aria-level="1">{title}</h1>
                <p class="hero-subtitle" tabindex="0" role="text">{subtitle}</p>
                <div class="cta-buttons">
                    {cta_buttons}
                </div>{google_reviews_html}
            </div>
            {media_html}
        </div>
    </section>'''

def render_text_section(section: Dict[str, Any], lang_data: Dict[str, str], lang: str, config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    content = translate(section['content'], lang_data)
    layout = section.get('layout', 'text-only')
    base_url = config.get('base_url', '')
    
    # Generate unique section ID from title for aria-labelledby
    section_id = section.get('title', 'section').replace('_', '-')
    heading_id = f"{section_id}-heading"
    
    # Check if this is the first content section
    is_first_content = section.get('is_first_content', False)
    first_class = ' first-content-section' if is_first_content else ''
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    image_config = section.get('image', {})
    if isinstance(image_config, dict):
        image_url = image_config.get(lang, image_config.get('default', ''))
        width = image_config.get('width', '')
        height = image_config.get('height', '')
    else:
        image_url = image_config if image_config else ''
        width = ''
        height = ''
    
    if image_url and not image_url.startswith('http'):
        image_url = base_url + image_url
    
    size_attrs = ''
    if width:
        size_attrs += f' width="{width}"'
    if height:
        size_attrs += f' height="{height}"'
    
    image_html = f'<img src="{image_url}" alt="{title}"{size_attrs}>' if image_url else ''
    
    # Create aria-describedby from content preview (first 200 chars)
    content_preview = content.replace('<p>', '').replace('</p>', ' ').strip()[:200]
    
    if layout == 'image-left' and image_html:
        return f'''
    <section class="text-section layout-image-left {bg_class}{first_class}"{bg_style} tabindex="0" role="region" aria-labelledby="{heading_id}" aria-label="{title}">
        <div class="container">
            <div class="content-grid">
                <div class="content-image">{image_html}</div>
                <div class="content-text">
                    <h2 id="{heading_id}">{title}</h2>
                    <div class="prose">{content}</div>
                </div>
            </div>
        </div>
    </section>'''
    elif layout == 'image-right' and image_html:
        return f'''
    <section class="text-section layout-image-right {bg_class}{first_class}"{bg_style} tabindex="0" role="region" aria-labelledby="{heading_id}" aria-label="{title}">
        <div class="container">
            <div class="content-grid">
                <div class="content-text">
                    <h2 id="{heading_id}">{title}</h2>
                    <div class="prose">{content}</div>
                </div>
                <div class="content-image">{image_html}</div>
            </div>
        </div>
    </section>'''
    else:
        return f'''
    <section class="text-section {bg_class}{first_class}"{bg_style} tabindex="0" role="region" aria-labelledby="{heading_id}" aria-label="{title}">
        <div class="container">
            <h2 id="{heading_id}">{title}</h2>
            <div class="prose">{content}</div>
            {f'<div class="section-image">{image_html}</div>' if image_html else ''}
        </div>
    </section>'''

def render_features_grid(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    base_url = config.get('base_url', '')
    items_data = section.get('items', [])
    
    # Check if this is the first content section
    is_first_content = section.get('is_first_content', False)
    first_class = ' first-content-section' if is_first_content else ''
    
    # Get gradient from section, fallback to config default
    gradient = section.get('gradient', config.get('default_gradient', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'))
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    # Generate unique section ID for aria-labelledby
    section_id = section.get('title', 'features').replace('_', '-')
    heading_id = f"{section_id}-heading"
    
    # Simple 2x2 grid with checkerboard gradient pattern
    items = []
    for idx, feature in enumerate(items_data):
        # Checkerboard: apply gradient to positions 0 and 3 (top-left and bottom-right)
        apply_gradient = (idx % 4 == 0 or idx % 4 == 3)
        items.append(render_feature_card(feature, lang_data, base_url, apply_gradient, gradient))
    
    return f'''
    <section class="features-section {bg_class}{first_class}"{bg_style} tabindex="0" role="region" aria-labelledby="{heading_id}" aria-label="{title}">
        <div class="container">
            <h2 id="{heading_id}">{title}</h2>
            <div class="features-grid grid-2x2" role="list">
                {chr(10).join(items)}
            </div>
        </div>
    </section>'''

def render_feature_card(feature: Dict[str, Any], lang_data: Dict[str, str], base_url: str, apply_gradient: bool, gradient: str) -> str:
    """Render a single feature card."""
    feat_title = translate(feature['title'], lang_data)
    feat_desc = translate(feature.get('description', ''), lang_data)
    
    # Handle media (image or video)
    media_config = feature.get('media', feature.get('image', ''))
    media_type = feature.get('media_type', 'image')
    width = feature.get('width', '')
    height = feature.get('height', '')
    
    media_html = ''
    if media_config:
        if not media_config.startswith('http'):
            media_url = base_url + media_config
        else:
            media_url = media_config
        
        # Check if image file exists (for local files)
        if not media_config.startswith('http'):
            # Remove leading slash and 'assets/' if present to avoid double path
            clean_path = media_config.lstrip('/').replace('assets/', '', 1)
            image_path = Path('assets') / clean_path
            if not image_path.exists():
                print(f"Warning: Image not found: {image_path} for feature '{feat_title}' - skipping image")
                media_html = ''
            else:
                size_attrs = ''
                if width:
                    size_attrs += f' width="{width}"'
                if height:
                    size_attrs += f' height="{height}"'
                
                if media_type == 'video':
                    media_html = f'<video src="{media_url}" class="feature-video" autoplay loop muted playsinline{size_attrs} aria-label="{feat_title}"></video>'
                else:
                    media_html = f'<img src="{media_url}" alt="{feat_title}" class="feature-image"{size_attrs}>'
        else:
            # External URLs - assume they work
            size_attrs = ''
            if width:
                size_attrs += f' width="{width}"'
            if height:
                size_attrs += f' height="{height}"'
            
            if media_type == 'video':
                media_html = f'<video src="{media_url}" class="feature-video" autoplay loop muted playsinline{size_attrs} aria-label="{feat_title}"></video>'
            else:
                media_html = f'<img src="{media_url}" alt="{feat_title}" class="feature-image"{size_attrs}>'
    
    # Don't show icon fallback - just leave empty if no media
    
    # Render bullets if present
    bullet_count = len(feature.get('bullets', []))
    bullets_html = ''
    if bullet_count > 0:
        bullet_items = []
        for b in feature.get('bullets', []):
            bullet_text = translate(b, lang_data)
            # Make text before ":" bold
            if ':' in bullet_text:
                parts = bullet_text.split(':', 1)
                bullet_text = f'<strong>{parts[0]}</strong>:{parts[1]}'
            bullet_items.append(f'<li>{bullet_text}</li>')
        bullets_html = f'<ul>{chr(10).join(bullet_items)}</ul>'
    
    desc_html = f'<p>{feat_desc}</p>' if feat_desc else ''
    
    # Create accessible label with all content
    bullets_text = ' '.join([translate(b, lang_data).replace(':', ' - ') for b in feature.get('bullets', [])])
    aria_label = f"{feat_title}. {feat_desc} {bullets_text}".strip()
    
    # Apply gradient background based on checkerboard pattern
    card_class = 'has-gradient' if apply_gradient else ''
    card_style = f' style="--card-gradient: {gradient};"' if apply_gradient else ''
    
    return f'''
        <article class="feature-card {card_class}"{card_style} role="region" aria-label="{aria_label}" tabindex="0">
            {media_html}
            <h3 role="heading" aria-level="3">{feat_title}</h3>
            {desc_html}
            {bullets_html}
        </article>'''

def render_feature_categories(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    categories_data = section.get('categories', [])
    
    # Get gradient from section or config
    gradient = section.get('gradient', config.get('default_gradient', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'))
    has_section_gradient = bool(section.get('background', ''))
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if has_section_gradient:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    # For desktop 2/1 layout: determine threshold based on median
    items_with_counts = []
    feature_counts = []
    for category in categories_data:
        feature_count = len(category.get('features', []))
        items_with_counts.append((category, feature_count))
        feature_counts.append(feature_count)
    
    # Calculate median feature count as threshold
    if feature_counts:
        sorted_counts = sorted(feature_counts)
        median = sorted_counts[len(sorted_counts) // 2]
        threshold = median
    else:
        threshold = 0
    
    # Create brick pattern: pair large items with small items
    brick_pattern = []
    used_indices = set()
    
    i = 0
    while i < len(items_with_counts):
        if i in used_indices:
            i += 1
            continue
            
        large = None
        small = None
        
        # Get two items for a row
        for j in range(i, len(items_with_counts)):
            if j in used_indices:
                continue
                
            item, count = items_with_counts[j]
            if count > threshold and large is None:
                large = (item, count, j)
            elif count <= threshold and small is None:
                small = (item, count, j)
            
            if large and small:
                break
        
        # If we found both, use them
        if large and small:
            brick_pattern.append((large, small))
            used_indices.add(large[2])
            used_indices.add(small[2])
        elif i not in used_indices:
            brick_pattern.append(((items_with_counts[i][0], items_with_counts[i][1], i), None))
            used_indices.add(i)
        
        i += 1
    
    # Determine if we should use 2/1 grid
    use_2_1_grid = len(categories_data) > 2 and any(len(c.get('features', [])) > 0 for c in categories_data)
    grid_class = 'grid-2-1' if use_2_1_grid else ''
    
    categories = []
    for idx, row in enumerate(brick_pattern):
        if row[1] is not None:  # We have both large and small
            large_item, small_item = row
            # Always render large first, small second for consistent layout
            # Alternate gradient: odd rows = right column (small), even rows = left column (large)
            is_odd_row = idx % 2 == 1
            categories.append(render_feature_category(large_item[0], lang_data, not is_odd_row, gradient))
            categories.append(render_feature_category(small_item[0], lang_data, is_odd_row, gradient))
        else:  # Only one item
            categories.append(render_feature_category(row[0][0], lang_data, False, gradient))
    
    return f'''
    <section class="feature-categories-section {bg_class}"{bg_style} aria-labelledby="feature-categories-heading">
        <div class="container">
            <h2 id="feature-categories-heading">{title}</h2>
            <div class="categories-grid {grid_class}">
                {chr(10).join(categories)}
            </div>
        </div>
    </section>'''

def render_feature_category(category: Dict[str, Any], lang_data: Dict[str, str], is_small: bool, gradient: str) -> str:
    """Render a single feature category card."""
    cat_title = translate(category['title'], lang_data)
    features_list = []
    features_text = []
    for feature in category.get('features', []):
        feat_text = translate(feature, lang_data)
        features_list.append(f'<li>{feat_text}</li>')
        features_text.append(feat_text.replace(':', ' - '))
    
    # Create accessible label
    aria_label = f"{cat_title}. {' '.join(features_text)}"
    
    # Small items (1 column) get gradient background
    card_class = 'has-gradient' if is_small else ''
    card_style = f' style="--card-gradient: {gradient};"' if is_small else ''
    
    return f'''
        <article class="feature-card {card_class}"{card_style} role="region" aria-label="{aria_label}" tabindex="0">
            <h3 role="heading" aria-level="3">{cat_title}</h3>
            <ul>
                {chr(10).join(features_list)}
            </ul>
        </article>'''

def render_testimonials(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section.get('title', ''), lang_data)
    testimonials = []
    
    # Check if this is the first content section
    is_first_content = section.get('is_first_content', False)
    first_class = ' first-content-section' if is_first_content else ''
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    for testimonial in section.get('items', []):
        quote = translate(testimonial['quote'], lang_data)
        author = translate(testimonial['author'], lang_data)
        company = translate(testimonial.get('company', ''), lang_data)
        
        author_line = f"{author}, {company}" if company else author
        # Add tabindex and aria-label for each testimonial
        testimonials.append(f'''
        <article class="testimonial-card" tabindex="0" role="article" aria-label="Testimonial from {author_line}">
            <blockquote>
                <p>"{quote}"</p>
                <footer> -  {author_line}</footer>
            </blockquote>
        </article>''')
    
    title_html = f'<h2 id="testimonials-heading">{title}</h2>' if title else ''
    aria_label = f' aria-labelledby="testimonials-heading" aria-label="{title}"' if title else ' aria-label="Customer testimonials"'
    
    return f'''
    <section class="testimonials-section {bg_class}{first_class}"{bg_style} tabindex="0" role="region"{aria_label}>
        <div class="container">
            {title_html}
            <div class="testimonials-grid" role="list">
                {chr(10).join(testimonials)}
            </div>
        </div>
    </section>'''

def render_google_reviews(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    rating = section.get('rating', 5.0)
    review_url = section.get('review_url', '')
    review_count = section.get('review_count', 0)
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    # Generate star display (filled and empty stars)
    full_stars = int(rating)
    half_star = (rating - full_stars) >= 0.5
    stars_html = '★' * full_stars
    if half_star:
        stars_html += '⯨'
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    stars_html += '☆' * empty_stars
    
    rating_text = f"{rating} {translate('google_reviews_text', lang_data)}"
    if review_count > 0:
        rating_text += f" ({review_count} {translate('reviews', lang_data)})"
    
    link_html = ''
    if review_url:
        link_html = f'''
            <div class="google-reviews-link">
                <a href="{review_url}" target="_blank" rel="noopener">{translate('see_all_reviews', lang_data)}</a>
            </div>'''
    
    return f'''
    <section class="google-reviews-section {bg_class}"{bg_style} aria-label="Google reviews">
        <div class="container">
            <div class="google-reviews-content">
                <div class="google-reviews-stars">
                    <span class="stars" aria-label="{rating} stars">{stars_html}</span>
                    <span class="rating-text">{rating_text}</span>
                </div>
                {link_html}
            </div>
        </div>
    </section>'''

def render_faq(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section.get('title', ''), lang_data)
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    faq_items = []
    for idx, item in enumerate(section.get('items', [])):
        question = translate(item['question'], lang_data)
        answer = translate(item['answer'], lang_data)
        
        # Generate unique IDs for aria-controls
        item_id = f"faq-item-{idx}"
        answer_id = f"faq-answer-{idx}"
        
        faq_items.append(f'''
        <div class="faq-item" id="{item_id}" tabindex="0" role="article">
            <h3>
                <button class="faq-question" onclick="this.parentElement.parentElement.classList.toggle('active'); this.setAttribute('aria-expanded', this.parentElement.parentElement.classList.contains('active'));" aria-expanded="false" aria-controls="{answer_id}" aria-label="{question}">
                    {question}
                </button>
            </h3>
            <div class="faq-answer" id="{answer_id}" role="region" aria-label="Answer to {question}">
                <p>{answer}</p>
            </div>
        </div>''')
    
    return f'''
    <section class="faq-section {bg_class}"{bg_style} tabindex="0" role="region" aria-labelledby="faq-heading" aria-label="{title}">
        <div class="container">
            <h2 id="faq-heading">{title}</h2>
            <div class="faq-list" role="list">
                {chr(10).join(faq_items)}
            </div>
        </div>
    </section>'''

def render_contact_form(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    phone = config['languages'][lang].get('phone', '')
    email = config.get('contact_email', '')
    
    # Check if this is the first content section
    is_first_content = section.get('is_first_content', False)
    first_class = ' first-content-section' if is_first_content else ''
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    subtitle_html = f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''
    
    return f'''
    <section class="contact-section {bg_class}{first_class}"{bg_style} tabindex="0" role="region" aria-labelledby="contact-heading" aria-label="{title}">
        <div class="container">
            <h2 id="contact-heading">{title}</h2>
            {subtitle_html}
            <div class="contact-info">
                <div class="contact-item">
                    <strong>{translate("contact_phone", lang_data)}:</strong>
                    <a href="tel:{phone}" aria-label="{translate('contact_phone', lang_data)}: {phone}">{phone}</a>
                </div>
                <div class="contact-item">
                    <strong>{translate("contact_email", lang_data)}:</strong>
                    <a href="mailto:{email}" aria-label="{translate('contact_email', lang_data)}: {email}">{email}</a>
                </div>
            </div>
        </div>
    </section>'''

def render_cta_section(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    demo_url = config['demo_url']
    calendly_url = config.get('calendly_url', '')
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    subtitle_html = f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''
    
    cta_buttons = f'<a href="{demo_url}" class="btn btn-primary">{translate("view_demo", lang_data)}</a>'
    if calendly_url:
        cta_buttons += f'<a href="{calendly_url}" class="btn btn-primary" target="_blank" rel="noopener">{translate("book_demo", lang_data)}</a>'
    
    return f'''
    <section class="cta-section {bg_class}"{bg_style} tabindex="0" role="region" aria-labelledby="cta-heading" aria-label="{title}">
        <div class="container">
            <h2 id="cta-heading">{title}</h2>
            {subtitle_html}
            <div class="cta-buttons">
                {cta_buttons}
            </div>
        </div>
    </section>'''

def parse_blog_post(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse a markdown blog post with frontmatter."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Parse frontmatter
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        # Parse YAML-like frontmatter
        frontmatter = {}
        for line in parts[1].strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        # Get markdown content
        markdown_content = parts[2].strip()
        
        # Convert to HTML
        html_content = simple_markdown_to_html(markdown_content)
        
        return {
            'title': frontmatter.get('title', ''),
            'date': frontmatter.get('date', ''),
            'author': frontmatter.get('author', ''),
            'excerpt': frontmatter.get('excerpt', ''),
            'content': html_content,
            'slug': file_path.stem
        }
    except Exception as e:
        print(f"Error parsing blog post {file_path}: {e}")
        return None

def render_blog_index(section: Dict[str, Any], lang_data: Dict[str, str], lang: str, config: Dict[str, Any]) -> str:
    """Render the blog index page with list of posts."""
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    base_url = config.get('base_url', '')
    
    # Check if this is the first content section
    is_first_content = section.get('is_first_content', False)
    first_class = ' first-content-section' if is_first_content else ''
    
    # Load blog posts for this language
    blog_dir = Path('blog') / lang
    posts = []
    
    if blog_dir.exists():
        for md_file in sorted(blog_dir.glob('*.md'), reverse=True):
            post = parse_blog_post(md_file)
            if post:
                posts.append(post)
    
    # Generate post list HTML
    posts_html = ''
    for post in posts:
        post_url = f"{base_url}/{lang}/blog/{post['slug']}.html"
        posts_html += f'''
        <article class="blog-post-preview">
            <h3><a href="{post_url}">{post['title']}</a></h3>
            <div class="blog-post-meta">
                <span class="blog-post-date">{translate('blog_posted_on', lang_data)} {post['date']}</span>
                {f" {translate('blog_by', lang_data)} {post['author']}" if post['author'] else ''}
            </div>
            <p class="blog-post-excerpt">{post['excerpt']}</p>
            <a href="{post_url}" class="blog-read-more">{translate('blog_read_more', lang_data)} →</a>
        </article>'''
    
    if not posts_html:
        posts_html = '<p>No blog posts available yet.</p>'
    
    return f'''
    <section class="blog-index-section{first_class}" tabindex="0" role="region" aria-labelledby="blog-heading" aria-label="{title}">
        <div class="container">
            <h1 id="blog-heading">{title}</h1>
            <p class="blog-subtitle">{subtitle}</p>
            <div class="blog-posts">
                {posts_html}
            </div>
        </div>
    </section>'''

def render_blog_post(post: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    """Render a single blog post."""
    base_url = config.get('base_url', '')
    blog_index_url = f"{base_url}/{lang}/blog.html"
    
    return f'''
    <section class="blog-post-section" aria-labelledby="post-heading">
        <div class="container">
            <article class="blog-post">
                <div class="blog-post-header">
                    <h1 id="post-heading">{post['title']}</h1>
                    <div class="blog-post-meta">
                        <span class="blog-post-date">{translate('blog_posted_on', lang_data)} {post['date']}</span>
                        {f" {translate('blog_by', lang_data)} {post['author']}" if post['author'] else ''}
                    </div>
                </div>
                <div class="blog-post-content prose">
                    {post['content']}
                </div>
                <div class="blog-post-footer">
                    <a href="{blog_index_url}" class="blog-back-link">{translate('blog_back_to_index', lang_data)}</a>
                </div>
            </article>
        </div>
    </section>'''

def render_section(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    if not section.get('enabled', True):
        return ""
    
    section_type = section['type']
    
    if section_type == 'hero':
        return render_hero(section, lang_data, config, lang)
    elif section_type == 'text':
        return render_text_section(section, lang_data, lang, config)
    elif section_type == 'features_grid':
        return render_features_grid(section, lang_data, config)
    elif section_type == 'feature_categories':
        return render_feature_categories(section, lang_data, config)
    elif section_type == 'testimonials':
        return render_testimonials(section, lang_data)
    elif section_type == 'google_reviews':
        return render_google_reviews(section, lang_data)
    elif section_type == 'faq':
        return render_faq(section, lang_data)
    elif section_type == 'contact':
        return render_contact_form(section, lang_data, config, lang)
    elif section_type == 'cta':
        return render_cta_section(section, lang_data, config)
    elif section_type == 'blog_index':
        return render_blog_index(section, lang_data, lang, config)
    
    return ""

def generate_page(page: Dict[str, Any], config: Dict[str, Any], lang: str, template: str) -> str:
    lang_data = load_json(f"translations/{lang}.json")
    base_url = config.get('base_url', '')
    
    # Check if first section has gradient to determine logo color
    has_gradient = False
    if page.get('sections') and len(page['sections']) > 0:
        first_section = page['sections'][0]
        if first_section.get('type') == 'hero':
            has_gradient = bool(first_section.get('gradient', config.get('default_gradient', '')))
    
    sections_html = []
    first_non_hero_found = False
    
    for idx, section in enumerate(page.get('sections', [])):
        # Clone section dict to avoid modifying original
        section = dict(section)
        
        # Mark first non-hero section for CSS styling (padding-top, larger title)
        if not first_non_hero_found and section.get('type') != 'hero':
            first_non_hero_found = True
            section['is_first_content'] = True
            
            # Do NOT add gradient automatically - let sections specify their own backgrounds
        
        sections_html.append(render_section(section, lang_data, config, lang))
    
    nav_html = render_nav(config, lang_data, page['slug'], lang)
    lang_switcher_html = render_lang_switcher(config, page['slug'], lang)
    nav_logo_html = render_nav_logo(config, lang_data, has_gradient)
    
    phone = config['languages'][lang].get('phone', '')
    email = config.get('contact_email', '')
    
    page_html = template.replace('{{TITLE}}', translate('site_title', lang_data))
    page_html = page_html.replace('{{META_DESCRIPTION}}', translate('site_description', lang_data))
    page_html = page_html.replace('{{LANG}}', lang)
    page_html = page_html.replace('{{BASE_URL}}', base_url)
    page_html = page_html.replace('{{SKIP_TO_CONTENT}}', translate('skip_to_content', lang_data))
    page_html = page_html.replace('{{NAV_HOME_LABEL}}', translate('nav_home_label', lang_data))
    page_html = page_html.replace('{{NAV_LOGO}}', nav_logo_html)
    page_html = page_html.replace('{{NAV_TITLE}}', translate('site_brand', lang_data))
    page_html = page_html.replace('{{NAV_LINKS}}', nav_html)
    page_html = page_html.replace('{{LANG_SWITCHER}}', lang_switcher_html)
    page_html = page_html.replace('{{CONTENT}}', '\n'.join(sections_html))
    page_html = page_html.replace('{{CONTACT_INFO_LABEL}}', translate('contact_info_label', lang_data))
    page_html = page_html.replace('{{CONTACT_PHONE}}', translate('contact_phone', lang_data))
    page_html = page_html.replace('{{CONTACT_EMAIL}}', translate('contact_email', lang_data))
    page_html = page_html.replace('{{DEMO_URL}}', config.get('demo_url', ''))
    page_html = page_html.replace('{{CALENDLY_URL}}', config.get('calendly_url', ''))
    page_html = page_html.replace('{{ONLINE_DEMO}}', translate('online_demo', lang_data))
    page_html = page_html.replace('{{BOOK_DEMO}}', translate('book_demo', lang_data))
    page_html = page_html.replace('{{PHONE}}', phone)
    page_html = page_html.replace('{{EMAIL}}', email)
    page_html = page_html.replace('{{FOOTER_TEXT}}', translate('footer_text', lang_data))
    
    return page_html

def main():
    config = load_json('config.json')
    template = Path('template.html').read_text(encoding='utf-8')
    
    dist = Path('dist')
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    
    (dist / 'assets').mkdir()
    shutil.copy('assets/styles.css', dist / 'assets' / 'styles.css')
    
    # Copy foam.svg if it exists
    foam_svg = Path('assets/foam.svg')
    if foam_svg.exists():
        shutil.copy(foam_svg, dist / 'assets' / 'foam.svg')
    
    for lang in config['languages'].keys():
        lang_dir = dist / lang
        lang_dir.mkdir()
        
        for page in config['pages']:
            html = generate_page(page, config, lang, template)
            
            if page['slug'] == 'home':
                (lang_dir / 'index.html').write_text(html, encoding='utf-8')
            else:
                (lang_dir / f"{page['slug']}.html").write_text(html, encoding='utf-8')
        
        # Generate individual blog post pages
        blog_dir = Path('blog') / lang
        if blog_dir.exists():
            blog_output_dir = lang_dir / 'blog'
            blog_output_dir.mkdir(exist_ok=True)
            
            lang_data = load_json(f'translations/{lang}.json')
            
            for md_file in blog_dir.glob('*.md'):
                post = parse_blog_post(md_file)
                if post:
                    # Create a minimal page structure for blog posts
                    blog_post_html = render_blog_post(post, lang_data, config, lang)
                    
                    nav_html = render_nav(config, lang_data, 'blog', lang)
                    lang_switcher_html = render_lang_switcher(config, 'blog', lang)
                    nav_logo_html = render_nav_logo(config, lang_data, False)
                    
                    phone = config['languages'][lang].get('phone', '')
                    email = config.get('contact_email', '')
                    base_url = config.get('base_url', '')
                    
                    page_html = template.replace('{{TITLE}}', f"{post['title']} - {translate('site_title', lang_data)}")
                    page_html = page_html.replace('{{META_DESCRIPTION}}', post['excerpt'])
                    page_html = page_html.replace('{{LANG}}', lang)
                    page_html = page_html.replace('{{BASE_URL}}', base_url)
                    page_html = page_html.replace('{{SKIP_TO_CONTENT}}', translate('skip_to_content', lang_data))
                    page_html = page_html.replace('{{NAV_HOME_LABEL}}', translate('nav_home_label', lang_data))
                    page_html = page_html.replace('{{NAV_LOGO}}', nav_logo_html)
                    page_html = page_html.replace('{{NAV_TITLE}}', translate('site_brand', lang_data))
                    page_html = page_html.replace('{{NAV_LINKS}}', nav_html)
                    page_html = page_html.replace('{{LANG_SWITCHER}}', lang_switcher_html)
                    page_html = page_html.replace('{{CONTENT}}', blog_post_html)
                    page_html = page_html.replace('{{CONTACT_INFO_LABEL}}', translate('contact_info_label', lang_data))
                    page_html = page_html.replace('{{CONTACT_PHONE}}', translate('contact_phone', lang_data))
                    page_html = page_html.replace('{{CONTACT_EMAIL}}', translate('contact_email', lang_data))
                    page_html = page_html.replace('{{DEMO_URL}}', config.get('demo_url', ''))
                    page_html = page_html.replace('{{CALENDLY_URL}}', config.get('calendly_url', ''))
                    page_html = page_html.replace('{{ONLINE_DEMO}}', translate('online_demo', lang_data))
                    page_html = page_html.replace('{{BOOK_DEMO}}', translate('book_demo', lang_data))
                    page_html = page_html.replace('{{PHONE}}', phone)
                    page_html = page_html.replace('{{EMAIL}}', email)
                    page_html = page_html.replace('{{FOOTER_TEXT}}', translate('footer_text', lang_data))
                    
                    (blog_output_dir / f"{post['slug']}.html").write_text(page_html, encoding='utf-8')
    
    default_lang = config.get('default_language', list(config['languages'].keys())[0])
    base_url = config.get('base_url', '')
    
    # Generate root index.html with language detection
    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raylay ERP - Enterprise Resource Planning</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            text-align: center;
            max-width: 600px;
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        .links {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        a {{
            display: inline-block;
            padding: 14px 32px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        a:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
    </style>
    <script>
        // Detect browser language and redirect
        (function() {{
            var userLang = navigator.language || navigator.userLanguage;
            var langCode = userLang.split('-')[0].toLowerCase();
            var availableLanguages = {list(config['languages'].keys())};
            var baseUrl = '{base_url}';
            
            // Check if user's language is supported
            if (availableLanguages.indexOf(langCode) !== -1) {{
                window.location.href = baseUrl + '/' + langCode + '/';
            }} else {{
                // Fallback to default language
                window.location.href = baseUrl + '/{default_lang}/';
            }}
        }})();
    </script>
</head>
<body>
    <div class="container">
        <h1>Raylay ERP</h1>
        <p>Please select your language:</p>
        <div class="links">'''
    
    for lang_code, lang_data in config['languages'].items():
        lang_name = lang_data['name']
        index_html += f'\n            <a href="{base_url}/{lang_code}/">{lang_name}</a>'
    
    index_html += '''
        </div>
    </div>
</body>
</html>'''
    
    (dist / 'index.html').write_text(index_html, encoding='utf-8')

if __name__ == '__main__':
    main()
