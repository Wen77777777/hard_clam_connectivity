# GitHub上传完整指南

## 📋 上传前准备

### 1. 确认已完成个人信息修改
参考 `PERSONALIZATION_GUIDE.md` 完成所有必要的信息替换。

### 2. 安装Git（如果还没有）

#### Mac系统
```bash
# 检查是否已安装
git --version

# 如果没有，安装Xcode Command Line Tools
xcode-select --install
```

#### Windows系统
下载并安装：https://git-scm.com/download/win

### 3. 配置Git（首次使用）
```bash
# 设置用户名和邮箱（与GitHub账号一致）
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的GitHub邮箱"

# 验证配置
git config --list
```

---

## 🌐 步骤1：创建GitHub仓库

### 方式A：通过GitHub网站（推荐新手）

1. **登录GitHub**
   - 访问 https://github.com
   - 登录您的账号

2. **创建新仓库**
   - 点击右上角 "+" → "New repository"

3. **填写仓库信息**
   ```
   Repository name: hard_clam_connectivity
   Description: Analysis code for hard clam connectivity in the Bohai Sea

   选项：
   ☑ Public （推荐，便于引用和审稿）
   ☐ Add a README file （不勾选，我们已有README）
   ☐ Add .gitignore （不勾选，我们已有.gitignore）
   ☑ Choose a license: MIT （可选）
   ```

4. **创建仓库**
   - 点击 "Create repository"
   - **保存仓库URL**，格式如：
     `https://github.com/您的用户名/hard_clam_connectivity.git`

---

## 💻 步骤2：本地初始化Git仓库

打开终端（Mac）或命令提示符（Windows），执行以下命令：

```bash
# 1. 进入项目目录
cd /Users/apple/Desktop/hard_clam_kit/hard_clam_connectivity

# 2. 初始化Git仓库
git init

# 3. 查看当前文件状态
git status
```

**预期输出：**
```
Initialized empty Git repository in ...
Untracked files:
  .gitignore
  LICENSE
  README.md
  ... (其他文件)
```

---

## 📦 步骤3：添加文件到Git

```bash
# 1. 添加所有文件
git add .

# 2. 查看已添加的文件
git status
```

**预期输出：**
```
Changes to be committed:
  new file:   .gitignore
  new file:   LICENSE
  new file:   README.md
  ... (其他文件)
```

**⚠️ 如果看到不应该提交的大文件，使用：**
```bash
# 查看大文件
find . -type f -size +10M -not -path "./.git/*"

# 从暂存区移除
git reset HEAD 大文件路径
```

---

## ✍️ 步骤4：创建首次提交

```bash
# 创建提交，包含详细的提交信息
git commit -m "Initial release: Hard clam connectivity analysis code

This repository contains the complete analysis code for the manuscript:
'Temperature-driven connectivity dynamics in marine protected area
networks: A nine-year assessment using effective accumulated
temperature framework in the Bohai Sea'

Code includes:
- Individual-based model (IBM) for Hard clam larval dispersal
- Connectivity analysis across 9 years (2014-2022)
- Temperature classification and effect analysis
- Statistical utilities (bootstrap, FDR correction, robust regression)
- Data processing and visualization scripts

Total: 3,271 lines of Python code across 7 scripts
Documentation: 963 lines across 6 markdown files
"
```

**预期输出：**
```
[main (root-commit) xxxxxx] Initial release: Hard clam connectivity analysis code
 XX files changed, XXXX insertions(+)
 create mode 100644 .gitignore
 create mode 100644 LICENSE
 ...
```

---

## 🔗 步骤5：连接到GitHub远程仓库

```bash
# 添加远程仓库（替换为您的实际URL）
git remote add origin https://github.com/您的用户名/hard_clam_connectivity.git

# 验证远程仓库
git remote -v
```

**预期输出：**
```
origin  https://github.com/您的用户名/hard_clam_connectivity.git (fetch)
origin  https://github.com/您的用户名/hard_clam_connectivity.git (push)
```

---

## 🚀 步骤6：推送到GitHub

```bash
# 1. 设置默认分支为main
git branch -M main

# 2. 推送代码到GitHub
git push -u origin main
```

**第一次推送时，会要求身份验证：**

### Mac系统（推荐使用Personal Access Token）
1. 在GitHub上生成Token：
   - Settings → Developer settings → Personal access tokens → Generate new token
   - 选择权限：`repo` (全部)
   - 生成并**保存Token**（只显示一次！）

2. 推送时输入：
   - Username: 您的GitHub用户名
   - Password: **粘贴刚才的Token**（不是GitHub密码）

### 保存凭证（避免重复输入）
```bash
# Mac系统
git config --global credential.helper osxkeychain

# Windows系统
git config --global credential.helper wincred
```

**成功推送的输出：**
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to X threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), XXX KiB | XXX MiB/s, done.
Total XX (delta X), reused 0 (delta 0)
To https://github.com/您的用户名/hard_clam_connectivity.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## ✅ 步骤7：验证上传

1. **访问您的GitHub仓库**
   ```
   https://github.com/您的用户名/hard_clam_connectivity
   ```

2. **检查清单：**
   - [ ] 所有文件都已上传
   - [ ] README.md正确显示
   - [ ] 图片可以查看
   - [ ] 目录结构清晰
   - [ ] 没有上传不应该公开的文件

3. **查看README预览**
   - GitHub会自动渲染README.md
   - 检查格式是否正确
   - 链接是否有效

---

## 🏷️ 步骤8：创建Release版本（可选但推荐）

### 为什么创建Release？
- 获得固定版本号
- 便于引用特定版本
- Zenodo可以自动归档
- 更专业的呈现方式

### 创建步骤：

1. **在GitHub仓库页面，点击 "Releases"**

2. **点击 "Create a new release"**

3. **填写Release信息：**
   ```
   Tag version: v1.0.0
   Release title: Initial Release - Manuscript Submission v1.0.0

   Description:
   ## Analysis Code for Hard Clam Connectivity Study

   This is the initial release of the analysis code accompanying our manuscript:
   "Temperature-driven connectivity dynamics in marine protected area networks"

   ### Code Contents
   - Individual-based model (IBM) implementation
   - Connectivity analysis (2014-2022)
   - Temperature effect analysis
   - Statistical utilities and visualization

   ### Statistics
   - 7 Python scripts (3,271 lines)
   - 6 documentation files (963 lines)
   - Full reproducibility support

   ### Citation
   Please cite this code as:
   [Your Name] (2024). Hard clam connectivity analysis code.
   GitHub: https://github.com/您的用户名/hard_clam_connectivity
   Version: v1.0.0
   ```

4. **选择分支：** main

5. **点击 "Publish release"**

---

## 📊 步骤9：获取Zenodo DOI（可选）

### 为什么需要Zenodo DOI？
- 永久存档代码
- 获得可引用的DOI
- 满足期刊数据可用性要求
- 提高学术影响力

### 操作步骤：

1. **访问Zenodo**
   - 网址：https://zenodo.org
   - 用GitHub账号登录

2. **连接GitHub仓库**
   - Settings → GitHub
   - 启用 hard_clam_connectivity 仓库

3. **创建新Release**
   - 在GitHub上创建新的Release（如v1.0.1）
   - Zenodo会自动检测并归档

4. **获取DOI**
   - Zenodo生成DOI（格式：10.5281/zenodo.XXXXXXX）
   - **更新README.md中的DOI引用**

5. **推送更新**
   ```bash
   git add README.md
   git commit -m "Update: Add Zenodo DOI"
   git push
   ```

---

## 📝 步骤10：更新论文中的引用

### 在Methods部分添加：

```
Code Availability
All analysis code is available at https://github.com/您的用户名/hard_clam_connectivity
(DOI: 10.5281/zenodo.XXXXXXX)
```

### 在References中引用：

```
Your Name (2024). Analysis code for temperature-driven connectivity
dynamics in marine protected area networks. GitHub repository.
https://github.com/您的用户名/hard_clam_connectivity
DOI: 10.5281/zenodo.XXXXXXX
```

---

## 🔧 常见问题解决

### Q1: 推送时提示"Permission denied"
**解决方案：**
```bash
# 确认使用Personal Access Token，不是密码
# 或使用SSH方式（需要先设置SSH key）

# 生成SSH key
ssh-keygen -t ed25519 -C "您的邮箱"

# 添加到GitHub：Settings → SSH and GPG keys → New SSH key
# 更改远程URL为SSH
git remote set-url origin git@github.com:您的用户名/hard_clam_connectivity.git
```

### Q2: 推送太慢或失败
**解决方案：**
```bash
# 检查文件大小
du -sh .git

# 如果过大，检查是否包含大文件
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print $3, $4}' | sort -n | tail -10

# 从历史中删除大文件（谨慎操作）
git filter-branch --tree-filter 'rm -f 大文件路径' HEAD
```

### Q3: 不小心提交了敏感信息
**解决方案：**
```bash
# 从历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch 敏感文件" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

### Q4: 想要更新已上传的代码
**解决方案：**
```bash
# 1. 修改本地文件
# 2. 查看变更
git status
git diff

# 3. 添加变更
git add 修改的文件

# 4. 提交变更
git commit -m "Update: 描述修改内容"

# 5. 推送到GitHub
git push
```

---

## 📱 推荐工具

### GUI工具（图形界面，更友好）
- **GitHub Desktop**: https://desktop.github.com （推荐新手）
- **SourceTree**: https://www.sourcetreeapp.com
- **GitKraken**: https://www.gitkraken.com

### VS Code集成
- 内置Git支持
- 可视化操作
- Source Control面板

---

## ✨ 上传后的维护

### 定期检查
- [ ] Issues是否有新提问
- [ ] 是否需要更新代码
- [ ] README是否需要补充

### 论文发表后
- [ ] 更新DOI
- [ ] 更新引用信息
- [ ] 添加Published标签
- [ ] 更新版本号（v1.1.0）

---

## 🎯 成功标志

上传成功后，您应该能够：

✅ 在 `https://github.com/您的用户名/hard_clam_connectivity` 看到完整代码
✅ README.md正确渲染显示
✅ 所有文件结构清晰
✅ 可以分享链接给合作者/审稿人
✅ 代码有明确的License
✅ 有详细的使用说明

---

## 📞 需要帮助？

- GitHub官方文档：https://docs.github.com
- Git教程：https://git-scm.com/book/zh/v2
- GitHub学习实验室：https://lab.github.com

---

**祝您上传顺利！** 🎉

如果遇到问题，可以：
1. 查看本指南的"常见问题解决"部分
2. 搜索错误信息
3. 在Stack Overflow提问
4. 联系GitHub Support