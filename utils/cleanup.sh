DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR"/bq_cleanup.sh
"$DIR"/database_cleanup.sh
"$DIR"/upload_cleanup.sh
"$DIR"/forms_cleanup.sh
