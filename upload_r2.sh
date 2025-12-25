#!/bin/bash
# R2 업로드 스크립트 (wrangler 사용)

cd "$(dirname "$0")/dist"

echo "======================================"
echo "R2 업로드 시작"
echo "======================================"

# metadata.json 업로드
echo "📋 Uploading metadata.json..."
npx wrangler r2 object put kmo-geometry/metadata.json --file=metadata.json > /dev/null 2>&1
echo "✅ metadata.json uploaded"

# problems/*.json 업로드
echo ""
echo "📄 Uploading problem JSON files..."
count=0
total=$(ls problems/*.json | wc -l | tr -d ' ')
for file in problems/*.json; do
  filename=$(basename "$file")
  npx wrangler r2 object put "kmo-geometry/problems/$filename" --file="$file" > /dev/null 2>&1
  count=$((count + 1))
  if [ $((count % 50)) -eq 0 ]; then
    echo "  Progress: $count/$total files uploaded..."
  fi
done
echo "✅ $total problem JSON files uploaded"

# svg/*.svg 업로드
echo ""
echo "🎨 Uploading SVG files..."
svg_count=0
if [ -d "svg" ]; then
  svg_total=$(ls svg/*.svg 2>/dev/null | wc -l | tr -d ' ')
  for file in svg/*.svg; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    npx wrangler r2 object put "kmo-geometry/svg/$filename" --file="$file" > /dev/null 2>&1
    svg_count=$((svg_count + 1))
  done
  echo "✅ $svg_count SVG files uploaded"
fi

echo ""
echo "======================================"
echo "✅ 업로드 완료!"
echo "======================================"
