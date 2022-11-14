DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET

cd "${DIR}/terraform/environments/dev" || exit
terraform apply