"""
Prompt 优化器 Pro - 商业化版本
四层架构 + 盈利功能 + 移动端适配
"""

import streamlit as st
import json
import re
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

# ===== 页面配置 - 移动端优化 =====
st.set_page_config(
    page_title="Prompt 优化器 Pro",
    page_icon="🐙",
    layout="centered",  # 移动端更好的居中布局
    initial_sidebar_state="collapsed"  # 移动端默认收起侧边栏
)

# ===== 移动端检测和适配 =====
def is_mobile():
    """检测是否为移动设备"""
    # 通过屏幕宽度简单判断
    return st.session_state.get('screen_width', 1200) < 768

# 自定义CSS - 移动端适配
st.markdown("""
<style>
    /* 移动端优化 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 1rem 1rem 1rem;
            max-width: 100%;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }
        .stTextArea textarea { font-size: 16px !important; }  /* 防止iOS缩放 */
        .stButton button { width: 100%; }
        .stProgress > div > div { height: 20px; }
    }
    
    /* 通用样式 */
    .logo-container { text-align: center; margin-bottom: 1rem; }
    .logo-container img { max-width: 120px; height: auto; }
    .usage-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .payment-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00d4aa;
    }
</style>

<script>
    // 检测屏幕宽度
    window.addEventListener('resize', function() {
        const width = window.innerWidth;
        // 通过localStorage传递宽度信息
        localStorage.setItem('screen_width', width);
    });
    localStorage.setItem('screen_width', window.innerWidth);
</script>
""", unsafe_allow_html=True)

# ===== 用户配额系统 - 简化版（基于浏览器存储） =====
class SimpleQuotaManager:
    """简化配额管理 - 使用session_state + localStorage概念"""
    
    def __init__(self):
        self.tiers = {
            'free': {'limit': 10, 'name': '免费版'},
            'pro': {'limit': 9999, 'name': 'Pro版'},
            'team': {'limit': 99999, 'name': 'Team版'}
        }
    
    def get_user_tier(self) -> str:
        """获取用户等级 - 从session或URL参数"""
        # 优先从URL参数获取（用于Pro用户激活）
        tier = st.query_params.get('tier', 'free')
        # 验证有效性
        if tier not in self.tiers:
            tier = 'free'
        return tier
    
    def get_usage_count(self) -> int:
        """获取使用次数 - 简化版，基于session"""
        if 'usage_count' not in st.session_state:
            st.session_state.usage_count = 0
        return st.session_state.usage_count
    
    def increment_usage(self):
        """增加使用次数"""
        if 'usage_count' not in st.session_state:
            st.session_state.usage_count = 0
        st.session_state.usage_count += 1
    
    def get_remaining(self, tier: str) -> int:
        """获取剩余次数"""
        used = self.get_usage_count()
        limit = self.tiers[tier]['limit']
        return max(0, limit - used)
    
    def check_quota(self, tier: str) -> bool:
        """检查是否还有配额"""
        return self.get_remaining(tier) > 0

# 初始化配额管理器
quota_mgr = SimpleQuotaManager()
user_tier = quota_mgr.get_user_tier()

# ===== Logo展示 - 居中 =====
st.markdown('<div class="logo-container"><img src="logo.png" alt="Prompt Optimizer"></div>', unsafe_allow_html=True)

# ===== 标题区 =====
st.title("🐙 Prompt 优化器 Pro")
st.caption("四层智能优化：语义压缩 → 结构重组 → 精准塑形 → 结构化输出")

# ===== 使用配额显示 - 卡片式 =====
remaining = quota_mgr.get_remaining(user_tier)
total_limit = quota_mgr.tiers[user_tier]['limit']
usage_percent = (total_limit - remaining) / total_limit if total_limit > 0 else 0

with st.container():
    tier_emoji = {'free': '🔵', 'pro': '🟡', 'team': '🟣'}
    tier_name = quota_mgr.tiers[user_tier]['name']
    
    st.markdown(f"""
    <div class="usage-card">
        <h4>{tier_emoji.get(user_tier, '🔵')} {tier_name}</h4>
        <p>今日剩余: <strong>{remaining}</strong> / {total_limit} 次</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(1 - usage_percent)

# ===== 付费提示 - 简化版 =====
if user_tier == 'free' and remaining < 3:
    with st.expander("💎 升级到 Pro - ¥29/月", expanded=True):
        st.markdown("""
        **Pro版特权：**
        - ✅ 无限次优化
        - ✅ 结构化输出（JSON格式）
        - ✅ 历史记录保存
        - ✅ 优先技术支持
        
        <div class="payment-info">
        <h4>🎯 付款方式（MVP简化版）</h4>
        
        <p><strong>方式1：微信/支付宝</strong><br>
        转账 ¥29 到：<code>wphj666@gmail.com</code><br>
        备注：Prompt Pro + 你的邮箱</p>
        
        <p><strong>方式2：联系开通</strong><br>
        发送邮件至：<code>wphj666@gmail.com</code><br>
        主题：开通Pro会员</p>
        
        <p><strong>⚡ 开通流程：</strong><br>
        1. 付款并备注邮箱<br>
        2. 发送邮件确认<br>
        3. 收到激活链接（5分钟内）<br>
        4. 点击链接即可使用Pro版</p>
        </div>
        
        <p><small>💡 MVP说明：当前为简化版，刷新页面会重置次数。Pro会员通过邮件激活链接验证。</small></p>
        """, unsafe_allow_html=True)
        
        if st.button("📧 我已付款，发送确认邮件", use_container_width=True):
            st.success("✅ 请发送邮件至 wphj666@gmail.com 确认开通")
            st.balloons()

# ===== 侧边栏配置 - 移动端收起 =====
with st.sidebar:
    st.header("⚙️ 设置")
    
    # API配置
    api_key = st.text_input("OpenAI API Key", type="password", 
                           value=st.session_state.get('api_key', ''),
                           help="可选，用于更高质量的优化")
    if api_key:
        st.session_state['api_key'] = api_key
    
    # 优化选项
    enable_layer4 = st.toggle("启用结构化输出", value=False,
                             help="输出JSON格式，适合API调用")
    show_intermediate = st.toggle("显示中间层", value=False,
                                  help="展示每层优化过程")
    
    st.divider()
    
    # 使用统计
    st.caption(f"本次已用: {quota_mgr.get_usage_count()} 次")
    st.caption(f"版本: MVP v1.0")

# ===== 核心优化类 =====

class SemanticCompressionLayer:
    """第一层：语义压缩"""
    
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
    """第二层：结构重组"""
    
    def reorganize(self, prompt: str) -> str:
        lines = prompt.split('\n')
        organized_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if any(kw in line.lower() for kw in ['role', '角色', 'act as']):
                line = f"【角色】{line}"
            elif any(kw in line.lower() for kw in ['task', '任务']):
                line = f"【任务】{line}"
            elif any(kw in line.lower() for kw in ['rule', '规则']):
                line = f"【规则】{line}"
            elif any(kw in line.lower() for kw in ['output', '输出']):
                line = f"【输出】{line}"
            
            organized_lines.append(line)
        
        return '\n'.join(organized_lines)

class PrecisionShapingLayer:
    """第三层：精准塑形"""
    
    def __init__(self):
        self.templates = {
            'code': {
                'prefix': '你是一位资深开发者，精通多种编程语言。',
                'suffix': '只输出代码，不解释。确保代码可运行、无bug。',
                'keywords': ['code', 'program', 'function', 'debug', '代码', '编程']
            },
            'writing': {
                'prefix': '你是一位专业写作者，文笔优美，逻辑清晰。',
                'suffix': '保持语言流畅，结构完整，引人入胜。',
                'keywords': ['write', 'essay', 'article', 'story', '写作', '文章']
            },
            'analysis': {
                'prefix': '你是一位分析专家，善于深度思考和逻辑推理。',
                'suffix': '提供结构化分析，列出关键点和数据支撑。',
                'keywords': ['analyze', 'analysis', 'research', '分析', '研究']
            },
            'creative': {
                'prefix': '你是一位创意专家，思维活跃，见解独到。',
                'suffix': '大胆创新，突破常规思维，提供独特视角。',
                'keywords': ['creative', 'idea', 'design', '创意', '设计']
            },
            'business': {
                'prefix': '你是一位商业顾问，熟悉市场和商业逻辑。',
                'suffix': '注重可行性，提供可落地的建议和ROI分析。',
                'keywords': ['business', 'market', 'strategy', '商业', '市场']
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
    """第四层：结构化输出"""
    
    def detect_structured_intent(self, user_input: str) -> bool:
        keywords = ['json', '结构化', 'structured', 'api', 'schema', '格式', 'template']
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

# ===== 主界面 - 移动端优化 =====
optimizer = PromptOptimizer()

# 输入区 - 移动端加大
col1, col2 = st.columns([3, 1])

with col1:
    input_prompt = st.text_area(
        "✏️ 输入你的 Prompt",
        height=150,  # 移动端适当减小
        placeholder="例如：帮我写一个关于程序员创业的小红书文案...",
        key="input"
    )

with col2:
    if input_prompt:
        st.metric("字符", len(input_prompt))
        st.metric("词汇", len(input_prompt.split()))
    else:
        st.info("输入后显示统计")

# 优化按钮 - 全宽
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    optimize_clicked = st.button("✨ 一键优化", type="primary", use_container_width=True, 
                                  disabled=not quota_mgr.check_quota(user_tier))

# 优化处理
if optimize_clicked:
    if not input_prompt:
        st.error("请输入 Prompt")
    else:
        # 检查配额
        if not quota_mgr.check_quota(user_tier):
            st.error("次数已用完，请升级Pro")
            st.info("💎 升级到 Pro - ¥29/月，获得无限次优化")
        else:
            with st.spinner("🧠 优化中..."):
                time.sleep(0.3)  # 模拟处理
                result = optimizer.optimize(input_prompt, enable_layer4)
                quota_mgr.increment_usage()
            
            st.success("✅ 优化完成！")
            
            # 场景标签
            scene_emojis = {
                'code': '💻', 'writing': '✍️', 'analysis': '📊', 
                'creative': '💡', 'business': '💼', 'general': '🤖'
            }
            st.info(f"{scene_emojis.get(result['scene'], '🤖')} 场景：**{result['scene'].upper()}**")
            
            # 结果展示 - 移动端优化
            st.markdown("---")
            st.markdown("### 🎉 优化结果")
            
            if result['format'] == 'structured':
                st.json(result['layers']['layer4'])
            else:
                st.code(result['final'], language='markdown')
            
            # 复制按钮
            st.download_button(
                "📋 复制结果",
                result['final'],
                file_name="optimized_prompt.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # Pro用户显示详细过程
            if user_tier in ['pro', 'team'] and show_intermediate:
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

# 底部信息 - 移动端友好
st.markdown("---")
st.caption("🤖 Prompt 优化器 Pro | 让每一次对话都更高效")
st.caption("📧 联系：wphj666@gmail.com")
st.caption("💡 提示：MVP版本，刷新页面会重置次数，Pro会员不受限制")
