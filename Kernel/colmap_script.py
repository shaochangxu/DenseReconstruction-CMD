import subprocess
import argparse
import os
from time import *

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_path", type=str)
parser.add_argument("--scene_path", type=str)
parser.add_argument("--pair_file", type=str)
parser.add_argument("--kernel_path", type=str)
parser.add_argument("--img_path", type=str)
parser.add_argument("--resolution", type=str)
parser.add_argument("--task_id", type=str)
parser.add_argument("--quality", type=str)
args = parser.parse_args()

dataset_path = args.dataset_path
scene_path = args.scene_path
pair_file_path = args.pair_file
kernel_path = args.kernel_path
img_path = args.img_path

resolution = args.resolution

task_id = args.task_id

fast_colmap_exe_path = kernel_path + "/acmh/colmap/build/src/exe/colmap "
colmap_exe_path = kernel_path + "/colmap/build/src/exe/colmap "

quality = args.quality

######################################################## Dense Reconstruction Start ##################################################################################
begin_time = time()
os.system(kernel_path + "/openMVS_dis_build/bin/InterfaceCOLMAP" + " -i " + dataset_path +  "../Densify_temp_" + str(task_id) + "/scene.mvs" + " -o " + dataset_path + " --archive-type 1" + " -w " + img_path)

os.popen("mkdir " + dataset_path + "/dense")

os.popen("cp -r " + dataset_path + "/stereo " + dataset_path + "/dense ")
os.popen("cp -r " + dataset_path + "/sparse " + dataset_path + "/dense ")

os.popen("mkdir -p " + dataset_path + "/dense/stereo/depth_maps/")
os.popen("mkdir -p " + dataset_path + "/dense/stereo/normal_maps/")

os.popen("ln -sf " + img_path + " "+ dataset_path + "/dense/images")

os.system("python " + kernel_path + "/modify_cfg.py --pair_file " + pair_file_path + " --cfg_dir " + dataset_path + "/dense/stereo")

if quality == 'Low':
	os.system(fast_colmap_exe_path + "patch_match_stereo" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --PatchMatchStereo.max_image_size 1000" + " --PatchMatchStereo.window_radius 4 --PatchMatchStereo.window_step 2 --PatchMatchStereo.num_samples 7 --PatchMatchStereo.num_iterations 3 --PatchMatchStereo.geom_consistency false ")
	os.system(colmap_exe_path + "stereo_fusion" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --output_path " + dataset_path + "/dense/fused.ply" + " --input_type photometric --StereoFusion.check_num_images 25 --StereoFusion.max_image_size 1000")
elif quality == 'Medium':
	os.system(colmap_exe_path + "patch_match_stereo" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --PatchMatchStereo.max_image_size 1600" + " --PatchMatchStereo.window_radius 4 --PatchMatchStereo.window_step 2 --PatchMatchStereo.num_samples 10 --PatchMatchStereo.num_iterations 5 --PatchMatchStereo.geom_consistency false ")
	os.system(colmap_exe_path + "stereo_fusion" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --output_path " + dataset_path + "/dense/fused.ply" + "  --input_type photometric --StereoFusion.check_num_images 33 --StereoFusion.max_image_size 1600")
elif quality == 'High':
	os.system(colmap_exe_path + "patch_match_stereo" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --PatchMatchStereo.max_image_size 2400")
	os.system(colmap_exe_path + "stereo_fusion" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --output_path " + dataset_path + "/dense/fused.ply" + "--StereoFusion.max_image_size 2400")
elif quality == 'Extreme':
	os.system(colmap_exe_path + "patch_match_stereo" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP ")
	os.system(colmap_exe_path + "stereo_fusion" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --output_path " + dataset_path + "/dense/fused.ply" + " --StereoFusion.max_image_size 2000")
else:
	os.system(colmap_exe_path + "patch_match_stereo" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --PatchMatchStereo.max_image_size " + resolution + " --PatchMatchStereo.window_radius 4 --PatchMatchStereo.window_step 2 --PatchMatchStereo.num_samples 7 --PatchMatchStereo.num_iterations 3 --PatchMatchStereo.geom_consistency false ")
	os.system(colmap_exe_path + "stereo_fusion" + " --workspace_path " + dataset_path +  "/dense" + " --workspace_format COLMAP " + " --output_path " + dataset_path + "/dense/fused.ply" + " --input_type photometric --StereoFusion.check_num_images 25 --StereoFusion.max_image_size " + resolution)

os.system(kernel_path + "/openMVS_dis_build/bin/InterfaceCOLMAP"  + " -i " + dataset_path + "/dense" + " -o " + scene_path + " --image-folder " + img_path + " --archive-type 1" + " -w " + img_path)

end_time = time()
run_time = end_time - begin_time
print("dense reconstruction finished, run time is %0.2f s\n"%run_time)
