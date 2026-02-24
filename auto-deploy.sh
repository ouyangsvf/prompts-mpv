#!/bin/bash
# Prompt优化器自动部署脚本
# 24小时运行，自动监控

cd /Users/ouyansufen/clawd/skills/prompt-optimizer

# 检查是否有更新
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "[$(date)] 检测到变更，准备部署..."
    
    # 提交变更
    git add -A
    git commit -m "Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 推送到GitHub（如果配置了远程仓库）
    if git remote get-url origin 2>/dev/null; then
        git push origin main
        echo "[$(date)] 已推送到GitHub"
    fi
    
    # 飞书通知
    curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"msg_type\": \"text\",
            \"content\": {
                \"text\": \"🚀 Prompt优化器已自动部署\\n时间：$(date '+%Y-%m-%d %H:%M:%S')\\n状态：成功\"
            }
        }" 2>/dev/null || echo "飞书通知未配置"
fi

# 检查服务健康
# curl -f https://your-app.streamlit.app/health || echo "服务异常"

echo "[$(date)] 部署检查完成"
