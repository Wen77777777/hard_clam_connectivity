# 快速开始指南 - 5分钟上传到GitHub

## 📌 3个文件，8处修改，6条命令

---

## 第一步：修改个人信息（5分钟）

### 文件1: README.md

用文本编辑器打开，搜索并替换：

1. **第174行** - 联系信息
   ```markdown
   把: - **Corresponding Author**: [Your Name] (email@institution.edu)
   改: - **Corresponding Author**: 您的姓名 (您的邮箱@单位.edu.cn)
   ```

2. **第156-162行** - 引用信息
   ```markdown
   把: author={Your Name et al.},
   改: author={姓名1, 姓名2, 姓名3},

   把: journal={Journal Name},
   改: journal={投稿期刊名称},
   ```

3. **第197-199行** - 致谢
   ```markdown
   把: - Ocean model data provided by [Institution/Collaborator]
   改: - Ocean model data provided by 合作单位名称

   把: - Funding support from [Grant Numbers]
   改: - Funding support from 国家自然科学基金 No. XXXXXXXX

   把: - Computational resources provided by [HPC Center]
   改: - Computational resources provided by 计算中心名称
   ```

### 文件2: LICENSE

4. **第3行** - 版权
   ```
   把: Copyright (c) 2024 [Your Name/Institution]
   改: Copyright (c) 2024 您的姓名
   ```

### 文件3: data/README.md

5. **第146行** - 数据引用
   ```markdown
   把: [Authors] (2024).
   改: 您的姓名等 (2024).
   ```

6. **第163行** - 邮箱
   ```markdown
   把: - Email: [data.contact@email.com]
   改: - Email: 您的邮箱
   ```

### 文件4: PROJECT_STATUS.md

7. **第299行** - 联系信息
   ```markdown
   把: - **Corresponding Author**: [Your Name] (email@institution.edu)
   改: - **Corresponding Author**: 您的姓名 (您的邮箱)
   ```

### 全局替换（可选，更快）

如果使用VS Code：
- 按 `Cmd+Shift+H` (Mac) 或 `Ctrl+Shift+H` (Windows)
- 查找: `[Your Name]` → 替换: `您的姓名`
- 查找: `email@institution.edu` → 替换: `您的邮箱`
- 点击"全部替换"

---

## 第二步：上传到GitHub（3分钟）

### 方式A：命令行（推荐）

```bash
# 1. 进入项目文件夹
cd /Users/apple/Desktop/hard_clam_kit/hard_clam_connectivity

# 2. 初始化Git
git init

# 3. 添加所有文件
git add .

# 4. 创建首次提交
git commit -m "Initial release: Hard clam connectivity analysis code"

# 5. 在GitHub网站创建新仓库（仓库名：hard_clam_connectivity）
# 获取仓库URL（例如：https://github.com/zhangsan/hard_clam_connectivity.git）

# 6. 连接远程仓库（替换为您的URL）
git remote add origin https://github.com/您的用户名/hard_clam_connectivity.git

# 7. 设置主分支
git branch -M main

# 8. 推送到GitHub
git push -u origin main
```

### 方式B：GitHub Desktop（更简单）

1. 下载并安装GitHub Desktop
2. 打开软件，登录GitHub账号
3. File → Add Local Repository
4. 选择 `/Users/apple/Desktop/hard_clam_kit/hard_clam_connectivity`
5. 点击 "Publish repository"
6. 填写名称：`hard_clam_connectivity`
7. 选择 Public
8. 点击 "Publish"

---

## 第三步：验证上传（1分钟）

访问您的GitHub仓库：
```
https://github.com/您的用户名/hard_clam_connectivity
```

检查：
- ✅ README显示正常
- ✅ 文件都已上传
- ✅ 个人信息已更新

---

## 常见问题

### Q: 推送时要求输入密码？
**A:** 使用Personal Access Token，不是GitHub密码
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token → 选择 `repo` 权限
3. 复制Token
4. 推送时用户名输入GitHub用户名，密码粘贴Token

### Q: 如何更新已上传的代码？
**A:**
```bash
# 修改文件后
git add .
git commit -m "Update: 描述修改内容"
git push
```

### Q: 不小心上传了错误的文件？
**A:**
```bash
# 从Git中删除但保留本地文件
git rm --cached 文件名
git commit -m "Remove: 删除错误文件"
git push
```

---

## 完成后在论文中引用

### Methods部分：
```
Code Availability: All analysis code is available at
https://github.com/您的用户名/hard_clam_connectivity
```

---

## 需要详细说明？

- 个人信息修改详细说明：查看 `PERSONALIZATION_GUIDE.md`
- GitHub上传详细步骤：查看 `GITHUB_UPLOAD_GUIDE.md`
- 完整检查清单：查看 `FINAL_CHECKLIST.md`

---

**就这么简单！** 🎉