#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Any, List
import shutil

def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def translate(key: str, lang_data: Dict[str, str]) -> str:
    return lang_data.get(key, key)

def get_image_url(section: Dict[str, Any], lang: str) -> str:
    images = section.get('image', {})
    if isinstance(images, dict):
        return images.get(lang, images.get('default', ''))
    return images if images else ''

def render_nav(config: Dict[str, Any], lang_data: Dict[str, str], current_page: str, lang: str) -> str:
    base_url = config.get('base_url', '')
    links = []
    for page in config['pages']:
        slug = page['slug']
        title = translate(page['nav_title'], lang_data)
        active = 'active' if slug == current_page else ''
        url = f"{base_url}/{lang}/{slug}.html" if slug != 'home' else f"{base_url}/{lang}/"
        links.append(f'<a href="{url}" class="{active}">{title}</a>')
    
    return ' '.join(links)

def render_lang_switcher(config: Dict[str, Any], current_page: str) -> str:
    base_url = config.get('base_url', '')
    links = []
    for l, ldata in config['languages'].items():
        url = f"{base_url}/{l}/{current_page}.html" if current_page != 'home' else f"{base_url}/{l}/"
        links.append(f'<a href="{url}">{ldata["name"]}</a>')
    return ' | '.join(links)

def render_hero(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    demo_url = config['demo_url']
    calendly_url = config.get('calendly_url', '')
    phone = config['languages'][lang].get('phone', '')
    base_url = config.get('base_url', '')
    
    # Handle gradient background
    gradient = section.get('gradient', '')
    gradient_style = f' style="background: {gradient};"' if gradient else ''
    
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
    
    # Generate media HTML (image or video with foam.svg background)
    media_html = ''
    if media_url:
        if media_type == 'video':
            media_html = f'''<div class="hero-image-wrapper">
                <video src="{media_url}" class="hero-video" autoplay loop muted playsinline{size_attrs}></video>
            </div>'''
        else:
            media_html = f'''<div class="hero-image-wrapper">
                <img src="{media_url}" alt="{title}" class="hero-image"{size_attrs}>
            </div>'''
    
    # Generate CTA buttons
    cta_buttons = f'<a href="{demo_url}" class="btn btn-primary">{translate("view_demo", lang_data)}</a>'
    cta_buttons += f'<a href="tel:{phone}" class="btn btn-secondary">{translate("contact_sales", lang_data)}</a>'
    
    if calendly_url:
        cta_buttons += f'<a href="{calendly_url}" class="btn btn-primary">{translate("book_demo", lang_data)}</a>'
    
    return f'''
    <section class="hero"{gradient_style}>
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
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    bg_style = f' style="background: {background};"' if background else ''
    
    # For desktop 2/1 layout: group features by bullet count
    # Features with more bullets go in 2-column span, fewer in 1-column span
    items_with_counts = []
    for feature in items_data:
        bullet_count = len(feature.get('bullets', []))
        items_with_counts.append((feature, bullet_count))
    
    # Sort by bullet count (descending) for better layout
    items_with_counts.sort(key=lambda x: x[1], reverse=True)
    
    # Determine if we should use 2/1 grid (only if we have mixed bullet counts)
    use_2_1_grid = len(items_with_counts) > 0 and max(x[1] for x in items_with_counts) > 0
    grid_class = 'grid-2-1' if use_2_1_grid else ''
    
    items = []
    for feature, bullet_count in items_with_counts:
        feat_title = translate(feature['title'], lang_data)
        feat_desc = translate(feature.get('description', ''), lang_data)
        
        # Handle media (image or video)
        media_config = feature.get('media', feature.get('image', ''))
        media_type = feature.get('media_type', 'image')
        
        if media_config:
            if not media_config.startswith('http'):
                media_url = base_url + media_config
            else:
                media_url = media_config
            
            if media_type == 'video':
                media_html = f'<video src="{media_url}" class="feature-video" autoplay loop muted playsinline></video>'
            else:
                media_html = f'<img src="{media_url}" alt="{feat_title}" class="feature-image">'
        else:
            icon = feature.get('icon', '●')
            media_html = f'<div class="feature-icon">{icon}</div>'
        
        # Render bullets if present
        bullets_html = ''
        if bullet_count > 0:
            bullet_items = [f'<li>{translate(b, lang_data)}</li>' for b in feature.get('bullets', [])]
            bullets_html = f'<ul>{chr(10).join(bullet_items)}</ul>'
        
        desc_html = f'<p>{feat_desc}</p>' if feat_desc else ''
        
        items.append(f'''
        <div class="feature-card">
            {media_html}
            <h3>{feat_title}</h3>
            {desc_html}
            {bullets_html}
        </div>''')
    
    return f'''
    <section class="features-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            <div class="features-grid {grid_class}">
                {chr(10).join(items)}
            </div>
        </div>
    </section>'''

def render_feature_categories(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section['title'], lang_data)
    categories = []
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
    bg_style = f' style="background: {background};"' if background else ''
    
    for category in section.get('categories', []):
        cat_title = translate(category['title'], lang_data)
        features_list = []
        for feature in category.get('features', []):
            features_list.append(f'<li>{translate(feature, lang_data)}</li>')
        
        categories.append(f'''
        <div class="feature-category">
            <h3>{cat_title}</h3>
            <ul>
                {chr(10).join(features_list)}
            </ul>
        </div>''')
    
    return f'''
    <section class="feature-categories-section {bg_class}"{bg_style}>
        <div class="container">
            <h2>{title}</h2>
            <div class="categories-grid">
                {chr(10).join(categories)}
            </div>
        </div>
    </section>'''

def render_testimonials(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section.get('title', ''), lang_data)
    testimonials = []
    
    # Handle section background
    background = section.get('background', '')
    bg_class = 'section-has-background' if background else ''
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
                    <span class="stars">{stars_html}</span>
                    <span class="rating-text">{rating_text}</span>
                </div>
                {link_html}
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
        return render_feature_categories(section, lang_data)
    elif section_type == 'testimonials':
        return render_testimonials(section, lang_data)
    elif section_type == 'google_reviews':
        return render_google_reviews(section, lang_data)
    elif section_type == 'contact':
        return render_contact_form(section, lang_data, config, lang)
    
    return ""

def generate_page(page: Dict[str, Any], config: Dict[str, Any], lang: str, template: str) -> str:
    lang_data = load_json(f"translations/{lang}.json")
    base_url = config.get('base_url', '')
    
    sections_html = []
    for section in page.get('sections', []):
        sections_html.append(render_section(section, lang_data, config, lang))
    
    nav_html = render_nav(config, lang_data, page['slug'], lang)
    lang_switcher_html = render_lang_switcher(config, page['slug'])
    
    page_html = template.replace('{{TITLE}}', translate('site_title', lang_data))
    page_html = page_html.replace('{{LANG}}', lang)
    page_html = page_html.replace('{{BASE_URL}}', base_url)
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
