# Healthcare Prior Authorization Form Generator

Use this tool to generate Healthcare Prior Authorization forms with synthetic test data.

## 1. Generate fake data to CSV file

```
cd examples/pa_form_generator
```

Run the following to generate a CSV file with 5 rows of fake data. You can modify
the config JSON file to generate additional fields.

```
python generate_fake_data.py --config=form_data_config.json --output=./out/test.csv --num-rows=5
```

## 2. Generate image forms based on fake data

Run the following to generate form images based on the given CSV file. It will
generate a number of images based on the rows in CSV file.

```
python ../../generate_images.py --config=form_image_config.json --data=./out/test.csv --output-folder=./out
```
You will see the list of images generated in the output folder.
* Please note that it will overwrite any existing files with the same file names.
