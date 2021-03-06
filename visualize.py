# Generate results from a trained model.

# Before starting visualization, make sure that correct model name is set in config.py

import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import os
from config import cfg
from data_factory import get_dataset
from net_factory import get_network
from torch.autograd import Variable

# setup checkpoint directory
out_dir = cfg.train.out_dir
if not os.path.exists(out_dir):
    raise ValueError('cannot find the directory and trained model')

# make a directory for image results
if not os.path.exists(os.path.join(out_dir, 'image_results')):
    os.makedirs(os.path.join(out_dir, 'image_results'))
else:
    print('overwriting results')

print('Configuration: \n', cfg) 

# dataloaders
cfg.train.shuffle = False
test_loader = get_dataset(dataset_name=cfg.data.name, mode = 'test')
print('Data loaders have been prepared!')

# network
af_plus = get_network('AF_plus')

# load pretrained model
if cfg.model.name == 'FDS':
    fds = get_network('FDS')
    fds.load_state_dict(torch.load(os.path.join(out_dir, 'fds_dict.pth')))
    af_plus.load_state_dict(torch.load(os.path.join('checkpoints', 'af_plus_dict.pth')))
    fds.eval()
else:
    af_plus.load_state_dict(torch.load(os.path.join(out_dir, 'model_dict.pth')))


af_plus.eval()    
print('Starting visualization...')



with torch.no_grad():
    ctr = 0
    for i, data in enumerate(test_loader, 0):
        if i>1:
            break
        source = data['source'].float().cuda()
        target = data['target'].float().cuda()
        vec = data['vec'].float().cuda()

        image_out, flow, _  = af_plus(source, vec)
        
        if cfg.model.name == 'FDS':
            image_out = fds(source, flow)
        
        source = source[:, :, :, 48:-48].permute(0,2,3,1).detach().cpu().numpy()
        target = target[:, :, :, 48:-48].permute(0,2,3,1).detach().cpu().numpy()
        image_out = image_out[:, :, :, 48:-48].permute(0,2,3,1).detach().cpu().numpy()

        plt.ioff()
        my_dpi = 300 
        
        for k in range(source.shape[0]):
                        
            plt.figure(figsize=(160 / my_dpi, 960 / my_dpi), dpi=8.0 * my_dpi)
            plt.imshow(source[k, :, :, :])
            plt.axis('off')
            fname1 = str(str(ctr) + '_source' + '.png')
            plt.savefig(os.path.join(out_dir, 'image_results', fname1), bbox_inches='tight', dpi=8.0*my_dpi, pad_inches=0.0)
            plt.close()

            plt.figure(figsize=(160 / my_dpi, 960 / my_dpi), dpi=8.0 * my_dpi)
            plt.imshow(target[k, :, :, :])
            plt.axis('off')
            fname1 = str(str(ctr) + '_target' + '.png')
            plt.savefig(os.path.join(out_dir, 'image_results', fname1), bbox_inches='tight', dpi=8.0*my_dpi, pad_inches=0.0)
            plt.close()

            plt.figure(figsize=(160 / my_dpi, 960 / my_dpi), dpi=8.0 * my_dpi)
            plt.axis('off')
            plt.imshow(image_out[k, :, :, :])
            fname1 = str(str(ctr) + '_output' + '.png')  # naming ans saving
            plt.savefig(os.path.join(out_dir, 'image_results', fname1), bbox_inches='tight', dpi=8.0*my_dpi, pad_inches=0.0)
            plt.close()
            
            plt.figure(dpi=150)
            plt.subplot(3, 1, 1)
            plt.imshow(source[k, :, :, :])
            plt.axis('off')
            plt.title('source')
            
            plt.subplot(3, 1, 2)
            plt.imshow(image_out[k, :, :, :])
            plt.axis('off')
            plt.title('AF++')
            
            plt.subplot(3, 1, 3)
            plt.imshow(target[k, :, :, :])
            plt.axis('off')
            plt.title('target')
            fname1 = str(str(ctr) + '_combined' + '.png')  # naming ans saving
            plt.savefig(os.path.join(out_dir, 'image_results', fname1), bbox_inches='tight', pad_inches=0.0)
            plt.close()
            
            ctr += 1


print('All done saving images')