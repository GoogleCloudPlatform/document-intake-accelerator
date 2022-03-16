from wand.image import Image

# Read image using Image() function
with Image(filename="koala.jpeg") as img:
    # Generate noise image using spread() function
    img.noise("poisson", attenuate=0.9)
    img.save(filename="noisekoala.jpeg")


# Ref

# https://www.geeksforgeeks.org/python-noise-function-in-wand/#:~:text=Python%20%E2%80%93%20noise()%20function%20in%20Wand,-Last%20Updated%20%3A%2008&text=We%20can%20add%20noise%20to,gaussian