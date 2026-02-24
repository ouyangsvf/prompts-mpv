# Prompt 优化器 - Streamlit Cloud 部署配置

## 部署步骤（3分钟完成）

### 1. 创建 GitHub 仓库
```bash
# 新建仓库
mkdir prompt-optimizer && cd prompt-optimizer
git init

# 复制必要文件
cp /Users/ouyansufen/clawd/skills/prompt-optimizer/app.py .
cp /Users/ouyansufen/clawd/skills/prompt-optimizer/requirements.txt .

# 创建 README
echo "# Prompt 优化器" > README.md

# 提交
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/prompt-optimizer.git
git push -u origin main
```

### 2. 连接 Streamlit Cloud
1. 访问 https://streamlit.io/cloud
2. 用 GitHub 登录
3. 点击 "New App"
4. 选择你的仓库
5. 点击 Deploy

### 3. 完成
- 自动获得 https://prompt-optimizer-xxxxx.streamlit.app
- 无需维护服务器
- 免费额度足够个人使用

---

## 或者：本地极简方案（绕过Python 3.14）

使用 miniconda 创建 Python 3.11 环境：

```bash
# 安装 miniconda
brew install miniconda

# 创建 Python 3.11 环境
conda create -n promptopt python=3.11 -y
conda activate promptopt

# 安装依赖（飞快）
pip install streamlit openai python-dotenv

# 运行
streamlit run app.py
```
