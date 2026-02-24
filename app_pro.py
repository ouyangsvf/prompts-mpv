"""
Prompt 优化器 Pro - 商业化版本
四层架构 + 盈利功能
"""

import streamlit as st
import json
import re
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

# ===== 页面配置 =====
st.set_page_config(
    page_title="Prompt 优化器 Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 用户配额系统 =====
class QuotaManager:
    """免费/付费用户配额管理"""
    
    def __init__(self):
        self.tiers = {
            'free': {'daily_limit': 10, 'features': ['basic']},
            'pro': {'daily_limit': 9999, 'features': ['basic', 'structured', 'history', 'api']},
            'team': {'daily_limit': 99999, 'features': ['basic', 'structured', 'history', 'api', 'monitor']}
        }
    
    def get_user_tier(self) -> str:
        """获取用户等级（简化版，后期可接数据库）"""
        # 从 session 或 query param 获取
        tier = st.query_params.get('tier', 'free')
        return tier if tier in self.tiers else 'free'
    
    def check_quota(self, tier: str, usage_count: int) -> bool:
        """检查是否超出配额"""
        return usage_count < self.tiers[tier]['daily_limit']
    
    def get_remaining(self, tier: str, usage_count: int) -> int:
        """获取剩余次数"""
        return max(0, self.tiers[tier]['daily_limit'] - usage_count)

# ===== 侧边栏 - 用户系统 =====
quota_mgr = QuotaManager()

with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=80)
    st.title("Prompt 优化器 Pro")
    
    # 用户等级显示
    user_tier = quota_mgr.get_user_tier()
    tier_colors = {'free': '🔵', 'pro': '🟡', 'team': '🟣'}
    st.markdown(f"### {tier_colors.get(user_tier, '🔵')} {user_tier.upper()} 版")
    
    # 初始化使用计数
    if 'usage_count' not in st.session_state:
        st.session_state.usage_count = 0
    
    remaining = quota_mgr.get_remaining(user_tier, st.session_state.usage_count)
    st.progress(remaining / quota_mgr.tiers[user_tier]['daily_limit'], 
                text=f"今日剩余: {remaining} 次")
    
    if user_tier == 'free' and remaining < 3:
        st.warning("⚠️ 免费次数即将用完")
        if st.button("💎 升级到 Pro - ¥29/月", type="primary", use_container_width=True):
            st.markdown("[点击支付](https://your-payment-link.com)", unsafe_allow_html=True)
    
    st.divider()
    
    # API 配置
    st.header("⚙️ 配置")
    api_key = st.text_input("OpenAI API Key", type="password", 
                           value=st.session_state.get('api_key', ''),
                           help="您的 API Key 仅保存在本地浏览器")
    if api_key:
        st.session_state['api_key'] = api_key
    
    # Pro 功能
    if user_tier in ['pro', 'team']:
        model = st.selectbox("模型", 
                           ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3-haiku"], 
                           index=0)
        enable_layer4 = st.toggle("结构化输出", value=True)
        save_history = st.toggle("保存历史", value=True)
    else:
        model = "gpt-4o-mini"
        enable_layer4 = st.checkbox("结构化输出 (Pro功能)", value=False, disabled=True)
        if enable_layer4:
            st.info("💎 升级到 Pro 解锁结构化输出")
        save_history = False
    
    st.divider()
    
    # 监控功能（Team 版）
    if user_tier == 'team':
        st.header("📊 监控")
        if st.button("🔍 监控网页变化", use_container_width=True):
            st.switch_page("monitor")
    
    # 使用统计
    st.caption(f"今日使用: {st.session_state.usage_count} 次")
    st.caption(f"上次优化: {st.session_state.get('last_optimized', '无')}")

# ===== 核心优化类（保持原有逻辑，增强） =====

class SemanticCompressionLayer:
    """第一层：语义压缩 - 去除冗余"""
    
    def compress(self, prompt: str) -> str:
        compressed = re.sub(r'\n+', '\n', prompt.strip())
        compressed = re.sub(r' +', ' ', compressed)
        
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
                'prefix': '你是一位资深开发者，精通多种编程语言。',
                'suffix': '只输出代码，不解释。确保代码可运行、无bug。',
                'keywords': ['code', 'program', 'function', 'class', 'debug', '代码', '编程', '程序']
            },
            'writing': {
                'prefix': '你是一位专业写作者，文笔优美，逻辑清晰。',
                'suffix': '保持语言流畅，结构完整，引人入胜。',
                'keywords': ['write', 'essay', 'article', 'story', '写作', '文章', '故事', '文案']
            },
            'analysis': {
                'prefix': '你是一位分析专家，善于深度思考和逻辑推理。',
                'suffix': '提供结构化分析，列出关键点和数据支撑。',
                'keywords': ['analyze', 'analysis', 'research', '分析', '研究', '报告']
            },
            'creative': {
                'prefix': '你是一位创意专家，思维活跃，见解独到。',
                'suffix': '大胆创新，突破常规思维，提供独特视角。',
                'keywords': ['creative', 'idea', 'design', '创意', '设计', '想法', '灵感']
            },
            'business': {
                'prefix': '你是一位商业顾问，熟悉市场和商业逻辑。',
                'suffix': '注重可行性，提供可落地的建议和ROI分析。',
                'keywords': ['business', 'market', 'strategy', '商业', '市场', '策略', '盈利']
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
            return f"你是一位专业助手。\n\n{prompt}\n\n请给出高质量的回答。"
        
        template = self.templates[scene]
        return f"{template['prefix']}\n\n{prompt}\n\n{template['suffix']}"

class StructuredOutputLayer:
    """第四层：结构化输出 - JSON Schema格式"""
    
    def detect_structured_intent(self, user_input: str) -> bool:
        keywords = ['json', '结构化', 'structured', 'api', 'schema', '格式', 'format', '模板', 'template']
        return any(kw in user_input.lower() for kw in keywords)
    
    def wrap_structured(self, prompt: str) -> Dict[str, Any]:
        return {
            "role": "AI Assistant",
            "instructions": prompt,
            "output_format": {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "confidence": {"type": "number"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }

class PromptOptimizer:
    """Prompt 优化器主类"""
    
    def __init__(self):
        self.layer1 = SemanticCompressionLayer()
        self.layer2 = StructureReorganizationLayer()
        self.layer3 = PrecisionShapingLayer()
        self.layer4 = StructuredOutputLayer()
    
    def optimize(self, prompt: str, enable_structured: bool = False) -> Dict[str, Any]:
        result = {"original": prompt, "layers": {}}
        
        # 四层处理
        compressed = self.layer1.compress(prompt)
        result["layers"]["layer1"] = compressed
        
        restructured = self.layer2.reorganize(compressed)
        result["layers"]["layer2"] = restructured
        
        scene = self.layer3.detect_scene(prompt)
        shaped = self.layer3.shape(restructured, scene)
        result["layers"]["layer3"] = shaped
        result["scene"] = scene
        
        if enable_structured:
            structured = self.layer4.wrap_structured(shaped)
            result["layers"]["layer4"] = structured
            result["final"] = json.dumps(structured, ensure_ascii=False, indent=2)
            result["format"] = "structured"
        else:
            result["final"] = shaped
            result["format"] = "text"
        
        return result

# ===== 主界面 =====
optimizer = PromptOptimizer()

st.markdown("## 🚀 让 AI 更懂你")
st.caption("四层智能优化：语义压缩 → 结构重组 → 精准塑形 → 结构化输出")

# 输入区
col1, col2 = st.columns([3, 1])

with col1:
    input_prompt = st.text_area(
        "✏️ 输入你的 Prompt",
        height=180,
        placeholder="例如：帮我写一个关于程序员创业的小红书文案...",
        key="input"
    )

with col2:
    st.markdown("### 📊 统计")
    if input_prompt:
        st.metric("字符", len(input_prompt))
        st.metric("词汇", len(input_prompt.split()))
        
        # 预估 token（粗略）
        est_tokens = len(input_prompt) // 4
        st.metric("预估Token", est_tokens)
    else:
        st.info("输入后显示统计")

# 优化按钮
if st.button("✨ 一键优化", type="primary", use_container_width=True, disabled=remaining<=0):
    if not input_prompt:
        st.error("请输入 Prompt")
    elif not quota_mgr.check_quota(user_tier, st.session_state.usage_count):
        st.error("今日次数已用完，请升级 Pro")
        st.markdown("[💎 升级到 Pro](https://your-payment-link.com)")
    else:
        with st.spinner("🧠 AI 正在优化..."):
            time.sleep(0.5)  # 模拟处理
            result = optimizer.optimize(input_prompt, enable_layer4)
            st.session_state.usage_count += 1
            st.session_state.last_optimized = datetime.now().strftime("%H:%M")
        
        st.success("✅ 优化完成！")
        
        # 场景标签
        scene_emojis = {
            'code': '💻', 'writing': '✍️', 'analysis': '📊', 
            'creative': '💡', 'business': '💼', 'general': '🤖'
        }
        st.info(f"{scene_emojis.get(result['scene'], '🤖')} 检测场景：**{result['scene'].upper()}**")
        
        # 结果展示
        st.markdown("---")
        st.markdown("### 🎉 优化结果")
        
        if result['format'] == 'structured':
            st.json(result['layers']['layer4'])
        else:
            st.code(result['final'], language='markdown')
        
        # 操作按钮
        col_copy, col_use = st.columns(2)
        with col_copy:
            st.download_button(
                "📋 复制",
                result['final'],
                file_name=f"optimized_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_use:
            if st.button("🚀 去使用", use_container_width=True):
                st.markdown(f"[打开 ChatGPT](https://chat.openai.com/?q={result['final'][:100]}...)")
        
        # Pro 用户显示详细过程
        if user_tier in ['pro', 'team']:
            with st.expander("🔍 查看优化过程"):
                tabs = st.tabs(["原始", "压缩", "重组", "塑形", "最终"])
                with tabs[0]:
                    st.code(result['original'])
                with tabs[1]:
                    st.code(result['layers']['layer1'])
                with tabs[2]:
                    st.code(result['layers']['layer2'])
                with tabs[3]:
                    st.code(result['layers']['layer3'])
                with tabs[4]:
                    st.code(result['final'])

# 付费墙提示
if remaining == 0 and user_tier == 'free':
    st.markdown("---")
    st.markdown("## 💎 解锁无限次数")
    st.markdown("""
    | 功能 | Free | Pro ¥29/月 | Team ¥99/月 |
    |------|------|-----------|------------|
    | 每日优化 | 10次 | 无限 | 无限 |
    | 结构化输出 | ❌ | ✅ | ✅ |
    | 历史记录 | ❌ | ✅ | ✅ |
    | API 调用 | ❌ | ✅ | ✅ |
    | 网页监控 | ❌ | ❌ | ✅ |
    """)
    
    col_pay, col_contact = st.columns(2)
    with col_pay:
        if st.button("💳 立即升级", type="primary", use_container_width=True):
            st.markdown("[点击支付](https://your-payment-link.com)")
    with col_contact:
        if st.button("💬 咨询客服", use_container_width=True):
            st.info("客服微信：your-wechat-id")

# 底部
st.markdown("---")
st.caption("🤖 Prompt 优化器 Pro | Make every conversation more efficient")
st.caption("📧 联系：wphj666@gmail.com | 🐦 Twitter: @yourhandle")
