# Fake news classification

The dataset used for our model is [r/Fakeddit](https://arxiv.org/abs/1911.03854) which contains both image and text
data.

#### IMPORTANT: In order to load the original `tsv` files as dataframes use `pd.read_csv('filepath', sep=`\t`)`.

# Notes that will help when writing the final report:

- `preprocessing.py`:
    - `findCorruptImages()`:
        - Because the images were downloaded through multiple sessions, every time I would end the session abruptly, the
          image being downloaded would become corrupt. Hence the need to delete those images.
    - `dropUnusedRows()`:
        - The dataset is huge (Roughly 1 million rows, which means roughly 1 million images). I didn't download all of
          them, so this function checks the `directory` of the images (`train`, `test`, etc.) and only keeps the rows
          of
          the csv files that contain the image `ids` found in the `directory`.
    - `removeDatasetBias()`:
        - The dataset that I ended up with after downloading the images, had a larger number of `False` images (not
          fake) than
          `True` (fake) images. So, this function removes the bias and makes the number of `0`s equal to the number
          of `1`s in the
          `2_way_label` column of the csv.
- `image_downloader.py`:
    - This script downloads the images of the dataset, it was taken from
      the [github repo](https://github.com/entitize/Fakeddit/blob/master/image_downloader.py) of the paper's authors. I
      modified it in order to search for already existing images and skip them, as well as to skip images when the
      server is not responding.
- `resnet.py`:
    - The implementation of the ResNet network, taken
      from [github](https://github.com/aladdinpersson/Machine-Learning-Collection/blob/master/ML/Pytorch/CNN_architectures/pytorch_resnet.py)
      and I added the 18 layer version.
- `dataset.py`:
    - Custom class to load the images and labels into tensors in order to train the model based
      on [pytorch documentation](https://pytorch.org/tutorials/beginner/data_loading_tutorial.html).
- `get_random_subset_of_dataset.py`:
    - The images I downloaded were still too many and the training took about 30 mins per epoch (sheesh), so I had to
      reduce the number of images even more. This is where this script comes in.
    - After running this, we need to run `preprocessing.py` again in order to remove dataset bias and make new csv files
      with only the necessary number of rows.
- `network.py`:
    - Here we compose the final model (woah). It's what they call "pantrema" in greece.
    - In the `transforms` the `Lambda` transforms are used because some images contained either < 3 channels
      or > 3 channels after their transformation to tensor, and our ResNet model takes 3-channel inputs.
    - I use `CrossEntropyLoss()` which is commonly used in binary classification problems, `SGD()` optimization,
      and `ReduceLROnPlateau()` with `patience = 2` optimization for the learning rate. The latter means that if the
      validation loss is not decreased for two consecutive epochs, the learning rate will be multiplied with $10^{-1}$.
    - [tqdm](https://tqdm.github.io/) is used to show a progress bar when training the network.