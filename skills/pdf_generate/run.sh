#!/bin/bash

INPUT="$1"
OUTPUT="$2"

echo "📄 Converting $INPUT to $OUTPUT..."

npx ai-pdf-builder generate memo "$INPUT" -o "$OUTPUT"

open "$OUTPUT"

