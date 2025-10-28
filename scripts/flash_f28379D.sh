#!/bin/bash
# flash_f28379D.sh
#
# Flash firmware to LaunchXL-F28379D using TI DSLite
#
# Usage:
#   ./flash_f28379D.sh [path/to/program.out] [optional_ccxml_path] [optional_ccs_dslite_path]
#
# If no arguments are given, defaults are used:
#   - Firmware: ../C2000_ws/Matlab/golfcart_model.out
#   - CCXML:    /usr/local/MATLAB/R2025b/toolbox/c2b/tic2000/CCS_Config/f28379D.ccxml
#   - DSLite:   /opt/ti/ccs2001/ccs/ccs_base/DebugServer/bin/DSLite
#
# Requires: LaunchXL-F28379D connected via onboard XDS100v2 or XDS110

set -euo pipefail

########################################
# Defaults
########################################
CCS_DSLITE_DEFAULT="/opt/ti/ccs2001/ccs/ccs_base/DebugServer/bin/DSLite"
CCXML_DEFAULT="/usr/local/MATLAB/R2025b/toolbox/c2b/tic2000/CCS_Config/f28379D.ccxml"
DEFAULT_OUT="../C2000_ws/Matlab/golfcart_model.out"

########################################
# Argument parsing
########################################
FW="${1:-$DEFAULT_OUT}"
CCXML="${2:-$CCXML_DEFAULT}"
CCS_DSLITE="${3:-$CCS_DSLITE_DEFAULT}"

########################################
# Color helpers
########################################
red()   { echo -e "\033[1;31m$*\033[0m"; }
green() { echo -e "\033[1;32m$*\033[0m"; }
yellow(){ echo -e "\033[1;33m$*\033[0m"; }

########################################
# Sanity checks
########################################
[ -x "$CCS_DSLITE" ] || { red "Error: DSLite not found at $CCS_DSLITE"; exit 1; }
[ -f "$CCXML" ] || { red "Error: CCXML config not found at $CCXML"; exit 1; }
[ -f "$FW" ] || { red "Error: Firmware image not found at $FW"; exit 1; }

########################################
# Flash
########################################
echo "------------------------------------------------------------"
echo "[INFO] LaunchXL-F28379D Flash Utility"
echo "------------------------------------------------------------"
echo "[INFO] Using:"
echo "   Firmware : $FW"
echo "   CCXML    : $CCXML"
echo "   DSLite   : $CCS_DSLITE"
echo

yellow "[WARN] Ensure the board is connected and powered"
yellow "[WARN] Close CCS or MATLAB if they are running"
echo

set +e
"$CCS_DSLITE" load -c "$CCXML" "$FW"
status=$?
set -e

if [ $status -eq 0 ]; then
    green "[OK] Flash complete!"
else
    red "[ERR] Flash failed (exit code $status)"
    exit $status
fi
