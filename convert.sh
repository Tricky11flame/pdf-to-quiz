#!/bin/bash

# Create output directory
mkdir -p ./text

# Iterate through all PDF files
for file in ./pdf/*.pdf; do
    # Get filename without path and extension
    filename=$(basename "$file" .pdf)
    
    echo "Processing: $filename"
    
    # Execute extraction
    pdftotext -layout -enc UTF-8 "$file" "./text/$filename.txt"
done