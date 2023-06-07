#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
cd "${DIR}/../sql-scripts"

echo "============================ Showing Diagnoses =========================="
./run_query.sh diagnose 2>/dev/null
echo
echo "========================= Showing Patient Names  ========================"
./run_query.sh patient_names 2>/dev/null

echo
echo " ================= Showing Texas PA Forms Patient Data  ================="
./run_query.sh texas_forms 2>/dev/null

echo

echo "=================== Showing BSC PA Forms Patient Data =================="
./run_query.sh bsc_forms 2>/dev/null

echo
echo "====================== Showing Corrected Values ========================="
./run_query.sh corrected_values 2>/dev/null

cd "$PWD"