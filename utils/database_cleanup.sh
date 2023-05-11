DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Cleaning FIRE database for ProjectID=[${PROJECT_ID}]  and using DATABASE_PREFIX=[${DATABASE_PREFIX}]"
python "${DIR}/database_cleanup.py"