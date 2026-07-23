#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

export TMPDIR="$project_root/tmp"
export BOOK_VERSION="${BOOK_VERSION:-пробная редактируемая сборка}"
export BOOK_BUILD_TIME="${BOOK_BUILD_TIME:-$(date '+%d.%m.%Y %H:%M:%S %Z')}"

output_dir="$project_root/tmp/editable"
output_name="probability-statistics-for-it-entrepreneurs"
docx_path="$output_dir/$output_name.docx"
odt_path="$output_dir/$output_name.odt"
lo_profile="$(mktemp -d "$TMPDIR/libreoffice-export.XXXXXX")"

mkdir -p "$output_dir"

if ! command -v soffice >/dev/null 2>&1; then
  echo "LibreOffice не найден: команда soffice недоступна" >&2
  exit 1
fi

quarto render --profile editable,part --to docx

if [[ ! -s "$docx_path" ]]; then
  echo "DOCX не создан: $docx_path" >&2
  exit 1
fi

find "$output_dir" -maxdepth 1 -type f -name "$output_name.odt" -delete

soffice --headless \
  -env:UserInstallation="file://$lo_profile" \
  --convert-to odt \
  --outdir "$output_dir" \
  "$docx_path"

if [[ ! -s "$odt_path" ]]; then
  echo "ODT не создан: $odt_path" >&2
  exit 1
fi

printf 'Созданы:\n%s\n%s\n' "$docx_path" "$odt_path"
