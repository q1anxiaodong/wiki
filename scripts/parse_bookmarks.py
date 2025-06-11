from bs4 import BeautifulSoup
import sys
import os
import re
from urllib.parse import urlparse, unquote

def normalize_url(url):
    """标准化URL以便比较"""
    # 解析URL
    parsed = urlparse(unquote(url))
    # 移除末尾的斜杠
    path = parsed.path.rstrip('/')
    # 重建URL，忽略某些参数
    return f"{parsed.scheme}://{parsed.netloc}{path}"

def categorize_url(url, title):
    """根据URL和标题对书签进行分类"""
    categories = {
        "前端开发": {
            "keywords": ["vue", "react", "typescript", "javascript", "css", "html", "webpack", "element", "ant design", 
                        "layui", "echarts", "d3", "three.js", "flex", "ui", "前端", "vant", "zrender", "canvas"],
            "subcategories": {
                "框架与库": ["vue", "react", "angular", "typescript", "javascript", "webpack"],
                "UI组件库": ["element", "ant", "layui", "vant", "ui"],
                "可视化": ["echarts", "d3", "three.js", "visualization", "可视化", "zrender", "canvas"],
                "CSS与设计": ["css", "flex", "design", "color", "动画", "animation"]
            }
        },
        "学习资源": {
            "keywords": ["教程", "tutorial", "course", "learn", "ruanyifeng", "study", "菜鸟教程", "入门", "文档"],
            "subcategories": {
                "教程文档": ["tutorial", "教程", "文档", "手册", "指南"],
                "在线课程": ["course", "课程", "learn", "training"],
                "技术博客": ["blog", "博客", "ruanyifeng", "阮一峰"],
                "面试资料": ["面试", "interview"]
            }
        },
        "AI与机器学习": {
            "keywords": ["ai", "chatgpt", "claude", "hugging face", "machine learning", "深度学习", "机器学习"],
            "subcategories": {
                "AI工具": ["chatgpt", "claude", "ai工具"],
                "AI学习资源": ["machine learning", "深度学习", "机器学习", "hugging face"],
                "AI导航与搜索": ["ai导航", "ai搜索"]
            }
        },
        "开发工具": {
            "keywords": ["github", "git", "draw.io", "processon", "mdn", "api", "tool", "工具"],
            "subcategories": {
                "在线工具": ["draw.io", "processon", "tool", "工具"],
                "开发文档": ["mdn", "api", "doc", "文档"],
                "代码托管": ["github", "git"],
                "效率工具": ["converter", "转换", "翻译", "工具"]
            }
        },
        "算法与数据结构": {
            "keywords": ["algorithm", "leetcode", "算法", "数据结构", "sorting"],
            "subcategories": {
                "算法可视化": ["visualization", "可视化"],
                "刷题平台": ["leetcode", "算法题"],
                "算法教程": ["algorithm", "算法教程"]
            }
        },
        "技术社区": {
            "keywords": ["v2ex", "weekly", "社区", "forum", "community"],
            "subcategories": {
                "技术论坛": ["v2ex", "forum", "社区"],
                "技术周刊": ["weekly", "周刊"],
                "开源社区": ["open source", "开源"]
            }
        },
        "职业发展": {
            "keywords": ["job", "职业", "远程", "remote", "职级", "规划", "路线"],
            "subcategories": {
                "远程工作": ["remote", "远程"],
                "职业规划": ["职级", "规划"],
                "技术路线": ["路线", "规划", "学习路线"]
            }
        },
        "其他资源": {
            "keywords": ["other", "工具", "tool", "娱乐", "文学"],
            "subcategories": {
                "文学艺术": ["文学", "艺术", "诗", "音乐"],
                "娱乐工具": ["game", "游戏", "娱乐"],
                "实用工具": ["工具", "tool", "实用"]
            }
        }
    }
    
    # 将URL和标题转换为小写以进行匹配
    url_lower = url.lower()
    title_lower = title.lower()
    
    # 首先尝试进行子分类匹配
    for main_category, data in categories.items():
        for subcategory_name, subcategory_keywords in data["subcategories"].items():
            for keyword in subcategory_keywords:
                if keyword.lower() in url_lower or keyword.lower() in title_lower:
                    return main_category, subcategory_name
    
    # 如果没有匹配到子分类，尝试主分类匹配
    for category, data in categories.items():
        for keyword in data["keywords"]:
            if keyword.lower() in url_lower or keyword.lower() in title_lower:
                return category, "其他"
    
    return "其他资源", "未分类"

def parse_bookmarks(html_file):
    """解析 Chrome 书签 HTML 文件并生成 Markdown 格式"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"读取到的文件大小: {len(content)} 字节")
        soup = BeautifulSoup(content, 'html.parser')
    
    # 用于存储分类后的书签
    categorized_bookmarks = {}
    # 用于检测重复URL
    seen_urls = set()
    
    def process_bookmark(a_tag):
        href = a_tag.get('href', '')
        text = a_tag.text.strip()
        if href and text:
            # 标准化URL
            normalized_url = normalize_url(href)
            # 检查是否是重复的URL
            if normalized_url in seen_urls:
                print(f"跳过重复链接: {text}")
                return
            
            seen_urls.add(normalized_url)
            main_category, subcategory = categorize_url(href, text)
            if main_category not in categorized_bookmarks:
                categorized_bookmarks[main_category] = {}
            if subcategory not in categorized_bookmarks[main_category]:
                categorized_bookmarks[main_category][subcategory] = []
            categorized_bookmarks[main_category][subcategory].append((text, href))
            print(f"添加书签: {text} -> {main_category}/{subcategory}")
    
    # 处理所有书签链接
    for a_tag in soup.find_all('a'):
        process_bookmark(a_tag)
    
    # 生成Markdown内容
    markdown_lines = []
    
    # 添加主分类
    for main_category in sorted(categorized_bookmarks.keys()):
        markdown_lines.append(f"\n## {main_category}\n")
        
        # 添加子分类
        for subcategory in sorted(categorized_bookmarks[main_category].keys()):
            if subcategory != "其他":
                markdown_lines.append(f"\n### {subcategory}\n")
                
                # 添加书签
                for title, url in sorted(categorized_bookmarks[main_category][subcategory]):
                    markdown_lines.append(f"- [{title}]({url})")
        
        # 添加未分类的书签
        if "其他" in categorized_bookmarks[main_category]:
            markdown_lines.append("\n### 其他\n")
            for title, url in sorted(categorized_bookmarks[main_category]["其他"]):
                markdown_lines.append(f"- [{title}]({url})")
    
    return '\n'.join(markdown_lines)

def main():
    if len(sys.argv) != 2:
        print("使用方法: python parse_bookmarks.py <书签文件路径>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    if not os.path.exists(html_file):
        print(f"错误: 文件 {html_file} 不存在")
        sys.exit(1)
    
    print(f"开始处理书签文件: {html_file}")
    markdown_content = parse_bookmarks(html_file)
    
    # 创建输出文件
    output_file = 'docs/my_bookmarks.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("""---
title: 我的书签
description: 从 Chrome 导入的书签
---

# 我的书签收藏

以下是从 Chrome 浏览器导入的书签，按照主题进行分类整理：

""")
        f.write(markdown_content)
    
    print(f"书签已成功转换并保存到 {output_file}")

if __name__ == '__main__':
    main() 