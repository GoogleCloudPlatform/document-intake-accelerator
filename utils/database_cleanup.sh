DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Cleaning FIRE database for Project ${PROJECT_ID}  and using DATABASE_PREFIX=${DATABASE_PREFIX}"
python "${DIR}/utils/database_cleanup.py"