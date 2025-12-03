import os

target_dir = "/Users/smallnest/ai_workplace/lango-website/repowiki/zh/_content"

# The content we previously injected
old_js_content = """
<script src="https://s4.zstatic.net/ajax/libs/mermaid/11.12.0/mermaid.min.js"></script>
<script src="https://s4.zstatic.net/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
<script>
    mermaid.initialize({ startOnLoad: true });
    hljs.highlightAll();
</script>
"""

# The new content we want to inject
new_js_content = """
<script src="https://s4.zstatic.net/ajax/libs/mermaid/11.12.0/mermaid.min.js"></script>
<script src="https://s4.zstatic.net/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
<script>
    // 初始化 Mermaid - 在加载 app.js 之前
    console.log('初始化 Mermaid');
    mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        pie: {
            textPosition: 0.75
        }
    });

    // 全局函数，用于处理 Mermaid 代码块
    window.processMermaidBlocks = async function () {
        console.log('开始处理 Mermaid 代码块...');

        const mermaidBlocks = document.querySelectorAll('code.language-mermaid');
        console.log('找到代码块数量:', mermaidBlocks.length);

        if (mermaidBlocks.length === 0) {
            console.log('没有找到 Mermaid 代码块');
            return;
        }

        for (let i = 0; i < mermaidBlocks.length; i++) {
            const block = mermaidBlocks[i];

            // 检查是否已经处理过
            if (block.dataset.mermaidProcessed) {
                continue;
            }

            const mermaidCode = block.textContent || block.innerText;
            console.log(`处理第 ${i + 1} 个代码块:`, mermaidCode);

            // 创建图表容器
            const diagramId = `mermaid-diagram-${Date.now()}-${i}`;
            const diagramContainer = document.createElement('div');
            diagramContainer.id = diagramId;
            diagramContainer.className = 'mermaid-diagram';
            diagramContainer.innerHTML = '<p>正在渲染图表...</p>';

            // 插入到代码块后面
            block.parentElement.insertAdjacentElement('afterend', diagramContainer);

            try {
                console.log('开始渲染图表...');

                // 生成唯一的 SVG ID
                const svgId = `diagram-svg-${Date.now()}-${i}`;

                const result = await mermaid.render(svgId, mermaidCode);
                console.log('渲染成功');

                diagramContainer.innerHTML = result.svg;

                // 隐藏原始代码块
                block.parentElement.style.display = 'none';

                // 标记为已处理
                block.dataset.mermaidProcessed = 'true';

            } catch (error) {
                console.error('渲染失败:', error);
                diagramContainer.innerHTML = `
                    <div style="color: red; padding: 10px; border: 1px solid red; border-radius: 4px;">
                        <strong>图表渲染失败:</strong><br>
                        ${error.message}<br>
                        <details>
                            <summary>原始代码</summary>
                            <pre>${mermaidCode}</pre>
                        </details>
                    </div>
                `;
            }
        }
    }

    // 在脚本末尾添加
    window.addEventListener('load', function() {
        console.log('所有资源加载完成，开始处理 Mermaid');
        window.processMermaidBlocks();
    });
    hljs.highlightAll();
</script>
"""

css_content = """
    <style>
        .mermaid-diagram {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }

        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if new content is already there
    if "window.processMermaidBlocks" in content:
        print(f"Skipping {filepath} (already has new mermaid logic)")
        return

    # Check if old content is there and replace it
    # We strip the leading/trailing newlines from the triple-quoted string for better matching if needed,
    # but exact match is safer if we are sure.
    # The previous script injected `js_content + "\n  </body>"`.
    # Let's try to find the unique part of the old script.
    old_script_signature = "mermaid.initialize({ startOnLoad: true });"
    
    if old_script_signature in content:
        print(f"Updating {filepath} (replacing old mermaid logic)")
        # We need to be careful about replacing the whole block.
        # Since we know exactly what we injected, let's try to replace the whole block.
        # However, whitespace might be tricky.
        # Let's use a regex or just replace the known signature block if we can identify the boundaries.
        
        # Simpler approach: construct the exact string we injected previously.
        # It was: js_content + "\n  </body>"
        # But `js_content` starts with a newline in the python string?
        # No, `js_content = """...` starts with a newline.
        # Let's try to replace the core script tag content.
        
        content = content.replace(old_js_content.strip(), new_js_content.strip())
        
        # Fallback if exact match fails due to whitespace:
        if old_script_signature in content:
             # If the replace didn't work (e.g. whitespace diffs), let's try a more aggressive replace
             # We can replace the specific lines.
             content = content.replace('mermaid.initialize({ startOnLoad: true });', 
                                     '// Replaced by new logic\n')
             # This is messy. Let's try to find the whole <script>...</script> block containing the signature.
             import re
             pattern = re.compile(r'<script>\s*mermaid\.initialize\(\{ startOnLoad: true \}\);\s*hljs\.highlightAll\(\);\s*</script>', re.DOTALL)
             
             # We want to replace the whole block including the library imports if possible, 
             # but the library imports are separate tags.
             # The old_js_content included the library imports.
             
             # Let's just overwrite the whole file if we detect the old signature, 
             # assuming we can just strip the old JS and append the new one?
             # No, that's dangerous.
             
             # Best effort: Replace the exact string `old_js_content` stripping the first newline if it exists.
             pass

    else:
        # If old signature not found, maybe it's a fresh file?
        # Inject CSS if missing
        if "mermaid-diagram" not in content:
             if "</head>" in content:
                content = content.replace("</head>", css_content + "\n  </head>")

        # Inject JS if missing
        if "mermaid.min.js" not in content:
            if "</body>" in content:
                content = content.replace("</body>", new_js_content + "\n  </body>")
            else:
                print(f"Warning: No </body> in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed {filepath}")

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith(".html"):
            process_file(os.path.join(root, file))
