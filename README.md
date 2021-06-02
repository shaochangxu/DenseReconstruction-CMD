# DenseReconstruction-CMD

Fisrt use colmap to complete the sparse reconstruction
The result dir just as follows:

e.g. sparse output path: /home/hadoop/data/data/0529/
     image path: /home/hadoop/data/data/TEST/
     
dir structure
  ---/home/hadoop/data/data/0529/
     |---0
         |-------scene.mvs

Then use the script as follows:
   python fulldense.py  --scene  /home/hadoop/data/data/0529/0/scene.mvs         # scene.mvs path
                        --img    /home/hadoop/data/data/TEST/                    # img path
                        -o       /home/hadoop/data/data/0529/dense_output/       # output path
                        -w       /home/hadoop/data/data/0529/                    # sparse path           
                        --tmp    /home/hadoop/data/data/tmp/                     # tmp path to store the middle file
                        --kernel /home/hadoop/scx/cmd_version/Kernel/            # kernel dir to colmap openmvs kernel
                        --quality Low                                            # quality

Then the result:
  ---/home/hadoop/data/data/0529/
     |---dense_output                        # only exists on master
         |------fusedAll.ply
         |------scene_dense_all.mvs          # store the all dense points as mvs file, internal structure as sparse scene.mvs
         |------scene_modify.mvs             # empty mvs file store the dense structure
         |------mvs
                |-----scene_dense_*.mvs
     |------Colmap_In_*.                     # exits on each nodes
                |-------dense
                          |------fused.ply                    # points
                          |------fused.ply.vis                # visual information 
                          |------images
                          |------sparse
                          |------stereo
                                  |-------depth_maps
                                  |-------normal_maps
                                  |-------fusion.cfg           # controls the images to fused
                                  |-------patch-match.cfg      # controls the images to estimate
                                  
fusedAll.ply:

<img width="840" alt="截屏2021-05-30 下午4 38 15" src="https://user-images.githubusercontent.com/85155497/120426434-abd65200-c3a2-11eb-9302-cd2ab79e39ae.png">
