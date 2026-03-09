#!/bin/bash
# 履历自动重命名与归档工具
# 用法：./auto-rename-resumes.sh

set -e

BASE_DIR="/Users/user/clawd/hr-recruitment/candidates/cambodia-finance"
SOURCE_DIR="/Users/user/.openclaw/media/inbound"
MAPPING_FILE="$BASE_DIR/候选人档案映射.txt"

echo "📂 履历自动重命名与归档工具"
echo "================================"
echo ""

if [ ! -f "$MAPPING_FILE" ]; then
    echo "❌ 错误：找不到映射文件 $MAPPING_FILE"
    echo "请先填写候选人姓名映射表"
    exit 1
fi

# 统计
total=0
success=0
skipped=0

echo "🔄 开始处理..."
echo ""

# 读取映射文件并处理
while IFS='|' read -r original_name candidate_name category; do
    # 跳过注释和空行
    [[ "$original_name" =~ ^#.*$ ]] && continue
    [[ -z "$original_name" ]] && continue
    
    # 清理空格
    original_name=$(echo "$original_name" | xargs)
    candidate_name=$(echo "$candidate_name" | xargs)
    category=$(echo "$category" | xargs)
    
    # 跳过待填写的项目
    if [[ "$candidate_name" == "[待填写]" ]]; then
        echo "⏭️  跳过 $original_name（待填写姓名）"
        ((skipped++))
        continue
    fi
    
    ((total++))
    
    # 原始档案路径
    source_file="$SOURCE_DIR/$original_name"
    
    if [ ! -f "$source_file" ]; then
        echo "⚠️  找不到档案: $original_name"
        continue
    fi
    
    # 生成新档名（空格转连字号）
    new_name=$(echo "$candidate_name" | sed 's/ /-/g').pdf
    
    # 确定目标文件夹
    case "$category" in
        P0)
            target_dir="$BASE_DIR/P0-优先联系"
            ;;
        P1)
            target_dir="$BASE_DIR/P1-待确认"
            ;;
        P2)
            target_dir="$BASE_DIR/P2-备选"
            ;;
        其他|OTHER)
            target_dir="$BASE_DIR/其他-不适合"
            new_name="其他-$new_name"
            ;;
        *)
            echo "⚠️  未知分类: $category ($original_name)"
            continue
            ;;
    esac
    
    # 确保目标文件夹存在
    mkdir -p "$target_dir"
    
    # 复制并重命名
    target_file="$target_dir/$new_name"
    
    if cp "$source_file" "$target_file"; then
        echo "✅ $candidate_name → $category/$new_name"
        ((success++))
    else
        echo "❌ 失败: $candidate_name"
    fi
    
done < "$MAPPING_FILE"

echo ""
echo "================================"
echo "✅ 处理完成！"
echo "   总计: $total 个"
echo "   成功: $success 个"
echo "   跳过: $skipped 个（待填写姓名）"
echo "================================"
echo ""
echo "📂 档案位置："
echo "   P0: $BASE_DIR/P0-优先联系/"
echo "   P1: $BASE_DIR/P1-待确认/"
echo "   P2: $BASE_DIR/P2-备选/"
echo "   其他: $BASE_DIR/其他-不适合/"
