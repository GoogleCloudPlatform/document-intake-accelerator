TO_DELETE=gs://${PROJECT_ID}-pa-forms
echo "Cleaning pa-forms directory inside $TO_DELETE"
read -p "Are you sure you want to delete all forms inside  $TO_DELETE? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Cleaning Up then..."
  gsutil -m rm -a -r "${TO_DELETE}/**"
fi

