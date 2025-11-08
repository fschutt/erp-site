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
    phone = config['languages'][lang].get('phone', '')
    base_url = config.get('base_url', '')
    
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
    
    image_html = f'<img src="{image_url}" alt="{title}" class="hero-image"{size_attrs}>' if image_url else ''
    
    return f'''
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h1>{title}</h1>
                <p class="hero-subtitle">{subtitle}</p>
                <div class="cta-buttons">
                    <a href="{demo_url}" class="btn btn-primary">{translate("view_demo", lang_data)}</a>
                    <a href="tel:{phone}" class="btn btn-secondary">{translate("contact_sales", lang_data)}</a>
                </div>
            </div>
            {image_html}
        </div>
    </section>'''

def render_text_section(section: Dict[str, Any], lang_data: Dict[str, str], lang: str, config: Dict[str, Any]) -> str:
    title = translate(section['title'], lang_data)
    content = translate(section['content'], lang_data)
    layout = section.get('layout', 'text-only')
    base_url = config.get('base_url', '')
    
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
    <section class="text-section layout-image-left">
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
    <section class="text-section layout-image-right">
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
    <section class="text-section">
        <div class="container">
            <h2>{title}</h2>
            <div class="prose">{content}</div>
            {f'<div class="section-image">{image_html}</div>' if image_html else ''}
        </div>
    </section>'''

def render_features_grid(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section['title'], lang_data)
    items = []
    
    for feature in section.get('items', []):
        feat_title = translate(feature['title'], lang_data)
        feat_desc = translate(feature['description'], lang_data)
        icon = feature.get('icon', '●')
        items.append(f'''
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{feat_title}</h3>
            <p>{feat_desc}</p>
        </div>''')
    
    return f'''
    <section class="features-section">
        <div class="container">
            <h2>{title}</h2>
            <div class="features-grid">
                {chr(10).join(items)}
            </div>
        </div>
    </section>'''

def render_feature_categories(section: Dict[str, Any], lang_data: Dict[str, str]) -> str:
    title = translate(section['title'], lang_data)
    categories = []
    
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
    <section class="feature-categories-section">
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
    <section class="testimonials-section">
        <div class="container">
            {title_html}
            <div class="testimonials-grid">
                {chr(10).join(testimonials)}
            </div>
        </div>
    </section>'''

def render_contact_form(section: Dict[str, Any], lang_data: Dict[str, str], config: Dict[str, Any], lang: str) -> str:
    title = translate(section['title'], lang_data)
    subtitle = translate(section.get('subtitle', ''), lang_data)
    phone = config['languages'][lang].get('phone', '')
    email = config.get('contact_email', '')
    
    subtitle_html = f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''
    
    return f'''
    <section class="contact-section">
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
        return render_features_grid(section, lang_data)
    elif section_type == 'feature_categories':
        return render_feature_categories(section, lang_data)
    elif section_type == 'testimonials':
        return render_testimonials(section, lang_data)
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
