#!/usr/bin/env bash
set -euo pipefail

#==========================
# Default installation path (global if root)
#==========================
if [ "${UID}" -eq 0 ]; then
  DEST_DIR="/usr/share/icons"
else
  DEST_DIR="${HOME}/.local/share/icons"
fi

# Source directory = script location
readonly SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

readonly DEFAULT_NAME="Nothing"

#==========================
# Help text
#==========================
usage() {
  cat << EOF
Usage: $0 [OPTION]

OPTIONS:
  -d, --dest    Specify theme destination directory (Default: $DEST_DIR)
  -n, --name    Specify theme name (Default: $DEFAULT_NAME)
  -r, --remove  Remove the theme
  -h, --help    Show this help
EOF
}

#==========================
# Utilities
#==========================
die() { echo "ERROR: $*" >&2; exit 1; }

install_file() { # mode src dest
  install -m"$1" "$2" "$3"
}

ensure_dir() {
  install -d "$1"
}

safe_rm_dir() {
  local d="$1"
  if [ -d "$d" ] || [ -L "$d" ]; then
    rm -rf --one-file-system "$d"
  fi
}

# Create a relative symlink (replace if exists)
rel_link() {
  local target="$1"
  local linkpath="$2"
  safe_rm_dir "$linkpath"
  ln -sr "$target" "$linkpath"
}

# Merge directory contents (overwrite on conflict)
merge_copy() {
  local dir_src="$1"
  local dir_dst="$2"
  [ -d "$dir_src" ] || return 0
  ensure_dir "$dir_dst"
  cp -rT "$dir_src" "$dir_dst" 2>/dev/null || cp -r "$dir_src/." "$dir_dst/"
}

#==========================
# Shared base (hidden dir, not exposed as a theme)
#==========================
SHARED_BASE=""

init_shared_name() {
  SHARED_BASE="${DEST_DIR}/.${NAME}-base"
}

build_shared_base() {
  safe_rm_dir "${SHARED_BASE}"
  echo "Preparing shared base: ${SHARED_BASE}"
  ensure_dir "${SHARED_BASE}"
  for d in 16 22 24 32 256 scalable symbolic; do
    merge_copy "${SRC_DIR}/src/${d}" "${SHARED_BASE}/${d}"
  done
  for d in 16 22 24 32 256 scalable symbolic; do
    merge_copy "${SRC_DIR}/links/${d}" "${SHARED_BASE}/${d}"
  done
}

#==========================
# Install theme
#==========================
install_theme() {
  local THEME_DIR="${DEST_DIR}/${NAME}"
  local TMP_DIR="${THEME_DIR}.tmp.$$"

  safe_rm_dir "${THEME_DIR}.tmp."* 2>/dev/null || true
  ensure_dir "${TMP_DIR}"

  echo "Installing '${NAME}'..."

  install_file 644 "${SRC_DIR}/src/index.theme" "${TMP_DIR}/index.theme"
  sed -i "s/%NAME%/${NAME}/g" "${TMP_DIR}/index.theme"

  for d in 16 22 24 32 256 symbolic; do
    [ -d "${SHARED_BASE}/${d}" ] && rel_link "${SHARED_BASE}/${d}" "${TMP_DIR}/${d}"
  done
  # Use a real directory (not a symlink) for scalable so that GTK's icon lookup
  # and gtk-update-icon-cache can traverse it without symlink-following issues
  # (relevant for snap-sandboxed apps like Firefox on Ubuntu).
  merge_copy "${SHARED_BASE}/scalable" "${TMP_DIR}/scalable"

  for mult in 2 3; do
    rel_link "${TMP_DIR}/16"       "${TMP_DIR}/16@${mult}x"      2>/dev/null || true
    rel_link "${TMP_DIR}/22"       "${TMP_DIR}/22@${mult}x"      2>/dev/null || true
    rel_link "${TMP_DIR}/24"       "${TMP_DIR}/24@${mult}x"      2>/dev/null || true
    rel_link "${TMP_DIR}/32"       "${TMP_DIR}/32@${mult}x"      2>/dev/null || true
    rel_link "${TMP_DIR}/256"      "${TMP_DIR}/256@${mult}x"     2>/dev/null || true
    rel_link "${TMP_DIR}/scalable" "${TMP_DIR}/scalable@${mult}x"
  done

  safe_rm_dir "${THEME_DIR}"
  mv "${TMP_DIR}" "${THEME_DIR}"

  gtk-update-icon-cache -f "${THEME_DIR}" >/dev/null 2>&1 || true
}

#==========================
# Argument parsing
#==========================
NAME=""
REMOVE=0

while [ $# -gt 0 ]; do
  case "$1" in
    -d|--dest)   [ $# -ge 2 ] || die "Missing argument for $1"; DEST_DIR="$2"; shift ;;
    -n|--name)   [ $# -ge 2 ] || die "Missing argument for $1"; NAME="$2"; shift ;;
    -r|--remove) REMOVE=1 ;;
    -h|--help)   usage; exit 0 ;;
    *)           die "Unrecognized option '$1'. Try '$0 --help'." ;;
  esac
  shift
done

: "${NAME:="${DEFAULT_NAME}"}"

#==========================
# Remove
#==========================
if [ "$REMOVE" -eq 1 ]; then
  echo "Removing ${DEST_DIR}/${NAME} ..."
  safe_rm_dir "${DEST_DIR}/${NAME}"
  safe_rm_dir "${DEST_DIR}/.${NAME}-base"
  echo "Done."
  exit 0
fi

#==========================
# Install
#==========================
ensure_dir "${DEST_DIR}"
init_shared_name
build_shared_base
install_theme

echo "Done."
