"""
Prompt 优化器 - 第四层：结构化输出
基于 prompts.csv 中的 STRUCTURED 类型最佳实践

升级说明：
- 原三层架构：语义压缩 → 结构重组 → 精准塑形
- 新增第四层：结构化输出（当用户需要 JSON/API 格式时启用）
"""

import json
import re
from typing import Dict, Any, Optional


class StructuredOutputLayer:
    """
    第四层：结构化输出层
    将优化后的提示词包装成 JSON Schema 格式
    """
    
    def __init__(self):
        self.structured_keywords = [
            'json', '结构化', 'structured', 'api', 'schema',
            '格式', 'format', '模板', 'template', '输出格式'
        ]
    
    def detect_structured_intent(self, user_input: str) -> bool:
        """检测用户是否需要结构化输出"""
        input_lower = user_input.lower()
        return any(kw in input_lower for kw in self.structured_keywords)
    
    def extract_variables(self, prompt: str) -> Dict[str, Any]:
        """
        从提示词中提取变量参数
        支持格式：${VariableName:default_value} 或 {{variable}}
        """
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
    
    def infer_output_schema(self, user_intent: str) -> Dict[str, Any]:
        """
        根据用户意图推断输出结构
        """
        # 代码审查类
        if any(kw in user_intent.lower() for kw in ['code', 'review', '代码', '审查']):
            return {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "category": {"type": "string"},
                    "line_number": {"type": "number"},
                    "suggestion": {"type": "string"},
                    "code_example": {"type": "string"}
                }
            }
        
        # 数据转换类
        if any(kw in user_intent.lower() for kw in ['data', 'transform', '数据', '转换']):
            return {
                "type": "object",
                "properties": {
                    "transformed_data": {"type": "object"},
                    "summary": {"type": "string"},
                    "warnings": {"type": "array", "items": {"type": "string"}}
                }
            }
        
        # 故事/内容生成类
        if any(kw in user_intent.lower() for kw in ['story', 'content', '故事', '内容']):
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "metadata": {"type": "object"}
                }
            }
        
        # 默认通用结构
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "details": {"type": "object"},
                "status": {"type": "string", "enum": ["success", "error", "partial"]}
            }
        }
    
    def wrap_structured(self, prompt: str, user_intent: str) -> Dict[str, Any]:
        """
        将普通提示词包装成结构化格式
        """
        variables = self.extract_variables(prompt)
        output_schema = self.infer_output_schema(user_intent)
        
        # 从用户意图推断 role
        role = self._infer_role(user_intent)
        
        structured_prompt = {
            "role": role,
            "parameters": variables if variables else {"input": {"type": "string", "description": "用户输入"}},
            "output_format": output_schema,
            "instructions": prompt
        }
        
        return structured_prompt
    
    def _infer_role(self, user_intent: str) -> str:
        """从用户意图推断角色名称"""
        intent_lower = user_intent.lower()
        
        role_mapping = {
            'code': 'Code Assistant',
            'review': 'Code Review Assistant',
            'story': 'Story Generator',
            'content': 'Content Creator',
            'data': 'Data Transformer',
            'regex': 'RegEx Generator',
            'sql': 'SQL Assistant',
            'translate': 'Translation Assistant',
            'review': 'Review Assistant'
        }
        
        for keyword, role in role_mapping.items():
            if keyword in intent_lower:
                return role
        
        return "AI Assistant"
    
    def format_output(self, structured: Dict[str, Any], format_type: str = "json") -> str:
        """格式化输出"""
        if format_type == "json":
            return json.dumps(structured, ensure_ascii=False, indent=2)
        elif format_type == "yaml":
            # 简单 YAML 格式
            lines = []
            lines.append(f"role: {structured['role']}")
            lines.append("parameters:")
            for key, value in structured.get('parameters', {}).items():
                lines.append(f"  {key}:")
                for k, v in value.items():
                    lines.append(f"    {k}: {v}")
            lines.append("instructions: |")
            for line in structured['instructions'].split('\n'):
                lines.append(f"  {line}")
            return '\n'.join(lines)
        else:
            return str(structured)


class PromptOptimizerV2:
    """
    Prompt 优化器 v2.0
    四层架构：语义压缩 → 结构重组 → 精准塑形 → 结构化输出
    """
    
    def __init__(self):
        self.layer1 = SemanticCompressionLayer()
        self.layer2 = StructureReorganizationLayer()
        self.layer3 = PrecisionShapingLayer()
        self.layer4 = StructuredOutputLayer()
    
    def optimize(self, prompt: str, user_intent: str = "", enable_structured: bool = False) -> Dict[str, Any]:
        """
        执行四层优化
        
        Args:
            prompt: 原始提示词
            user_intent: 用户意图描述
            enable_structured: 强制启用结构化输出
        
        Returns:
            优化结果，包含各层输出
        """
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
        shaped = self.layer3.shape(restructured, user_intent)
        result["layers"]["layer3_precision_shaping"] = shaped
        
        # 第四层：结构化输出（条件触发）
        if enable_structured or self.layer4.detect_structured_intent(user_intent):
            structured = self.layer4.wrap_structured(shaped, user_intent)
            result["layers"]["layer4_structured_output"] = structured
            result["final_output"] = structured
            result["output_format"] = "structured"
        else:
            result["final_output"] = shaped
            result["output_format"] = "text"
        
        return result


# ===== 占位层实现（需要与原有实现集成）=====

class SemanticCompressionLayer:
    """第一层：语义压缩 - 去除冗余，保留核心语义"""
    def compress(self, prompt: str) -> str:
        # TODO: 集成原有实现
        return prompt

class StructureReorganizationLayer:
    """第二层：结构重组 - 优化信息层级和逻辑流"""
    def reorganize(self, prompt: str) -> str:
        # TODO: 集成原有实现
        return prompt

class PrecisionShapingLayer:
    """第三层：精准塑形 - 针对特定场景微调"""
    def shape(self, prompt: str, context: str) -> str:
        # TODO: 集成原有实现
        return prompt


# ===== 使用示例 =====

if __name__ == "__main__":
    optimizer = PromptOptimizerV2()
    
    # 示例 1：普通文本优化
    result1 = optimizer.optimize(
        prompt="帮我写一个故事，关于一个程序员",
        user_intent="生成创意故事"
    )
    print("=== 示例 1：文本格式 ===")
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    
    # 示例 2：结构化输出（自动检测）
    result2 = optimizer.optimize(
        prompt="审查这段代码并给出建议",
        user_intent="代码审查，输出 JSON 格式"
    )
    print("\n=== 示例 2：结构化格式（自动检测） ===")
    print(json.dumps(result2, ensure_ascii=False, indent=2))
    
    # 示例 3：强制结构化输出
    result3 = optimizer.optimize(
        prompt="生成一个正则表达式匹配邮箱",
        user_intent="正则表达式生成",
        enable_structured=True
    )
    print("\n=== 示例 3：强制结构化格式 ===")
    print(json.dumps(result3, ensure_ascii=False, indent=2))
