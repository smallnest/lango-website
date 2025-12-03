import os
import re

target_dir = "/Users/smallnest/ai_workplace/lango-website/repowiki/zh/_content"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find <cite>...</cite> blocks
    # We use DOTALL to match across lines
    pattern = re.compile(r'<cite>(.*?)</cite>', re.DOTALL)
    
    def replace_cite(match):
        inner_content = match.group(1)
        # Check if it looks like a list (lines starting with - or *)
        lines = inner_content.strip().split('\n')
        
        # If it's already HTML, we might not want to touch it, but the request implies 
        # it's probably markdown-like text inside or just plain text lines.
        # The example shows:
        # **本文档中引用的文件**
        # - [README.md](file://README.md)
        # ...
        
        # We want to convert this to:
        # <div class="cite-container">
        #   <p><strong>本文档中引用的文件</strong></p>
        #   <ul>
        #     <li><a href="...">...</a></li>
        #   </ul>
        # </div>
        # Or just keep it simple.
        
        # Let's parse the lines.
        new_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                
                # Remove the marker
                item_content = line[2:].strip()
                
                # Simple markdown link parser: [text](url) -> <a href="url">text</a>
                # Note: The existing content might already be HTML <a> tags if the markdown converter ran first?
                # Looking at the view_file output:
                # - [README.md](file://README.md)
                # It seems it is still markdown inside the cite tag? 
                # Or maybe the previous tool didn't convert inside cite?
                # Let's assume it might be markdown.
                
                # Regex for markdown link
                link_match = re.search(r'\[(.*?)\]\((.*?)\)', item_content)
                if link_match:
                    text = link_match.group(1)
                    url = link_match.group(2)
                    item_content = f'<a href="{url}">{text}</a>'
                
                new_lines.append(f'<li>{item_content}</li>')
            else:
                if in_list:
                    new_lines.append('</ul>')
                    in_list = False
                
                # Handle bold **text**
                bold_match = re.search(r'\*\*(.*?)\*\*', line)
                if bold_match:
                    line = line.replace(bold_match.group(0), f'<strong>{bold_match.group(1)}</strong>')
                
                new_lines.append(f'<p>{line}</p>')
        
        if in_list:
            new_lines.append('</ul>')
            
        return f'<div class="cite-content">\n' + '\n'.join(new_lines) + '\n</div>'

    new_content = pattern.sub(replace_cite, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Processed {filepath}")

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith(".html"):
            process_file(os.path.join(root, file))
