#! /bin/bash
TO_DELETE=$1
if [ -z "$TO_DELETE" ]; then
  echo "GCS uri must be specified"
  exit
fi

echo "Cleaning pa-forms directory inside $TO_DELETE"
read -p "Are you sure you want to delete all forms inside  $TO_DELETE? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Cleaning Up then..."
  gsutil -m rm -a -r "${TO_DELETE}/**"
fi

