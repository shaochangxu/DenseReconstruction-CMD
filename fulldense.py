import datetime
import os
import numpy
import subprocess
import time
import argparse
import signal

import importlib, sys
importlib.reload(sys)
#sys.setdefaultencoding("utf-8")

# input: scene.mvs images
# output: ply scene_modified.mvs

# python fulldense.py --scene  /home/hadoop/data/data/0529/0/scene.mvs -o /home/hadoop/data/data/0529/dense_output/ -w /home/hadoop/data/data/0529/ --img /home/hadoop/data/data/TEST/ --tmp /home/hadoop/data/data/tmp/ --kernel /home/hadoop/scx/cmd_version/cmd_version/Kernel/ --quality Low


#################################################################Preprocess#######################################################################
begin_time = time.time()

parser = argparse.ArgumentParser()
# scene.mvs path
parser.add_argument("--scene", type=str)
# output path
parser.add_argument("-o", type=str)
# workpath
parser.add_argument("-w", type=str)
# images path
parser.add_argument("--img", type=str)
# 中间文件的文件夹
parser.add_argument("--tmp", type=str)

parser.add_argument("-r", default = '2000', type=str)
# kernel path
parser.add_argument("--kernel", type=str) #point to kernel dir
parser.add_argument("--quality", default='Self_Defined', type=str, choices=['Low', 'Medium', 'High', 'Extreme', 'Self_Defined'])
args = parser.parse_args()


#################################### we can modify ##############################
nParts = 21
execNum = 6
# 每个节点几个任务, len = exeNum
task_num_list = [6,3,3,3,3,3]
#################################################################################



# 每个任务由哪个节点完成 len = nParts
task_exeSlave = []
slave_id = 0

quality = args.quality
resolution = args.r
##original scene and images path
#basepath: "/home/hadoop/data/data/0423_SF/"
basepath = args.w
scenepath = args.scene
tmppath = args.tmp
imgpath = args.img
outputdir = args.o
kernel_path = args.kernel

sleep_time = 0.1

# 开始分配
for i in range(0, execNum):
	exe_num_each_nodes = task_num_list[i]
	for j in range(0, exe_num_each_nodes):
		task_exeSlave.append(slave_id)
	slave_id = slave_id + 1



#input and output path
inputpaths = [] # scene.mvs, pair.txt
colmap_data_paths = [] #Colmap output
outputpaths = []# scene.mvs ply

#independent path
for i in range(0, nParts):
	inputpaths.append(basepath + "/Densify_temp_" + str(i)+ "/")                 #"/home/hadoop/data/data/0423_SF/Densify_temp"
	colmap_data_paths.append(basepath + "/Colmap_In_" + str(i) + "/")            #"/home/hadoop/data/data/0423_SF/Colmap_In"
	outputpaths.append(outputdir + "/Re_" + str(i) + "/")                        #"/home/hadoop/data/data/0423_SF/scx_Re"
	
########################################EXE PATH#########################################################
#partition exe program path 
part_exepath = kernel_path + "/openMVS_partition_build/bin/DensifyPointCloud"

# dense estimate exe path
colmap_exepath = kernel_path + "/colmap_script.py"

# merge exe program path
merge_mvs_exepath = kernel_path + "/openMVS_merge_build/bin/DensifyPointCloud"
merge_ply_exepath = kernel_path + "/merge_ply_files.py "

############################################# Part #####################################################

#delete extra outputs
os.popen("mkdir " + tmppath)
os.popen("mkdir " + outputdir)
os.popen("mkdir " + outputdir + "/mvs")
os.popen("rm " + tmppath + "/pair*")
os.popen("rm " + tmppath + "/doupair*")

for i in range(0, execNum - 1):
	os.popen("ssh slave" + str(i + 1) + " mkdir -p " + basepath)
	time.sleep(sleep_time)
	os.popen("ssh slave" + str(i + 1) + " rm -r " + outputdir)
	time.sleep(sleep_time)
	os.popen("ssh slave" + str(i + 1) + " mkdir -p " + outputdir)
	time.sleep(sleep_time)

print(task_exeSlave)
for i in range(0, nParts):
	slave_index = task_exeSlave[i]
	if slave_index == 0:
		os.popen("rm -r " + inputpaths[i])
		time.sleep(sleep_time)
		os.popen("rm -r " + outputpaths[i])
		time.sleep(sleep_time)
		os.popen("rm -r " + colmap_data_paths[i])
		time.sleep(sleep_time)
		os.popen("mkdir -p " + inputpaths[i])
		time.sleep(sleep_time)
		os.popen("mkdir -p " + outputpaths[i])
		time.sleep(sleep_time)
		os.popen("mkdir -p " + colmap_data_paths[i])
		time.sleep(sleep_time)
        # Colmap_In/images 下形成一个软连接，指向图片
        #os.popen("ln -sf " + imgpath + " " + colmap_data_paths[slave_index] + "/images")
	else:
		os.popen("ssh slave" + str(slave_index) + " rm -r " + inputpaths[i])
		time.sleep(sleep_time)
		os.popen("ssh slave" + str(slave_index) + " rm -r " + outputpaths[i])
		time.sleep(sleep_time)
		os.popen("ssh slave" + str(slave_index) + " rm -r " + colmap_data_paths[i])
		time.sleep(sleep_time)
		os.popen("ssh slave" + str(slave_index) + " mkdir -p " + inputpaths[i])
		time.sleep(sleep_time)
		os.popen("ssh slave" + str(slave_index) + " mkdir -p " + outputpaths[i])
		time.sleep(sleep_time)
		os.popen("ssh slave" + str(slave_index) + " mkdir -p " + colmap_data_paths[i])
		time.sleep(sleep_time)
        # Colmap_In/images 下形成一个软连接，指向图片
        #os.popen("ssh slave" + str(slave_index) + " ln -sf " + imgpath + " " + colmap_data_paths[i] + "/images")
        
part_start_time = time.time()
child = subprocess.Popen(part_exepath + " -i " + scenepath + " -o " + outputdir + "/scene_modified.mvs  --archive-type 1 --parts " + str(nParts) + " -w " + imgpath + " --pairpath " + tmppath, shell=True, stdout=subprocess.PIPE, stderr = subprocess.STDOUT)

# for output log
while child.poll() is None:
	child.stdout.flush()
	line = child.stdout.readline()
	line = line.decode('utf-8')
	print(line)

part_end_time = time.time()
part_time = part_end_time - part_start_time
print("Partition finished, run time is %0.2f s\n"%part_time)
print("=====================Partition end=====================")

#send scene to master input && slaves input
for i in range(0, nParts):
	slave_index = task_exeSlave[i]
    # sleep to ensure the transport
	if slave_index == 0:
		os.popen("cp -r " + scenepath + " " + inputpaths[i])
		time.sleep(sleep_time)
		# os.popen("cp -r " + pairpath + "/pair"+str(i)+".txt " + inputpaths[i])
		os.popen("cp -r " + tmppath + "/pairName"+str(i)+".txt " + inputpaths[i] + "/pairName.txt")
		time.sleep(sleep_time)
	else:
		os.popen("scp " + scenepath + " hadoop@slave"+str(slave_index)+":"+inputpaths[i])
		time.sleep(sleep_time)
		# os.popen("scp " + pairpath + "/pair"+str(i)+".txt "+" hadoop@slave"+str(slave_index)+":"+inputpaths[i])
		os.popen("scp " + tmppath + "/pairName"+str(i)+".txt "+" hadoop@slave"+str(slave_index)+":"+inputpaths[i] + "/pairName.txt")
		time.sleep(sleep_time)

########################################################### first part end, ensure every nodes have correct file directory ####################################


################################################################        Densify         ######################################################################

processlist = []
densify_end = []

for i in range(0, nParts):
	slave_index = task_exeSlave[i]
	if(slave_index == 0):
		#print("python " + colmap_exepath + " --dataset_path "+ colmap_data_paths[i] + " --scene_path " + outputpaths[i] + "/scene_dense_" + str(i) + ".mvs" + " --pair_file " + inputpaths[i] + "/pairName.txt" + " --kernel_path " + kernel_path + " --img_path " + imgpath + " --resolution " + str(resolution) + " --task_id " + str(i) + " --quality " + quality)
		#print(1/0)
		child = subprocess.Popen("python " + colmap_exepath + " --dataset_path "+ colmap_data_paths[i] + " --scene_path " + outputpaths[i] + "/scene_dense_" + str(i) + ".mvs" + " --pair_file " + inputpaths[i] + "/pairName.txt" + " --kernel_path " + kernel_path + " --img_path " + imgpath + " --resolution " + str(resolution) + " --task_id " + str(i) + " --quality " + quality, shell= True,stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
	else:
        # 指定位置，提前赋予执行权限，所以没有放在tmppath里
		#f1 = open('/home/hadoop/scx/Distribute/tmpData/test.sh', 'w')
		#headtext = "#!/bin/bash\n"
		#sshhead = "ssh hadoop@slave" + str(slave_index) + " -tt << sshoff\n"
		cmdtext = "python " + colmap_exepath + " --dataset_path " + colmap_data_paths[i] + " --scene_path " + outputpaths[i] + "/scene_dense_"+ str(i) +".mvs" + " --pair_file " + inputpaths[i] + "/pairName.txt" +  " --kernel_path " + kernel_path + " --img_path " + imgpath + " --resolution " + str(resolution) + " --task_id " + str(i) + " --quality " + quality + "\n"
		#exittext = "exit\n"
		#endtext = "sshoff\n"
		#f1.writelines([headtext, sshhead, cmdtext, exittext, endtext] )
		#child = subprocess.Popen("/home/hadoop/scx/Distribute/tmpData/test.sh",shell = True,stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
		child = subprocess.Popen("ssh slave" + str(slave_index) + " " + cmdtext, shell = True,stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
	child.send_signal(signal.SIGTSTP)
	processlist.append(child)
	densify_end.append(False)
	time.sleep(5)
    
#start first task each slave
processlist[0].send_signal(signal.SIGCONT)
running_task = []
running_task.append(0)
start = 0
for i in range(0, execNum - 1):
	start = start + task_num_list[i]
	running_task.append(start)
	processlist[start].send_signal(signal.SIGCONT)

#wait task all done
Partition_Densify_Flag = False
while ((not Partition_Densify_Flag)):
	Partition_Densify_Flag = True
	for i in range(0, nParts):
		if(densify_end[i] == False):
			Partition_Densify_Flag = False
			break
	
	len_running_task = len(running_task)
	print(running_task)
	# 轮询各个节点，看当前任务是否结束，结束开始下一个，都结束就完成
	i = 0
	while i < len_running_task:
    
		task_id = running_task[i]
		p = processlist[task_id]
		slave_index = task_exeSlave[task_id]
		
		if p.poll() is None:
			p.stdout.flush()
			line = p.stdout.readline()
			line = line.decode('utf-8')
			print("slave" + str(slave_index) + " : " + line)
		else:
			if densify_end[task_id] == False:
				densify_end[task_id] = True
				running_task.remove(task_id)
				i = i - 1
				len_running_task = len_running_task - 1
				if task_id + 1 < nParts and task_exeSlave[task_id] == task_exeSlave[task_id + 1]:
					running_task.append(task_id + 1)
					len_running_task = len_running_task + 1
					processlist[task_id + 1].send_signal(signal.SIGCONT)
		i = i + 1
			
print("=====================Partition Densify end=====================")

# ################################################## Merge ######################################################################

merge_start_time = time.time()
#send results to master
for i in range(0,nParts):
	slave_index = task_exeSlave[i]
	if slave_index == 0:
		os.popen("cp " + outputpaths[i] + "/scene* " + outputdir + "/mvs/scene_dense_" + str(i) + ".mvs")
		os.popen("cp " + colmap_data_paths[i] + "/dense/fused.ply  " + outputdir + "/fused" + str(i) + ".ply")
	else:
		os.popen("scp "+"hadoop@slave"+str(slave_index)+":"+outputpaths[i]+"/scene* " + outputdir + "/mvs/scene_dense_" + str(i) + ".mvs")
		os.popen("scp "+"hadoop@slave"+str(slave_index)+":"+colmap_data_paths[i]+"/dense/fused.ply  " + outputdir + "/fused" + str(i) + ".ply")

#print("python " + merge_ply_exepath + " --folder_path " + outputdir + " --merged_path "+ outputdir + "/fused_All.ply ")
os.popen("python " + merge_ply_exepath + " --folder_path " + outputdir + " --merged_path "+ outputdir + "/fused_All.ply ")

#Merge results into one

child=subprocess.Popen(merge_mvs_exepath + " -i " + outputdir + "/mvs " +" -o " + outputdir + "/scene_dense_all.mvs " + " --archive-type 1 " + " -w " + imgpath, shell=True,stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
while child.poll() is None:
	child.stdout.flush()
	line = child.stdout.readline()
	line = line.decode('utf-8')
	print(line)

merge_end_time = time.time()
merge_time = merge_end_time - merge_start_time
print("merge finished, run time is %0.2f s\n"%merge_time)
print("=====================Merge end=====================")

end_time = time.time()
run_time = end_time - begin_time
print("total dense reconstruction finished, run time is %0.2f s\n"%run_time)

