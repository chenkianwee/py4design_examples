import os
#=================================================================
#INPUTS
#=================================================================
n_students = 28
data_dir = "F:\\kianwee_work\\smart\\journal\\enabling_evo_design\\data"

#=================================================================
#MAIN SCRIPT
#================================================================= 
all_student = "student_id,n_design_concept_explored,success,unsuccessful,avg_nparms,srf_cnt_min, srf_cnt_max,"+\
                "n_design_alternatives,feedback_time,far_min,far_max,far_range,usffai_min,usffai_max,usffai_range,ngen,"+\
                "stage1%,stage2%,stage3%,avg_design_space,dominate,avg_c_measure,s_measure,facilitate,consider\n"

all_concept = "student_id,name,srf_cnt,nparms,design_space,n_design_alternatives,feedback_time,far_min,far_max,far_range,usffai_min,usffai_max,usffai_range\n"

all_stage = "student_id,n_design_concept1,n_design_alternatives1,feedback_time1,far_min1,far_max1,far_range1,usffai_min1,usffai_max1,usffai_range1,"+\
            "n_design_concept2,n_design_alternatives2,feedback_time2,far_min2,far_max2,far_range2,usffai_min2,usffai_max2,usffai_range2," +\
            "n_design_concept3,n_design_alternatives3,feedback_time3,far_min3,far_max3,far_range3,usffai_min3,usffai_max3,usffai_range3\n"
sline_list2 = []
facilitate_list = []
facilitate_list_yes = []
consider_list = []
consider_list_yes = []
for scnt in range(n_students):
    student_dir = os.path.join(data_dir, str(scnt))
    info_filepath = os.path.join(student_dir, "info.csv")
    #=================================================================
    #read the info file
    #=================================================================
    info_file = open(info_filepath,"r")
    info_line_list = info_file.readlines()
    facilitate = info_line_list[7].split(",")[1].replace("\n","")
    consider = info_line_list[8].split(",")[1].replace("\n","")
    facilitate_list.append(facilitate)
    consider_list.append(consider)
    if facilitate == "yes":
        facilitate_list_yes.append(facilitate)
    if consider == "yes":
        consider_list_yes.append(consider)
    print facilitate, consider
    #=================================================================
    #read the student exp file
    #=================================================================
    student_exploration_filepath = os.path.join(student_dir, "student_exploration.csv")
    sf = open(student_exploration_filepath, "r")
    sline_list = sf.readlines()
    sline_list = sline_list[1:]
    sline = sline_list[0]
    sline_list2.append(sline)
    #all_student = all_student + sline
    sf.close()
    #=================================================================
    #read the concept exp file
    #=================================================================
    concept_exploration_filepath = os.path.join(student_dir, "concept_exploration.csv")
    cf = open(concept_exploration_filepath, "r")
    cline_list = cf.readlines()
    cline_list = cline_list[1:]
    for cline in cline_list:
        all_concept = all_concept + cline
    cf.close()
    #=================================================================
    #read the stage exp file
    #=================================================================
    stage_exploration_filepath = os.path.join(student_dir, "stage_exploration.csv")
    sf2 = open(stage_exploration_filepath, "r")
    sf2line_list = sf2.readlines()
    sf2line_list = sf2line_list[1:]
    all_stage = all_stage + sf2line_list[0]
    sf2.close()
    

nconcept = 0
nda = 0
total_time = 0
srf_cnt_min = 1000000
srf_cnt_max = -1

far_min = 1000000
far_max = -1

usffai_min = 1000000
usffai_max = -1

stage1_percent = 0
stage2_percent = 0
stage3_percent = 0

avg_nparms = 0
avg_space = 0

s_measure_dict = {}
scnt = 0
for sline2 in sline_list2:
    sline = sline2.replace("\n", "")
    sline_split_list = sline.split(",")
    
    a_nconcept = int(sline_split_list[2])
    nconcept = nconcept + a_nconcept
    
    a_nda = int(sline_split_list[6])
    nda = nda + a_nda
    
    feedback_time = float(sline_split_list[7])
    time = feedback_time*a_nda
    total_time = total_time + time
    
    asrf_cnt_min = float(sline_split_list[4])
    asrf_cnt_max = float(sline_split_list[5])
    if asrf_cnt_min < srf_cnt_min:
        srf_cnt_min = asrf_cnt_min
    if asrf_cnt_max > srf_cnt_max:
        srf_cnt_max = asrf_cnt_max
        
    afar_min = float(sline_split_list[8])
    afar_max = float(sline_split_list[9])
    if afar_min < far_min:
        far_min = afar_min
    if afar_max > far_max:
        far_max = afar_max
        
    ausffai_min = float(sline_split_list[11])
    ausffai_max = float(sline_split_list[12])
    if ausffai_min < usffai_min:
        usffai_min = ausffai_min
    if ausffai_max > usffai_max:
        usffai_max = ausffai_max
        
    stage1_percent+=float(sline_split_list[-7])
    stage2_percent+=float(sline_split_list[-6])
    stage3_percent+=float(sline_split_list[-5])
    
    avg_nparms+=int(sline_split_list[4])
    
    avg_space+=int(sline_split_list[-4])
    
    domination = int(sline_split_list[-3])
    s_measure = float(sline_split_list[-1])
    s_measure_dict[sline+ "," + facilitate_list[scnt]+ "," + consider_list[scnt] + "\n"] = (domination,s_measure)
    scnt +=1
    
for key, value in sorted(s_measure_dict.iteritems(), key=lambda (k,v): (v,k), reverse = True):
    all_student = all_student + key
    
print nconcept/28.0
print nda, nda/28.0
print total_time/nda
print srf_cnt_min, srf_cnt_max
print far_min, far_max
print usffai_min, usffai_max
print stage1_percent/28
print stage2_percent/28
print stage3_percent/28
print avg_nparms/28
print avg_space/28
print len(facilitate_list_yes)
print len(consider_list_yes)

all_student_filepath = os.path.join(data_dir, "all_student.csv")
asf = open(all_student_filepath, "w")
asf.write(all_student)
asf.close()

all_concept_filepath = os.path.join(data_dir, "all_concept.csv")
acf = open(all_concept_filepath, "w")
#print all_concept
acf.write(all_concept)
acf.close()

all_stage_filepath = os.path.join(data_dir, "all_stage.csv")
asf2 = open(all_stage_filepath, "w")
asf2.write(all_stage)
asf2.close()
