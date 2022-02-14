from datetime import datetime
import cv2
import os
import random
import numpy as np
import skimage

# brightness
# contrast
# noise 
# shadowing effects
# random contrast and noise levels

def add_contrast_brightness(image_path, alpha=1, beta=0):

    if image_path.endswith(("png", "jpeg")):
        image = cv2.imread(image_path)

        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def generate_shadow_coordinates(imshape, no_of_shadows=1):
    vertices_list=[]
    for index in range(no_of_shadows):
        vertex=[]
        for dimensions in range(np.random.randint(4,15)): ## Dimensionality of the shadow polygon
            vertex.append((imshape[1]*np.random.uniform(),imshape[0]//5+imshape[0]*np.random.uniform()))
            vertices = np.array([vertex], dtype=np.int32) ## single shadow vertices
            vertices_list.append(vertices)
        return vertices_list ## List of shadow vertices    

def add_shadow(image_HLS, mask, vertices_list):
    for vertices in vertices_list:
        cv2.fillPoly(mask, vertices, 125) ## adding all shadow polygons on empty mask, single 255 denotes only red channel
        image_HLS[:,:,1][mask[:,:,0]==125] = image_HLS[:,:,1][mask[:,:,0]==125]*0.9  ## if red channel is hot, image's "Lightness" channel's brightness is lowered
        image_RGB = cv2.cvtColor(image_HLS,cv2.COLOR_HLS2RGB) ## Conversion to RGB
    return image_RGB


def add_noise(image):
    return skimage.util.random_noise(image, mode='gaussian')
    # row,col,ch= image.shape
    # mean = 0
    # var = 0.1
    # sigma = var**np.random.normal()
    # print(sigma)
    # gauss = np.random.normal(mean,sigma,(row,col,ch))
    # gauss = gauss.reshape(row,col,ch)
    # noisy = image + gauss
    # return noisy

if __name__ == "__main__":
    CONTRAST = 1
    SHADOW = 1
    NOISE = 1

    folder = "/users/sumitvaise/Downloads/DocAI/Dataset/Form_wise_images/Utility/"
    cb_out_folder = "/users/sumitvaise/Downloads/DocAI/Dataset/modified/Utility/contrast_brightness"
    shadow_folder = "/users/sumitvaise/Downloads/DocAI/Dataset/modified/Utility/Shadowed"
    noise_folder = "/users/sumitvaise/Downloads/DocAI/Dataset/modified/Utility/Noise"

    inp_imgs = os.listdir(folder)
    random.shuffle(inp_imgs)
    c = 0
    for img in inp_imgs:   
        
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        if img.endswith(('png', 'jpeg')):
            img_name, extn = os.path.splitext(img)
            

            if c < 301:
                c+=1
                if CONTRAST and c <50:
                    beta = random.randint(0,100)
                    alpha = random.uniform(0.5,2.5)
                    bright = add_contrast_brightness(os.path.join(folder, img), alpha=1, beta=beta)
                    contrast = add_contrast_brightness(os.path.join(folder, img), alpha=alpha, beta=0)

                    b_img_name =  img_name + '_' + timestamp + '_b' + str(beta) + extn
                    cb_img_path = os.path.join(cb_out_folder, b_img_name)
                    cv2.imwrite(cb_img_path, bright)

                    c_img_name =  img_name + '_' + timestamp + '_a' + str(alpha) + extn
                    cb_img_path = os.path.join(cb_out_folder, c_img_name)
                    cv2.imwrite(cb_img_path, contrast)
                    print(c_img_name, b_img_name,c)

                if SHADOW and  50 < c < 151:
                    shdw_mat_img = cv2.imread(os.path.join(folder, img))
                    image_HLS = cv2.cvtColor(shdw_mat_img,cv2.COLOR_RGB2HLS) ## Conversion to HLS
                    mask = np.zeros_like(shdw_mat_img)
                    imshape = shdw_mat_img.shape
                    vertices_list= generate_shadow_coordinates(imshape, 1)

                    shadowed_img = add_shadow(image_HLS, mask, vertices_list)
                    shadow_img_name =  img_name + '_' + timestamp + '_shadowed_' + extn
                    shadow_img_path = os.path.join(shadow_folder, shadow_img_name)
                    cv2.imwrite(shadow_img_path, shadowed_img)
                    print(shadow_img_name,c)

                if NOISE and 151 < c < 252 :
                    noise_mat_img = skimage.io.imread(os.path.join(folder, img))/255.0  
                    noisy = add_noise(noise_mat_img)             
                    noise_img_name =  img_name + '_' + timestamp + '_noisy' + extn
                    nout_img = os.path.join(noise_folder, noise_img_name)
                    skimage.io.imsave(nout_img, noisy)
                    # cv2.imwrite(nout_img, noisy)
                    print(noise_img_name,c)
