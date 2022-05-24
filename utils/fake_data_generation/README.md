# Benefits Fake Data Generator

## Getting Started

Install python dependencies.

```
cd utils/fake_data_generator
pip install -r requirements.txt
```

## Generate fake data to CSV file

Run the following to generate a CSV file with 20 rows of fake data. You can modify
the config JSON file to generate additional fields.

```
python generate_data.py --config=configs/sample_data_config.json --output=.tmp/test.csv --num-rows=20
```

## Generate image forms based on fake data

Run the following to generate form images based on the given CSV file. It will
generate a number of images based on the rows in CSV file.

```
python generate_images.py --config=configs/sample_image_config.json --data=.tmp/test.csv --output-folder=.tmp
```

* Please note that it will override any existing files with the same file names.

You will see the list of images generated in the output folder.

### Image generation config

TBD
