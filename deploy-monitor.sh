#!/bin/bash
# 24小时自动部署和监控脚本

PROJECT_DIR="/Users/ouyansufen/clawd/skills/prompt-optimizer"
LOG_FILE="/tmp/prompt-optimizer-deploy.log"
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"

echo "[$(date)] 开始部署检查..." >> $LOG_FILE

cd $PROJECT_DIR

# 检查代码更新
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "[$(date)] 发现本地修改，准备提交..." >> $LOG_FILE
    git add .
    git commit -m "Auto deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
    
    # 飞书通知
    curl -X POST $FEISHU_WEBHOOK \
        -H "Content-Type: application/json" \
        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"🚀 Prompt优化器已自动部署\\n时间：$(date '+%Y-%m-%d %H:%M:%S')\\n提交：$(git log -1 --pretty=format:'%h %s')\"}}"
fi

# 检查服务状态（如果部署到自己的服务器）
# curl -f https://your-app.streamlit.app/health || echo "服务异常" >> $LOG_FILE

echo "[$(date)] 部署检查完成" >> $LOG_FILE
