#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil
import base64

def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

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
        title = translate(page['nav_title'], lang_data)
        active = 'active' if slug == current_page else ''
        url = f"{base_url}/{lang}/{slug}.html" if slug != 'home' else f"{base_url}/{lang}/"
        links.append(f'<a href="{url}" class="{active}" role="menuitem">{title}</a>')
    
    return ' '.join(links)

def render_lang_switcher(config: Dict[str, Any], current_page: str) -> str:
    base_url = config.get('base_url', '')
    links = []
    for l, ldata in config['languages'].items():
        url = f"{base_url}/{l}/{current_page}.html" if current_page != 'home' else f"{base_url}/{l}/"
        links.append(f'<a href="{url}" role="menuitem" lang="{l}">{ldata["name"]}</a>')
    return ' | '.join(links)

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
    style_attrs = ''
    if width:
        size_attrs += f' width="{width}"'
        style_attrs += f'width: {width}px; '
    if height:
        size_attrs += f' height="{height}"'
        style_attrs += f'height: {height}px; '
    
    if style_attrs:
        style_attrs = f' style="{style_attrs}"'
    
    # Generate media HTML (image or video with foam.svg background)
    media_html = ''
    if media_url:
        if media_type == 'video':
            media_html = f'''<div class="hero-image-wrapper"{style_attrs}>
                <video src="{media_url}" class="hero-video" autoplay loop muted playsinline{size_attrs} aria-label="{title}"></video>
            </div>'''
        else:
            media_html = f'''<div class="hero-image-wrapper"{style_attrs}>
                <img src="{media_url}" alt="{title}" class="hero-image"{size_attrs}>
            </div>'''
    
    # Generate CTA buttons
    cta_buttons = f'<a href="{demo_url}" class="btn btn-primary">{translate("view_demo", lang_data)}</a>'
    
    if calendly_url:
        cta_buttons += f'<a href="{calendly_url}" class="btn btn-primary" target="_blank" rel="noopener">{translate("book_demo", lang_data)}</a>'
    
    cta_buttons += f'<a href="tel:{phone}" class="btn btn-secondary">{translate("contact_sales", lang_data)}</a>'
    
    return f'''
    <section class="hero{gradient_class}"{gradient_style} aria-label="Hero section">
        <div class="container">
            <div class="hero-content">
                <h1>{title}</h1>
                <p class="hero-subtitle">{subtitle}</p>
                <div class="cta-buttons">
                    {cta_buttons}
                </div>
            </div>
            {media_html}
        </div>
    </section>'''

def render_text_section(section: Dict[str, Any], lang_data: Dict[str, str], lang: str, config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    content = translate(section['content'], lang_data)
    layout = section.get('layout', 'text-only')
    base_url = config.get('base_url', '')
    
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
    style_attrs = ''
    if width:
        size_attrs += f' width="{width}"'
        style_attrs += f'width: {width}px; '
    if height:
        size_attrs += f' height="{height}"'
        style_attrs += f'height: {height}px; '
    
    if style_attrs:
        style_attrs = f' style="{style_attrs}"'
    
    image_html = f'<img src="{image_url}" alt="{title}"{size_attrs}{style_attrs}>' if image_url else ''
    
    if layout == 'image-left' and image_html:
        return f'''
    <section class="text-section layout-image-left {bg_class}"{bg_style}>
        <div class="container">
            <div class="content-grid">
                <div class="content-image">{image_html}</div>
                <div class="content-text">
                    <h2>{title}</h2>
                    <div class="prose">{content}</div>
                </div>
            </div>
        </div>
    </section>'''
    elif layout == 'image-right' and image_html:
        return f'''
    <section class="text-section layout-image-right {bg_class}"{bg_style}>
        <div class="container">
            <div class="content-grid">
                <div class="content-text">
                    <h2>{title}</h2>
                    <div class="prose">{content}</div>
                </div>
                <div class="content-image">{image_html}</div>
            </div>
        </div>
    </section>'''
    else:
        return f'''
    <section class="text-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            <div class="prose">{content}</div>
            {f'<div class="section-image">{image_html}</div>' if image_html else ''}
        </div>
    </section>'''

def render_features_grid(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    base_url = config.get('base_url', '')
    items_data = section.get('items', [])
    
    # Get gradient from section, fallback to config default
    gradient = section.get('gradient', config.get('default_gradient', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'))
    has_gradient = bool(section.get('background', ''))
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if has_gradient:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    # For desktop 2/1 layout: group features by bullet count
    # Features with more bullets go in 2-column span, fewer in 1-column span
    items_with_counts = []
    for feature in items_data:
        bullet_count = len(feature.get('bullets', []))
        items_with_counts.append((feature, bullet_count))
    
    # Create brick pattern: alternate large-small with small-large
    # Items with fewer bullets (1-column) get gradient background
    brick_pattern = []
    used_indices = set()
    
    i = 0
    while i < len(items_with_counts):
        if i in used_indices:
            i += 1
            continue
            
        # Find next large and small items
        large = None
        small = None
        
        # Get two items for a row
        for j in range(i, len(items_with_counts)):
            if j in used_indices:
                continue
                
            item, count = items_with_counts[j]
            if count >= 3 and large is None:
                large = (item, count, j)
            elif count < 3 and small is None:
                small = (item, count, j)
            
            if large and small:
                break
        
        # If we found both, use them
        if large and small:
            brick_pattern.append((large, small))
            used_indices.add(large[2])
            used_indices.add(small[2])
        # Otherwise just add what we have left
        elif i not in used_indices:
            brick_pattern.append(((items_with_counts[i][0], items_with_counts[i][1], i), None))
            used_indices.add(i)
        
        i += 1
    
    # Determine if we should use 2/1 grid
    use_2_1_grid = len(items_data) > 2 and any(len(f.get('bullets', [])) > 0 for f in items_data)
    grid_class = 'grid-2-1' if use_2_1_grid else ''
    
    items = []
    for idx, row in enumerate(brick_pattern):
        if row[1] is not None:  # We have both large and small
            large_item, small_item = row
            # Alternate the order: even rows are large-small, odd rows are small-large
            if idx % 2 == 0:
                items.append(render_feature_card(large_item[0], lang_data, base_url, False, gradient))
                items.append(render_feature_card(small_item[0], lang_data, base_url, True, gradient))
            else:
                items.append(render_feature_card(small_item[0], lang_data, base_url, True, gradient))
                items.append(render_feature_card(large_item[0], lang_data, base_url, False, gradient))
        else:  # Only one item
            items.append(render_feature_card(row[0][0], lang_data, base_url, False, gradient))
    
    return f'''
    <section class="features-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            <div class="features-grid {grid_class}">
                {chr(10).join(items)}
            </div>
        </div>
    </section>'''

def render_feature_card(feature: Dict[str, Any], lang_data: Dict[str, str], base_url: str, is_small: bool, gradient: str) -> str:
    """Render a single feature card."""
    feat_title = translate(feature['title'], lang_data)
    feat_desc = translate(feature.get('description', ''), lang_data)
    
    # Handle media (image or video)
    media_config = feature.get('media', feature.get('image', ''))
    media_type = feature.get('media_type', 'image')
    width = feature.get('width', '')
    height = feature.get('height', '')
    
    if media_config:
        if not media_config.startswith('http'):
            media_url = base_url + media_config
        else:
            media_url = media_config
        
        size_attrs = ''
        style_attrs = ''
        if width:
            size_attrs += f' width="{width}"'
            style_attrs += f'width: {width}px; '
        if height:
            size_attrs += f' height="{height}"'
            style_attrs += f'height: {height}px; '
        
        if style_attrs:
            style_attrs = f' style="{style_attrs}"'
        
        if media_type == 'video':
            media_html = f'<video src="{media_url}" class="feature-video" autoplay loop muted playsinline{size_attrs}{style_attrs} aria-label="{feat_title}"></video>'
        else:
            media_html = f'<img src="{media_url}" alt="{feat_title}" class="feature-image"{size_attrs}{style_attrs}>'
    else:
        icon = feature.get('icon', '●')
        media_html = f'<div class="feature-icon" aria-hidden="true">{icon}</div>'
    
    # Render bullets if present
    bullet_count = len(feature.get('bullets', []))
    bullets_html = ''
    if bullet_count > 0:
        bullet_items = [f'<li>{translate(b, lang_data)}</li>' for b in feature.get('bullets', [])]
        bullets_html = f'<ul>{chr(10).join(bullet_items)}</ul>'
    
    desc_html = f'<p>{feat_desc}</p>' if feat_desc else ''
    
    # Small items (1 column) get gradient background
    card_class = 'has-gradient' if is_small else ''
    card_style = f' style="--card-gradient: {gradient};"' if is_small else ''
    
    return f'''
        <div class="feature-card {card_class}"{card_style}>
            {media_html}
            <h3>{feat_title}</h3>
            {desc_html}
            {bullets_html}
        </div>'''

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
    
    # For desktop 2/1 layout: group categories by feature count
    items_with_counts = []
    for category in categories_data:
        feature_count = len(category.get('features', []))
        items_with_counts.append((category, feature_count))
    
    # Create brick pattern: alternate large-small with small-large
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
            if count >= 6 and large is None:
                large = (item, count, j)
            elif count < 6 and small is None:
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
            # Alternate the order: even rows are large-small, odd rows are small-large
            if idx % 2 == 0:
                categories.append(render_feature_category(large_item[0], lang_data, False, gradient))
                categories.append(render_feature_category(small_item[0], lang_data, True, gradient))
            else:
                categories.append(render_feature_category(small_item[0], lang_data, True, gradient))
                categories.append(render_feature_category(large_item[0], lang_data, False, gradient))
        else:  # Only one item
            categories.append(render_feature_category(row[0][0], lang_data, False, gradient))
    
    return f'''
    <section class="feature-categories-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            <div class="categories-grid {grid_class}">
                {chr(10).join(categories)}
            </div>
        </div>
    </section>'''

def render_feature_category(category: Dict[str, Any], lang_data: Dict[str, str], is_small: bool, gradient: str) -> str:
    """Render a single feature category card."""
    cat_title = translate(category['title'], lang_data)
    features_list = []
    for feature in category.get('features', []):
        features_list.append(f'<li>{translate(feature, lang_data)}</li>')
    
    # Small items (1 column) get gradient background
    card_class = 'has-gradient' if is_small else ''
    card_style = f' style="--card-gradient: {gradient};"' if is_small else ''
    
    return f'''
        <div class="feature-category {card_class}"{card_style}>
            <h3>{cat_title}</h3>
            <ul>
                {chr(10).join(features_list)}
            </ul>
        </div>'''

def render_testimonials(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section.get('title', ''), lang_data)
    testimonials = []
    
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
        testimonials.append(f'''
        <div class="testimonial-card">
            <blockquote>
                <p>"{quote}"</p>
                <footer>— {author_line}</footer>
            </blockquote>
        </div>''')
    
    title_html = f'<h2>{title}</h2>' if title else ''
    
    return f'''
    <section class="testimonials-section {bg_class}"{bg_style}>
        <div class="container">
            {title_html}
            <div class="testimonials-grid">
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
    <section class="google-reviews-section {bg_class}"{bg_style}>
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
        
        faq_items.append(f'''
        <div class="faq-item">
            <button class="faq-question" onclick="this.parentElement.classList.toggle('active')" aria-expanded="false">
                {question}
            </button>
            <div class="faq-answer">
                <p>{answer}</p>
            </div>
        </div>''')
    
    return f'''
    <section class="faq-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            <div class="faq-list">
                {chr(10).join(faq_items)}
            </div>
        </div>
    </section>'''

def render_contact_form(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    phone = config['languages'][lang].get('phone', '')
    email = config.get('contact_email', '')
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    if background:
        bg_class += ' has-gradient'
    bg_style = f' style="background: {background};"' if background else ''
    
    subtitle_html = f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''
    
    return f'''
    <section class="contact-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            {subtitle_html}
            <div class="contact-info">
                <div class="contact-item">
                    <strong>{translate("contact_phone", lang_data)}:</strong>
                    <a href="tel:{phone}">{phone}</a>
                </div>
                <div class="contact-item">
                    <strong>{translate("contact_email", lang_data)}:</strong>
                    <a href="mailto:{email}">{email}</a>
                </div>
            </div>
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
    for section in page.get('sections', []):
        sections_html.append(render_section(section, lang_data, config, lang))
    
    nav_html = render_nav(config, lang_data, page['slug'], lang)
    lang_switcher_html = render_lang_switcher(config, page['slug'])
    nav_logo_html = render_nav_logo(config, lang_data, has_gradient)
    
    page_html = template.replace('{{TITLE}}', translate('site_title', lang_data))
    page_html = page_html.replace('{{META_DESCRIPTION}}', translate('site_description', lang_data))
    page_html = page_html.replace('{{LANG}}', lang)
    page_html = page_html.replace('{{BASE_URL}}', base_url)
    page_html = page_html.replace('{{NAV_LOGO}}', nav_logo_html)
    page_html = page_html.replace('{{NAV_TITLE}}', translate('site_brand', lang_data))
    page_html = page_html.replace('{{NAV_LINKS}}', nav_html)
    page_html = page_html.replace('{{LANG_SWITCHER}}', lang_switcher_html)
    page_html = page_html.replace('{{CONTENT}}', '\n'.join(sections_html))
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
    
    default_lang = config.get('default_language', list(config['languages'].keys())[0])
    shutil.copy(dist / default_lang / 'index.html', dist / 'index.html')

if __name__ == '__main__':
    main()
