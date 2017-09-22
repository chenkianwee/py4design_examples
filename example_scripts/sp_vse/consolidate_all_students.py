import os
#=================================================================
#INPUTS
#=================================================================
n_students = 28
data_dir = "F:\\kianwee_work\\smart\\journal\\enabling_evo_design\\data1"

#=================================================================
#MAIN SCRIPT
#================================================================= 
all_student = "student_id,n_design_concept_explored,success,unsuccessful,n_design_alternatives,feedback_time,far_min,far_max,far_range,usffai_min,usffai_max,usffai_range,ngen\n"
all_concept = "student_id,name,srf_cnt,nparms,design_space,n_design_alternatives,feedback_time,far_min,far_max,far_range,usffai_min,usffai_max,usffai_range\n"
all_stage = "student_id,n_design_concept1,n_design_alternatives1,feedback_time1,far_min1,far_max1,far_range1,usffai_min1,usffai_max1,usffai_range1,"+\
            "n_design_concept2,n_design_alternatives2,feedback_time2,far_min2,far_max2,far_range2,usffai_min2,usffai_max2,usffai_range2," +\
            "n_design_concept3,n_design_alternatives3,feedback_time3,far_min3,far_max3,far_range3,usffai_min3,usffai_max3,usffai_range3\n"
for scnt in range(n_students):
    student_dir = os.path.join(data_dir, str(scnt))
    #=================================================================
    #read the student exp file
    #=================================================================
    student_exploration_filepath = os.path.join(student_dir, "student_exploration.csv")
    sf = open(student_exploration_filepath, "r")
    sline_list = sf.readlines()
    sline_list = sline_list[1:]
    all_student = all_student + sline_list[0]
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
    

all_student_filepath = os.path.join(data_dir, "all_student.csv")
asf = open(all_student_filepath, "w")
asf.write(all_student)
asf.close()

all_concept_filepath = os.path.join(data_dir, "all_concept.csv")
acf = open(all_concept_filepath, "w")
acf.write(all_concept)
acf.close()

all_stage_filepath = os.path.join(data_dir, "all_stage.csv")
asf2 = open(all_stage_filepath, "w")
asf2.write(all_stage)
asf2.close()