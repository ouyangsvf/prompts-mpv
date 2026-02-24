#!/usr/bin/env python3
"""
Prompt 优化器 - 命令行版
无需streamlit，直接运行
"""

import json
import re
import sys

class PromptOptimizer:
    """完整四层优化器"""
    
    def __init__(self):
        self.templates = {
            'code': ('你是一位资深开发者。', '只输出代码，不解释。'),
            'writing': ('你是一位专业写作者。', '保持语言流畅，逻辑清晰。'),
            'analysis': ('你是一位分析专家。', '提供结构化分析，列出关键点。'),
            'creative': ('你是一位创意专家。', '大胆创新，突破常规思维。'),
            'general': ('', '')
        }
    
    def detect_scene(self, prompt):
        prompt_lower = prompt.lower()
        keywords = {
            'code': ['code', 'program', 'function', 'class', 'debug', '代码', '编程', '算法'],
            'writing': ['write', 'essay', 'article', 'story', '写作', '文章', '故事', '文案'],
            'analysis': ['analyze', 'analysis', 'research', '分析', '研究', '报告', '评估'],
            'creative': ['creative', 'idea', 'design', '创意', '设计', '想法', '策划']
        }
        scores = {scene: sum(1 for kw in words if kw in prompt_lower) 
                  for scene, words in keywords.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 'general'
    
    def compress(self, prompt):
        compressed = re.sub(r'\n+', '\n', prompt.strip())
        compressed = re.sub(r' +', ' ', compressed)
        return compressed
    
    def shape(self, prompt, scene):
        prefix, suffix = self.templates.get(scene, ('', ''))
        if prefix:
            return f"{prefix}\n\n{prompt}\n\n{suffix}"
        return prompt
    
    def to_json(self, prompt):
        return {
            "role": "AI Assistant",
            "parameters": {"input": {"type": "string"}},
            "output_format": {"type": "object", "properties": {"result": {"type": "string"}}},
            "instructions": prompt
        }
    
    def optimize(self, prompt, structured=False):
        scene = self.detect_scene(prompt)
        compressed = self.compress(prompt)
        shaped = self.shape(compressed, scene)
        
        result = {
            "场景": scene.upper(),
            "压缩后": compressed,
            "最终输出": shaped
        }
        
        if structured:
            result["JSON格式"] = self.to_json(shaped)
        
        return result

def main():
    optimizer = PromptOptimizer()
    
    print("=" * 60)
    print("✨ Prompt 优化器 (命令行版)")
    print("=" * 60)
    print()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
        structured = '--json' in user_input
        if structured:
            user_input = user_input.replace('--json', '').strip()
    else:
        user_input = input("📝 输入Prompt: ")
        json_choice = input("📦 输出JSON格式? (y/n): ").lower()
        structured = json_choice == 'y'
    
    print()
    print("⏳ 优化中...")
    print()
    
    result = optimizer.optimize(user_input, structured)
    
    print(f"🎯 检测场景: {result['场景']}")
    print()
    print("=" * 60)
    print("✅ 优化结果:")
    print("=" * 60)
    print(result['最终输出'])
    
    if structured:
        print()
        print("=" * 60)
        print("📦 JSON格式:")
        print("=" * 60)
        print(json.dumps(result['JSON格式'], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
