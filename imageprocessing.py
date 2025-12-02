import streamlit as sl
import numpy as np
import time as time
from PIL import Image
import cv2
import matplotlib.pyplot as plt

sl.set_page_config(
    layout="wide",
    page_title="Image processing"    
)

add_selectbox = sl.sidebar.selectbox(
    'Select which data you require',
    ("image processing")
)

if add_selectbox == "image processing":
    tab1, tab2 = sl.tabs(["tab 1","tab 2"])
    a = tab1.camera_input("take a picture")
    if a is not None:
        with open("captured_image.jpg", "wb") as file:
            if file is not None:
                file.write(a.getbuffer())

    bar = tab2.progress(0)
    if a is not None:
        for i in range(101):
            bar.progress(i)
            time.sleep(0.02)
            if i == 100:
                if a is None:
                    sl.write("error loading an image")
                if a is not None:
                    image= Image.open(a)
                    imagearray = np.array(image)
                    grey_image = cv2.cvtColor(imagearray,cv2.COLOR_BGR2GRAY)
                    tab2.write("converting image to gray scale is completed")
                    tab2.image(grey_image)

                    image=cv2.imread("captured_image.jpg",cv2.IMREAD_GRAYSCALE)
                    scale_factor = 0.5
                    height,width = image.shape
                    new_height=int(height*scale_factor)
                    new_width = int(width*scale_factor)
                    image=cv2.resize(image,(new_width,new_height))
                    x_coords =[]
                    y_coord=[]
                    intensities=[]
                    for y in range(new_height):
                        for x in range(new_width):
                            if image[y,x]!=255:
                                x_coords.append(x)
                                y_coord.append(y)
                                intensities.append(image[y,x])
                    
                    if x_coords and y_coord:
                        fig, ax =plt.subplots()
                        scatter = ax.scatter(x_coords,y_coord,c=intensities,cmap="gray",s=0.5)
                        plt.colorbar(scatter,ax=ax,label="Intensity")
                        ax.set_xlabel('x_coords')
                        ax.set_ylabel('y_coord')
                        ax.set_title("graph of the image")
                        tab2.write("converting image to graph is completed")
                        tab2.pyplot(fig)

                    image=cv2.imread("captured_image.jpg",cv2.IMREAD_GRAYSCALE)
                    x_histogram = np.sum(image,axis=0)
                    y_histogram = np.sum(image,axis=1)
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    ax1.plot(x_histogram)
                    ax1.set_title('X Histogram (Sum of intensities across rows)')
                    ax1.set_xlabel('X Coordinate')
                    ax1.set_ylabel('Sum of Intensities')

                    ax2.plot(y_histogram)
                    ax2.set_title('Y Histogram (Sum of intensities across columns)')
                    ax2.set_xlabel('Y Coordinate')
                    ax2.set_ylabel('Sum of Intensities')

                    tab2.write("generating histogram of the image is completed")
                    tab2.pyplot(fig)
                    
                    image=cv2.imread("captured_image.jpg",cv2.IMREAD_GRAYSCALE)
                    x_intensity = np.sum(image, axis=0)  
                    y_intensity = np.sum(image, axis=1)
                    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
                    ax[0].bar(range(len(x_intensity)), x_intensity, color='gray')
                    ax[0].set_title('X Axis Bar Plot (Column Intensity)')
                    ax[0].set_xlabel('Column Index')
                    ax[0].set_ylabel('Sum of Intensities')
                    ax[1].bar(range(len(y_intensity)), y_intensity, color='gray')
                    ax[1].set_title('Y Axis Bar Plot (Row Intensity)')
                    ax[1].set_xlabel('Row Index')
                    ax[1].set_ylabel('Sum of Intensities')
                    tab2.write("Generating bar graph for the image is completed")
                    tab2.pyplot(fig)

                    image=cv2.imread("captured_image.jpg",cv2.IMREAD_GRAYSCALE)
                    x_intensity = np.sum(image, axis=0)
                    y_intensity = np.sum(image, axis=1)
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    ax1.plot(x_intensity, color='blue', label="Column Intensity")
                    ax1.set_title('X Axis Line Graph (Column Intensity)')
                    ax1.set_xlabel('Column Index')
                    ax1.set_ylabel('Sum of Intensities')
                    ax1.legend()
                    ax2.plot(y_intensity, color='red', label="Row Intensity")
                    ax2.set_title('Y Axis Line Graph (Row Intensity)')
                    ax2.set_xlabel('Row Index')
                    ax2.set_ylabel('Sum of Intensities')
                    ax2.legend()
                    tab2.write("Generating line graph for the image is completed")
                    tab2.pyplot(fig)