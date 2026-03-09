#!/bin/bash
# 快速重命名工具 - 按上传时间顺序自动分配

set -e

BASE_DIR="/Users/user/clawd/hr-recruitment/candidates/cambodia-finance"
SOURCE_DIR="/Users/user/.openclaw/media/inbound"

echo "📂 快速履历重命名工具"
echo "================================"
echo ""
echo "⚠️  假设：PDF 按上传时间顺序 = 前11位是 P0+P1+P2 候选人"
echo ""
echo "按 Enter 继续，或 Ctrl+C 取消..."
read

# 定义候选人顺序（按 P0→P1→P2）
declare -a CANDIDATES=(
    "P0:Soun-Mara"
    "P0:Ingrid-Ren"
    "P0:Malita-Hout"
    "P1:Chong-Chhe-Chhit"
    "P1:Mao-Veasna"
    "P1:Chanmolen-Chen"
    "P2:Nang-Y-Daly"
    "P2:Hor-Chhunly"
    "P2:Sona-Rath"
    "P2:SO-Panharath"
    "P2:Sann-Cheng"
)

# 获取按时间排序的 PDF 列表（最早的在前）
mapfile -t PDF_FILES < <(ls -t "$SOURCE_DIR"/file_6*.pdf | tail -r)

echo "找到 ${#PDF_FILES[@]} 个 PDF 档案"
echo ""

# 处理前 11 个（P0+P1+P2）
for i in "${!CANDIDATES[@]}"; do
    if [ $i -ge ${#PDF_FILES[@]} ]; then
        echo "⚠️  PDF 档案不足 $((i+1)) 个"
        break
    fi
    
    pdf_file="${PDF_FILES[$i]}"
    candidate_info="${CANDIDATES[$i]}"
    
    # 分离分类和姓名
    category=$(echo "$candidate_info" | cut -d: -f1)
    name=$(echo "$candidate_info" | cut -d: -f2)
    
    # 确定目标文件夹
    case "$category" in
        P0) target_dir="$BASE_DIR/P0-优先联系" ;;
        P1) target_dir="$BASE_DIR/P1-待确认" ;;
        P2) target_dir="$BASE_DIR/P2-备选" ;;
    esac
    
    # 添加编号
    num=$(printf "%02d" $((i+1)))
    new_name="${num}-${name}.pdf"
    target_file="$target_dir/$new_name"
    
    # 复制并重命名
    if cp "$pdf_file" "$target_file"; then
        echo "✅ $category/$new_name"
    else
        echo "❌ 失败: $(basename "$pdf_file")"
    fi
done

echo ""
echo "================================"
echo "✅ 前 11 位候选人已归档！"
echo ""
echo "⚠️  剩余 $((${#PDF_FILES[@]} - 11)) 个 PDF 归档到「其他-不适合」"
echo "   （需要手动确认姓名）"
echo ""

# 剩余档案归档到"其他"
other_dir="$BASE_DIR/其他-不适合"
mkdir -p "$other_dir"

for i in $(seq 11 $((${#PDF_FILES[@]} - 1))); do
    pdf_file="${PDF_FILES[$i]}"
    filename=$(basename "$pdf_file")
    
    # 保留原始档名，加上"其他-"前缀
    cp "$pdf_file" "$other_dir/待确认-$filename"
done

echo "✅ 剩余档案已复制到: $other_dir/"
echo ""
echo "📂 检查结果："
echo "   P0: $(ls -1 "$BASE_DIR/P0-优先联系"/*.pdf 2>/dev/null | wc -l | xargs) 个"
echo "   P1: $(ls -1 "$BASE_DIR/P1-待确认"/*.pdf 2>/dev/null | wc -l | xargs) 个"
echo "   P2: $(ls -1 "$BASE_DIR/P2-备选"/*.pdf 2>/dev/null | wc -l | xargs) 个"
echo "   其他: $(ls -1 "$BASE_DIR/其他-不适合"/*.pdf 2>/dev/null | wc -l | xargs) 个"
