"""
Prompt 优化器 MVP
四层架构：语义压缩 → 结构重组 → 精准塑形 → 结构化输出
"""

import streamlit as st
import json
import re
from typing import Dict, Any, Optional

# ===== 配置页面 =====
st.set_page_config(
    page_title="Prompt 优化器",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Prompt 优化器")
st.markdown("四层架构：语义压缩 → 结构重组 → 精准塑形 → 结构化输出")

# ===== 侧边栏配置 =====
with st.sidebar:
    st.header("⚙️ 配置")
    
    # API配置
    api_key = st.text_input("OpenAI API Key", type="password", 
                           value=st.session_state.get('api_key', ''))
    if api_key:
        st.session_state['api_key'] = api_key
    
    model = st.selectbox("模型", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], 
                        index=0)
    
    st.divider()
    
    # 优化选项
    enable_layer4 = st.toggle("启用结构化输出", value=False,
                             help="输出JSON Schema格式")
    
    show_intermediate = st.toggle("显示中间层", value=True,
                                  help="展示每层优化结果")

# ===== 核心优化类 =====

class SemanticCompressionLayer:
    """第一层：语义压缩 - 去除冗余"""
    
    def compress(self, prompt: str) -> str:
        # 去除多余空格和换行
        compressed = re.sub(r'\n+', '\n', prompt.strip())
        compressed = re.sub(r' +', ' ', compressed)
        
        # 去除常见的冗余前缀
        redundant_patterns = [
            r'^please\s+', r'^请\s+', 
            r'^i want you to\s+', r'^我想让你\s+',
            r'^can you\s+', r'^你能\s+',
            r'^would you\s+', r'^你愿意\s+'
        ]
        for pattern in redundant_patterns:
            compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)
        
        return compressed.strip()

class StructureReorganizationLayer:
    """第二层：结构重组 - 优化信息层级"""
    
    def reorganize(self, prompt: str) -> str:
        lines = prompt.split('\n')
        organized_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测并标记关键部分
            if any(kw in line.lower() for kw in ['role', '角色', 'act as', '作为']):
                line = f"【角色】{line}"
            elif any(kw in line.lower() for kw in ['task', '任务', 'you will', '你需要']):
                line = f"【任务】{line}"
            elif any(kw in line.lower() for kw in ['rule', '规则', 'constraint', '约束']):
                line = f"【规则】{line}"
            elif any(kw in line.lower() for kw in ['output', '输出', 'format', '格式']):
                line = f"【输出】{line}"
            
            organized_lines.append(line)
        
        return '\n'.join(organized_lines)

class PrecisionShapingLayer:
    """第三层：精准塑形 - 针对场景微调"""
    
    def __init__(self):
        self.templates = {
            'code': {
                'prefix': '你是一位资深开发者。',
                'suffix': '只输出代码，不解释。',
                'keywords': ['code', 'program', 'function', 'class', 'debug', '代码', '编程']
            },
            'writing': {
                'prefix': '你是一位专业写作者。',
                'suffix': '保持语言流畅，逻辑清晰。',
                'keywords': ['write', 'essay', 'article', 'story', '写作', '文章', '故事']
            },
            'analysis': {
                'prefix': '你是一位分析专家。',
                'suffix': '提供结构化分析，列出关键点。',
                'keywords': ['analyze', 'analysis', 'research', '分析', '研究']
            },
            'creative': {
                'prefix': '你是一位创意专家。',
                'suffix': '大胆创新，突破常规思维。',
                'keywords': ['creative', 'idea', 'design', '创意', '设计', '想法']
            }
        }
    
    def detect_scene(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        scores = {}
        
        for scene, config in self.templates.items():
            score = sum(1 for kw in config['keywords'] if kw in prompt_lower)
            scores[scene] = score
        
        best_scene = max(scores, key=scores.get)
        return best_scene if scores[best_scene] > 0 else 'general'
    
    def shape(self, prompt: str, scene: str = None) -> str:
        if not scene:
            scene = self.detect_scene(prompt)
        
        if scene == 'general':
            return prompt
        
        template = self.templates[scene]
        shaped = f"{template['prefix']}\n\n{prompt}\n\n{template['suffix']}"
        
        return shaped

class StructuredOutputLayer:
    """第四层：结构化输出 - JSON Schema格式"""
    
    def __init__(self):
        self.structured_keywords = [
            'json', '结构化', 'structured', 'api', 'schema',
            '格式', 'format', '模板', 'template'
        ]
    
    def detect_structured_intent(self, user_input: str) -> bool:
        input_lower = user_input.lower()
        return any(kw in input_lower for kw in self.structured_keywords)
    
    def extract_variables(self, prompt: str) -> Dict[str, Any]:
        variables = {}
        
        # 匹配 ${Name:default} 格式
        pattern1 = r'\$\{(\w+):([^}]*)\}'
        matches1 = re.findall(pattern1, prompt)
        for name, default in matches1:
            variables[name] = {
                'type': 'string',
                'default': default.strip(),
                'description': f'{name} 参数'
            }
        
        # 匹配 {{variable}} 格式
        pattern2 = r'\{\{(\w+)\}\}'
        matches2 = re.findall(pattern2, prompt)
        for name in matches2:
            if name not in variables:
                variables[name] = {
                    'type': 'string',
                    'description': f'{name} 参数'
                }
        
        return variables
    
    def infer_output_schema(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ['code', 'review', '代码', '审查']):
            return {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "category": {"type": "string"},
                    "suggestion": {"type": "string"},
                    "code_example": {"type": "string"}
                }
            }
        
        if any(kw in prompt_lower for kw in ['data', 'transform', '数据']):
            return {
                "type": "object",
                "properties": {
                    "result": {"type": "object"},
                    "summary": {"type": "string"}
                }
            }
        
        if any(kw in prompt_lower for kw in ['story', 'content', '故事', '内容']):
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "status": {"type": "string", "enum": ["success", "error"]}
            }
        }
    
    def wrap_structured(self, prompt: str) -> Dict[str, Any]:
        variables = self.extract_variables(prompt)
        output_schema = self.infer_output_schema(prompt)
        
        structured = {
            "role": "AI Assistant",
            "parameters": variables if variables else {"input": {"type": "string"}},
            "output_format": output_schema,
            "instructions": prompt
        }
        
        return structured

class PromptOptimizer:
    """Prompt 优化器主类"""
    
    def __init__(self):
        self.layer1 = SemanticCompressionLayer()
        self.layer2 = StructureReorganizationLayer()
        self.layer3 = PrecisionShapingLayer()
        self.layer4 = StructuredOutputLayer()
    
    def optimize(self, prompt: str, enable_structured: bool = False) -> Dict[str, Any]:
        result = {
            "original": prompt,
            "layers": {}
        }
        
        # 第一层：语义压缩
        compressed = self.layer1.compress(prompt)
        result["layers"]["layer1_semantic_compression"] = compressed
        
        # 第二层：结构重组
        restructured = self.layer2.reorganize(compressed)
        result["layers"]["layer2_structure_reorganization"] = restructured
        
        # 第三层：精准塑形
        scene = self.layer3.detect_scene(prompt)
        shaped = self.layer3.shape(restructured, scene)
        result["layers"]["layer3_precision_shaping"] = shaped
        result["scene_detected"] = scene
        
        # 第四层：结构化输出
        if enable_structured or self.layer4.detect_structured_intent(prompt):
            structured = self.layer4.wrap_structured(shaped)
            result["layers"]["layer4_structured_output"] = structured
            result["final_output"] = json.dumps(structured, ensure_ascii=False, indent=2)
            result["output_format"] = "structured"
        else:
            result["final_output"] = shaped
            result["output_format"] = "text"
        
        return result

# ===== Streamlit UI =====

optimizer = PromptOptimizer()

# 输入区
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 输入原始 Prompt")
    input_prompt = st.text_area(
        "粘贴你的 Prompt",
        height=200,
        placeholder="例如：帮我写一个故事，关于一个程序员的冒险...",
        key="input_prompt"
    )

with col2:
    st.subheader("📊 统计")
    if input_prompt:
        st.metric("字符数", len(input_prompt))
        st.metric("词数", len(input_prompt.split()))
        st.metric("行数", len(input_prompt.split('\n')))

# 优化按钮
if st.button("✨ 开始优化", type="primary", use_container_width=True):
    if not input_prompt:
        st.error("请输入 Prompt")
    else:
        with st.spinner("优化中..."):
            result = optimizer.optimize(input_prompt, enable_layer4)
        
        st.success("优化完成！")
        
        # 显示检测结果
        st.info(f"🎯 检测场景：**{result['scene_detected'].upper()}**")
        
        # 中间层展示
        if show_intermediate:
            with st.expander("🔍 查看每层优化过程", expanded=True):
                tabs = st.tabs(["原始", "压缩", "重组", "塑形", "最终"])
                
                with tabs[0]:
                    st.code(result['original'], language='text')
                
                with tabs[1]:
                    st.code(result['layers']['layer1_semantic_compression'], language='text')
                
                with tabs[2]:
                    st.code(result['layers']['layer2_structure_reorganization'], language='text')
                
                with tabs[3]:
                    st.code(result['layers']['layer3_precision_shaping'], language='text')
                
                with tabs[4]:
                    if result['output_format'] == 'structured':
                        st.json(result['layers']['layer4_structured_output'])
                    else:
                        st.code(result['final_output'], language='text')
        
        # 最终输出
        st.subheader("🎉 优化结果")
        
        if result['output_format'] == 'structured':
            st.json(result['layers']['layer4_structured_output'])
        else:
            st.code(result['final_output'], language='text')
        
        # 复制按钮
        st.download_button(
            "📋 复制结果",
            result['final_output'],
            file_name="optimized_prompt.txt",
            mime="text/plain"
        )

# 底部提示
st.divider()
st.markdown("""
💡 **使用提示**：
- 输入越详细，优化效果越好
- 启用「结构化输出」可获得 JSON Schema 格式
- 支持代码、写作、分析、创意等场景自动检测
""")
