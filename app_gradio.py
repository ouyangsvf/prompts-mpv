"""
Prompt 优化器 - Gradio版
比Streamlit更轻量，Python 3.14兼容更好
"""

import json
import re
import gradio as gr
from typing import Dict, Any

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
            'code': ['code', 'program', 'function', 'debug', '代码', '编程'],
            'writing': ['write', 'article', 'story', '写作', '文章', '故事'],
            'analysis': ['analyze', 'research', '分析', '研究', '报告'],
            'creative': ['creative', 'idea', 'design', '创意', '设计']
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
        
        result_text = f"🎯 检测场景: {scene.upper()}\n\n"
        result_text += f"【压缩后】\n{compressed}\n\n"
        result_text += f"【最终输出】\n{shaped}\n\n"
        
        if structured:
            json_output = json.dumps(self.to_json(shaped), ensure_ascii=False, indent=2)
            result_text += f"【JSON格式】\n{json_output}"
        
        return result_text

# 初始化优化器
optimizer = PromptOptimizer()

# 创建Gradio界面
def optimize_prompt(prompt, structured):
    if not prompt:
        return "请输入Prompt"
    return optimizer.optimize(prompt, structured)

# 界面定义
with gr.Blocks(title="✨ Prompt 优化器") as demo:
    gr.Markdown("# ✨ Prompt 优化器")
    gr.Markdown("四层架构：语义压缩 → 结构重组 → 精准塑形 → 结构化输出")
    
    with gr.Row():
        with gr.Column():
            input_prompt = gr.Textbox(
                label="输入原始 Prompt",
                placeholder="例如：帮我写一个故事，关于程序员的冒险...",
                lines=5
            )
            structured_check = gr.Checkbox(
                label="输出JSON格式",
                value=False
            )
            optimize_btn = gr.Button("✨ 开始优化", variant="primary")
        
        with gr.Column():
            output_result = gr.Textbox(
                label="优化结果",
                lines=15,
                interactive=False
            )
    
    optimize_btn.click(
        fn=optimize_prompt,
        inputs=[input_prompt, structured_check],
        outputs=output_result
    )
    
    gr.Markdown("---")
    gr.Markdown("💡 支持场景自动检测：代码 / 写作 / 分析 / 创意")

if __name__ == "__main__":
    demo.launch()
