import os
from bs4 import BeautifulSoup

target_dir = "/Users/smallnest/ai_workplace/lango-website/repowiki/zh/_content"

ORDER_LIST = [
    "项目概述",
    "快速入门",
    "贡献指南",
    "架构与设计",
    "教程与示例",
    "核心概念",
    "预构建组件",
    "检查点存储",
    "工具集成",
    "高级特性",
    "API 参考"
]

def get_group_name(group):
    if not group:
        return ""
    first_tag = group[0]
    return first_tag.get_text(strip=True)

def get_sort_index(name):
    try:
        return ORDER_LIST.index(name)
    except ValueError:
        return 999

def get_groups(ul):
    groups = []
    tags = ul.find_all(recursive=False)
    skip_next = False
    
    for i, tag in enumerate(tags):
        if skip_next:
            skip_next = False
            continue
            
        if tag.name == 'li':
            classes = tag.get('class', [])
            if 'heading' in classes:
                # Submenu group start
                group = [tag]
                # Check if next element is a UL
                if i + 1 < len(tags) and tags[i+1].name == 'ul':
                    group.append(tags[i+1])
                    skip_next = True
                groups.append(group)
            else:
                # Leaf item
                groups.append([tag])
        elif tag.name == 'ul':
            # Orphaned UL? Treat as its own group (branch)
            groups.append([tag])
        else:
            # Comments or other tags
            groups.append([tag])
    return groups

def is_branch(group):
    # A group is a branch if it contains a ul
    for tag in group:
        if tag.name == 'ul':
            return True
    return False

def reorder_ul(ul, level=0):
    groups = get_groups(ul)
    
    # Recursively reorder sub-ULs first
    for group in groups:
        for tag in group:
            if tag.name == 'ul':
                reorder_ul(tag, level + 1)

    # Sort current level
    if level == 0:
        # Top level: use ORDER_LIST
        groups.sort(key=lambda g: get_sort_index(get_group_name(g)))
    else:
        # Submenus: Leaves first, then branches
        leaves = [g for g in groups if not is_branch(g)]
        branches = [g for g in groups if is_branch(g)]
        
        # We keep the original relative order within leaves and branches
        # unless we want to sort them alphabetically? 
        # The user request only said "no submenus items placed at top".
        # So stable sort is best.
        
        groups = leaves + branches

    # Rebuild UL
    ul.clear()
    for group in groups:
        for tag in group:
            ul.append(tag)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    menu_nav = soup.find('nav', id='menu')
    if not menu_nav:
        return

    main_ul = menu_nav.find('ul', recursive=False)
    if not main_ul:
        main_ul = menu_nav.find('ul')
        
    if not main_ul:
        return

    reorder_ul(main_ul, level=0)
            
    output_html = str(soup)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output_html)
    print(f"Processed {filepath}")

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith(".html"):
            process_file(os.path.join(root, file))
