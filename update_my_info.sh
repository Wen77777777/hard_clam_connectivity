#!/bin/bash
# 快速更新个人信息脚本
# 使用方法：bash update_my_info.sh

echo "开始更新个人信息..."

# 定义您的信息（请修改下面的内容）
YOUR_NAME="Wen Chen"  # 修改为您的英文姓名
YOUR_EMAIL="cw8057937@gmail.com"  # 已经是您的邮箱
YOUR_INSTITUTION="Ocean University of China"  # 修改为您的单位
YOUR_LAB_URL="https://your-lab-website.com"  # 修改为您的实验室网站（如果有）
YOUR_FUNDING="National Natural Science Foundation of China (Grant No. XXXXXXXX)"  # 修改为您的基金信息
YOUR_GITHUB_USERNAME="Wen77777777"  # 已经是您的GitHub用户名

echo "您的信息："
echo "  姓名: $YOUR_NAME"
echo "  邮箱: $YOUR_EMAIL"
echo "  单位: $YOUR_INSTITUTION"
echo "  GitHub: $YOUR_GITHUB_USERNAME"
echo ""

# 备份原始文件
echo "创建备份..."
cp README.md README.md.backup
cp LICENSE LICENSE.backup
cp data/README.md data/README.md.backup
cp PROJECT_STATUS.md PROJECT_STATUS.md.backup

# 更新 README.md
echo "更新 README.md..."
sed -i '' "s/\[Your Name\]/$YOUR_NAME/g" README.md
sed -i '' "s/email@institution\.edu/$YOUR_EMAIL/g" README.md
sed -i '' "s/Your Name et al\./$YOUR_NAME et al./g" README.md
sed -i '' "s/\[Institution\/Collaborator\]/$YOUR_INSTITUTION/g" README.md
sed -i '' "s/\[Grant Numbers\]/$YOUR_FUNDING/g" README.md
sed -i '' "s/\[Your Lab URL\]/$YOUR_LAB_URL/g" README.md
sed -i '' "s/yourusername/$YOUR_GITHUB_USERNAME/g" README.md

# 更新 LICENSE
echo "更新 LICENSE..."
sed -i '' "s/\[Your Name\/Institution\]/$YOUR_NAME, $YOUR_INSTITUTION/g" LICENSE

# 更新 data/README.md
echo "更新 data/README.md..."
sed -i '' "s/\[Authors\]/$YOUR_NAME/g" data/README.md
sed -i '' "s/data\.contact@email\.com/$YOUR_EMAIL/g" data/README.md
sed -i '' "s/yourusername/$YOUR_GITHUB_USERNAME/g" data/README.md

# 更新 PROJECT_STATUS.md
echo "更新 PROJECT_STATUS.md..."
sed -i '' "s/\[Your Name\]/$YOUR_NAME/g" PROJECT_STATUS.md
sed -i '' "s/email@institution\.edu/$YOUR_EMAIL/g" PROJECT_STATUS.md
sed -i '' "s/\[Your Lab URL\]/$YOUR_LAB_URL/g" PROJECT_STATUS.md
sed -i '' "s/yourusername/$YOUR_GITHUB_USERNAME/g" PROJECT_STATUS.md

echo ""
echo "✅ 个人信息更新完成！"
echo ""
echo "已更新的文件："
echo "  - README.md"
echo "  - LICENSE"
echo "  - data/README.md"
echo "  - PROJECT_STATUS.md"
echo ""
echo "备份文件已创建（.backup后缀）"
echo ""
echo "⚠️  请注意："
echo "1. 请手动检查更新后的文件是否正确"
echo "2. 如需恢复，可以使用备份文件"
echo "3. 建议在VS Code中打开文件确认"
echo ""
echo "下一步：执行 Git 命令上传到 GitHub"
echo "---------------------------------------------"
echo "cd /Users/apple/Desktop/hard_clam_kit/hard_clam_connectivity"
echo "git init"
echo "git add ."
echo 'git commit -m "Initial release: Hard clam connectivity analysis code"'
echo "# 然后在GitHub创建仓库，获取URL后执行："
echo "git remote add origin https://github.com/Wen77777777/hard_clam_connectivity.git"
echo "git branch -M main"
echo "git push -u origin main"
echo "---------------------------------------------"