
count=10
dest="gs://${PROJECT_ID}-pa-forms/demo"
while getopts f:c:d: flag
do
    case "${flag}" in
        f) form=${OPTARG};;
        c) count=${OPTARG};;
        d) dest=${OPTARG};;
        *);;
    esac
done

if [ -z "$form" ]; then
  echo "Form to copy must be provided."
  echo "Usage: copy_form.sh -f <form_to_copy.pdf> [-c <count>] [-d <dest>]"
  exit
fi

x=0

echo "Copying $form form to $dest $count times"

while [ $x -lt $(( $count - 1)) ]
do
   x=$(( $x + 1 ))
   #basename $form .pdf
   f="$(basename -- $form .pdf)"
   new_form=" ${f}_${x}.pdf"
   echo "Copying ${new_form} to $dest"
   gsutil cp "$form" "$dest/$new_form"
done