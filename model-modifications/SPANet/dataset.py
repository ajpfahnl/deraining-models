from pathlib import Path
import cv2
import numpy as np
from numpy.random import RandomState
from torch.utils.data import Dataset
from randomcrop import RandomRotation,RandomResizedCrop,RandomHorizontallyFlip,RandomVerticallyFlip
import PIL.Image as Image

class TrainValDataset(Dataset):
    def __init__(self, name):
        super().__init__()
        self.dataset = name
        self.mat_files = open(self.dataset,'r').readlines()
        self.file_num = len(self.mat_files)
        self.rc = RandomResizedCrop(256)

    def __len__(self):
        return self.file_num * 100

    def __getitem__(self, idx):
        file_name = self.mat_files[idx % self.file_num]
        gt_file = file_name.split(' ')[1][:-1]
        img_file = file_name.split(' ')[0]

        O = cv2.imread(img_file)
        B = cv2.imread(gt_file)

        O = Image.fromarray(O)
        B = Image.fromarray(B)

        O,B = self.rc(O,B)
        O,B = np.array(O),np.array(B)

        M = np.clip((O-B).sum(axis=2),0,1).astype(np.float32)
        O = np.transpose(O.astype(np.float32) / 255, (2, 0, 1))
        B = np.transpose(B.astype(np.float32) / 255, (2, 0, 1)) 

        sample = {'O': O, 'B': B,'M':M}

        return sample



class TestDataset(Dataset):
    def __init__(self, dir: Path, nogt=True):
        '''
        Assumes `dir` has structure:
            dir
              |- rainy
              |- clean (not necessary for nogt)
        '''
        super().__init__()
        self.nogt = nogt
        self.rand_state = RandomState(66)
        self.root_dir = dir
        self.file_num = 0
        self.mat_files = []
        for img_path in sorted((dir / "rainy").glob('*')):
            img = cv2.imread(str(img_path), 1)
            if isinstance(img, np.ndarray):
                self.file_num += 1
                self.mat_files.append(img_path)
        
        self.mat_files_gt = []
        self.gtcount = 0
        if not nogt:
            for img_path in sorted((dir / "clean").glob('*')):
                img = cv2.imread(str(img_path), 1)
                if isinstance(img, np.ndarray):
                    self.mat_files_gt.append(img_path)
                    self.gtcount += 1
            if self.gtcount != self.file_num:
                print('[ERROR] rainy and ground truth file counts don\'t match')
                exit(1)
        print(f'Test dataset initialized with {self.file_num} rainy and {self.gtcount} GTs.')
        for mf, mfgt in zip(self.mat_files, self.mat_files_gt):
            print(f'\t{mf}\t{mfgt}')
        
    def __len__(self):
        return self.file_num

    def __getitem__(self, idx):
        rainy_fname = self.mat_files[idx % self.file_num]
        O = cv2.imread(str(rainy_fname), 1)
        O = np.transpose(O, (2, 0, 1)).astype(np.float32) / 255.0 
        
        if self.nogt:
            B = None
        else:
            gt_fname = self.mat_files_gt[idx % self.file_num]
            B = cv2.imread(str(gt_fname), 1)
            B = np.transpose(B, (2, 0, 1)).astype(np.float32) / 255.0 


        sample = {'O': O,'B':B,'M':O}

        return sample
