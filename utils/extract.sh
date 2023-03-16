#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR"/../SET
export DEBUG=true

# Make sure to pass remote URL

#python "$DIR"/extract.py -f gs://$PROJECT_ID/sample_data/bsc_demo/Package.pdf -c bsc_package_form
#python "$DIR"/extract.py -f gs://$PROJECT_ID/sample_data/bsc_demo/pa-form-1.pdf -c prior_auth_form
CONFIG_BUCKET=$CONFIG_BUCKET python "$DIR"/extract.py -f gs://$PROJECT_ID/sample_data/bsc_demo/bsc-dme-pa-form-1.pdf -c bsc_pa_form
