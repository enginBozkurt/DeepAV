import numpy as np
#import copy
from nuscenes.nuscenes import NuScenes
nusc = NuScenes(version='v1.0-mini', dataroot='D:/mini', verbose=True)
import pickle

f = open('C:/TrafficPredict/data/trajectories.cpkl', "rb")
raw_data = pickle.load(f)
f.close()

annodict = {
  "rotation": [],
  "size": [],
  "translation": [],
  "name": []
}
trash = []
data = []
instances = []
loglist = []
#my_scene = level5data.scene[0]
for my_scene in nusc.scene:
    trash=[] #empty trash bc instances are not kept across scenes
    
    log = nusc.get('log', my_scene['log_token'])
    loglist.append(log['location'])
    if (log['location'] != 'singapore-hollandvillage'):
        if (log['location'] == 'singapore-onenorth'):
            contextnum = 1
        if (log['location'] == 'boston-seaport'):
            contextnum = 2
        if (log['location'] == 'singapore-queenstown'):
            contextnum = 3
        
        firstsampletoken = my_scene["first_sample_token"]
        samp = nusc.get('sample', firstsampletoken)
        nextexists=True
        scenelist = []
        while (nextexists):
            samprow = np.array([0,0,0,0], dtype='float64').reshape((1,4))
            
            for ann in samp['anns']:
                anno = nusc.get('sample_annotation', ann)
                #vehicle or pedestrian
                instoken = anno['instance_token']
                if instoken not in instances:
                    instances.append(instoken)
                if 'vehicle' in anno['category_name']:
                    pedid = instances.index(instoken)+1
                    annadd = np.array([pedid, anno['translation'][0], anno['translation'][1], contextnum], dtype='float64').reshape((1,4))
                    samprow = np.concatenate((samprow, annadd))
            samprow = samprow[1:]
            samprow.sort(axis=0)
            scenelist.append(samprow)
            #print('tick')
            
            if (samp['next'] == ""):
                print('reached end')
                nextexists=False
            else:
                samp = nusc.get('sample', samp['next'])
        data.append(scenelist)

min_position_x = 1000
max_position_x = -1000
min_position_y = 1000
max_position_y = -1000

for scene in data:
    for sample in scene:
        min_position_x = min(min_position_x, min(sample[:, 1]))
        max_position_x = max(max_position_x, max(sample[:, 1]))
        min_position_y = min(min_position_y, min(sample[:, 2]))
        max_position_y = max(max_position_y, max(sample[:, 2]))
for scene in data:
    for sample in scene:
        sample[:, 1] = (
            (sample[:, 1] - min_position_x) / (max_position_x - min_position_x)
        ) * 2 - 1
        sample[:, 2] = (
            (sample[:, 2] - min_position_y) / (max_position_y - min_position_y)
        ) * 2 - 1

np.random.shuffle(data)
limit = int(len(data)/2)

raw=[]
raw.append([])
raw.append([])
raw[0]=data[0:limit]
raw[1]=data[limit:]

pickle.dump( raw, open( "data.cpkl", "wb" ) )


# =============================================================================
# all_frame_data = []
# # Validation frame data
# valid_frame_data = []
# # frameList_data would be a list of lists corresponding to each dataset
# # Each list would contain the frameIds of all the frames in the dataset
# frameList_data = []
# # numPeds_data would be a list of lists corresponding to each dataset
# # Ech list would contain the number of pedestrians in each frame in the dataset
# numPeds_data = []
# # Index of the current dataset
# dataset_index = 0
# 
# # Frame IDs of the frames in the current dataset
# frameList = np.unique(data[:, 0]).tolist()
# numFrames = len(frameList)
# # Add the list of frameIDs to the frameList_data
# frameList_data.append(frameList)
# # Initialize the list of numPeds for the current dataset
# numPeds_data.append([])
# # Initialize the list of numpy arrays for the current dataset
# all_frame_data.append([])
# # Initialize the list of numpy arrays for the current dataset
# valid_frame_data.append([])
# 
# skip = 1
# 
# for ind, frame in enumerate(frameList):
# 
#     ## NOTE CHANGE
#     if ind % skip != 0:
#         # Skip every n frames
#         continue
# 
#     # Extract all pedestrians in current frame
#     pedsInFrame = data[data[:, 0] == frame, :]
# 
#     # Extract peds list
#     pedsList = pedsInFrame[:, 1].tolist()
# 
#     # Add number of peds in the current frame to the stored data
#     numPeds_data[dataset_index].append(len(pedsList))
# 
#     # Initialize the row of the numpy array
#     pedsWithPos = []
#     # For each ped in the current frame
#     for ped in pedsList:
#         # Extract their x and y positions
#         current_x = pedsInFrame[pedsInFrame[:, 1] == ped, 3][0]
#         current_y = pedsInFrame[pedsInFrame[:, 1] == ped, 4][0]
#         current_type = self.class_objtype(
#             int(pedsInFrame[pedsInFrame[:, 1] == ped, 2][0])
#         )
#         # print('current_type    {}'.format(current_type))
#         # Add their pedID, x, y to the row of the numpy array
#         pedsWithPos.append([ped, current_x, current_y, current_type])
# 
#     if (ind > numFrames * self.val_fraction) or (self.infer):
#         # At inference time, no validation data
#         # Add the details of all the peds in the current frame to all_frame_data
#         all_frame_data[dataset_index].append(
#             np.array(pedsWithPos)
#         )  # different frame (may) have diffenent number person
#     else:
#         valid_frame_data[dataset_index].append(np.array(pedsWithPos))
# 
#     dataset_index += 1
# =============================================================================