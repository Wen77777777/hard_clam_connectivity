# 个人信息修改指南

## 需要修改的文件和位置

### 1️⃣ README.md - 主要项目说明文件

#### 位置1：第5行 - 物种学名
```markdown
当前：Hard clam (*Meretrix meretrix*)
建议：确认您研究的物种学名是否正确
```

#### 位置2：第156-162行 - 引用信息
```markdown
当前：
@article{yourname2024,
  title={Temperature-driven connectivity dynamics in marine protected area networks:
         A nine-year assessment using effective accumulated temperature framework in the Bohai Sea},
  author={Your Name et al.},
  journal={Journal Name},
  year={2024},
  volume={X},
  pages={XXX-XXX},
  doi={10.XXXX/XXXXXX}
}

需要修改为：
@article{您的姓氏2024,
  author={您的姓名1, 姓名2, 姓名3, etc.},
  journal={投稿期刊名称},
  year={发表年份},
  # 其他信息在接受后填写
}
```

#### 位置3：第174行 - 联系信息
```markdown
当前：
- **Corresponding Author**: [Your Name] (email@institution.edu)
- **Lab Website**: [Your Lab URL]
- **Issues**: Please report bugs via GitHub Issues

需要修改为：
- **Corresponding Author**: 您的姓名 (您的邮箱@单位.edu.cn)
- **Lab Website**: https://您的实验室网站
- **Issues**: https://github.com/您的用户名/hard_clam_connectivity/issues
```

#### 位置4：第197-199行 - 致谢信息
```markdown
当前：
- Ocean model data provided by [Institution/Collaborator]
- Funding support from [Grant Numbers]
- Computational resources provided by [HPC Center]

需要修改为：
- Ocean model data provided by 提供ROMS数据的单位/合作者
- Funding support from 基金号（如：国家自然科学基金 No. XXXXXXXX）
- Computational resources provided by 计算中心名称
```

---

### 2️⃣ LICENSE - 版权信息

#### 第3行 - 版权声明
```
当前：Copyright (c) 2024 [Your Name/Institution]

需要修改为：Copyright (c) 2024 您的姓名 或 您的单位名称
```

---

### 3️⃣ data/README.md - 数据文档

#### 位置1：第146-147行 - 数据引用
```markdown
当前：
[Authors] (2024). Temperature-driven connectivity dynamics dataset for Hard clam
in the Bohai Sea (2014-2022). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

需要修改为：
您的姓名等 (2024). Temperature-driven connectivity dynamics dataset for Hard clam
in the Bohai Sea (2014-2022). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
（DOI在Zenodo上传后自动生成，先保留占位符）
```

#### 位置2：第163行 - 联系邮箱
```markdown
当前：
- Email: [data.contact@email.com]
- GitHub Issues: [repository issues page]

需要修改为：
- Email: 您的邮箱
- GitHub Issues: https://github.com/您的用户名/hard_clam_connectivity/issues
```

---

### 4️⃣ PROJECT_STATUS.md - 项目状态

#### 第299行 - 联系信息
```markdown
当前：
- **Corresponding Author**: [Your Name] (email@institution.edu)
- **Lab Website**: [Your Lab URL]
- **Issues**: [GitHub Issues URL]

需要修改为：
- **Corresponding Author**: 您的姓名 (您的邮箱)
- **Lab Website**: 您的实验室网站
- **Issues**: https://github.com/您的用户名/hard_clam_connectivity/issues
```

---

## 📝 修改步骤

### 准备工作
1. 打开文本编辑器（推荐：VS Code, Sublime Text, 或记事本）
2. 准备好以下信息：
   - ✅ 您的英文姓名
   - ✅ 您的单位邮箱
   - ✅ 基金资助信息
   - ✅ 合作单位/致谢信息
   - ✅ 实验室网站（如有）

### 替换方法（使用查找替换功能）

#### 方法1：使用VS Code（推荐）
```
1. 用VS Code打开hard_clam_connectivity文件夹
2. 按 Cmd+Shift+F (Mac) 或 Ctrl+Shift+F (Windows) 打开全局搜索
3. 搜索关键词，逐个替换：
   - "[Your Name]" → "您的姓名"
   - "email@institution.edu" → "您的邮箱"
   - "[Institution/Collaborator]" → "合作单位"
   - "[Grant Numbers]" → "基金号"
   - "[HPC Center]" → "计算中心"
```

#### 方法2：使用命令行
```bash
cd /Users/apple/Desktop/hard_clam_kit/hard_clam_connectivity

# 替换作者名（示例）
sed -i '' 's/\[Your Name\]/Zhang San/g' README.md LICENSE PROJECT_STATUS.md data/README.md

# 替换邮箱（示例）
sed -i '' 's/email@institution.edu/zhangsan@university.edu.cn/g' README.md PROJECT_STATUS.md data/README.md

# 以此类推...
```

---

## 快速修改清单 ✅

完成后在每项前打勾：

- [ ] README.md - 第5行物种学名检查
- [ ] README.md - 第156-162行引用信息
- [ ] README.md - 第174行联系信息
- [ ] README.md - 第197-199行致谢信息
- [ ] LICENSE - 第3行版权信息
- [ ] data/README.md - 第146-147行数据引用
- [ ] data/README.md - 第163行联系邮箱
- [ ] PROJECT_STATUS.md - 第299行联系信息

---

## ⚠️ 暂时不需要填写的信息

以下信息在论文接受/发表后再填写：

- [ ] 期刊卷号、页码
- [ ] 论文DOI
- [ ] Zenodo数据DOI
- [ ] 具体发表年份（如果跨年）

可以先保留占位符如：`doi={10.XXXX/XXXXXX}`

---

## 示例：完整修改后的样子

### README.md 引用部分
```bibtex
@article{zhang2024,
  title={Temperature-driven connectivity dynamics in marine protected area networks:
         A nine-year assessment using effective accumulated temperature framework in the Bohai Sea},
  author={Zhang, San and Li, Si and Wang, Wu},
  journal={Marine Ecology Progress Series},
  year={2024},
  volume={XXX},
  pages={XXX-XXX},
  doi={10.XXXX/XXXXXX}
}
```

### README.md 联系部分
```markdown
### Contact

- **Corresponding Author**: Zhang San (zhangsan@ouc.edu.cn)
- **Lab Website**: http://marinelab.ouc.edu.cn
- **Issues**: Please report bugs via [GitHub Issues](https://github.com/zhangsan/hard_clam_connectivity/issues)
```

### LICENSE
```
Copyright (c) 2024 Zhang San, Ocean University of China
```

---

## 检查清单

修改完成后，请检查：

1. [ ] 所有 `[Your Name]` 已替换
2. [ ] 所有 `email@institution.edu` 已替换
3. [ ] 所有 `[Institution]` 已替换
4. [ ] 所有 `[Grant Numbers]` 已替换
5. [ ] GitHub用户名占位符已确定
6. [ ] 邮箱地址正确无误
7. [ ] 单位名称正确
8. [ ] 基金信息完整

---

下一步：修改完成后，查看 GITHUB_UPLOAD_GUIDE.md 获取上传步骤！