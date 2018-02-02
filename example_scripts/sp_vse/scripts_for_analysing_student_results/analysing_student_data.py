import os
from py4design import pyoptimise
#=================================================================
#FUNCTIONS
#=================================================================
def extract_design_concept(design_concept_dir, student_id):
    isdir = os.path.isdir(design_concept_dir)
    #each directory is a design concept
    if isdir:
        concept_name = os.path.split(design_concept_dir)[1]
        design_concept_dict = {}
        e_alternative_dict_list = []
        p_alternative_dict_list = []
        o_alternative_dict_2dlist = []
        optimisation_run_dict_list = []
        csv_dir = os.path.join(design_concept_dir, "csv")
        csv_list = [name for name in os.listdir(csv_dir)]
        name = os.path.split(design_concept_dir)[-1]
        for csv in csv_list:
            csv_file = os.path.join(csv_dir, csv)
            if csv == "exploration_log.csv":
                rf = open(csv_file,"r")
                line_list = rf.readlines()
                line_list = line_list[1:]
                for line in line_list:
                    #each line is a design alternative
                    alternative_dict = {}
                    element_list = line.split(",")
                    alternative_dict["far"] = float(element_list[1])
                    alternative_dict["usffai"] = float(element_list[2])
                    alternative_dict["nparms"] = 0
                    alternative_dict["nsurfaces"] = int(element_list[3])
                    alternative_dict["time"] = float(element_list[4].replace("\n",""))
                    alternative_dict["concept_name"] = concept_name
                    alternative_dict["student_id"] = student_id
                    alternative_dict["stage"] = "stage1"
                    alternative_dict["name"] = concept_name
                    e_alternative_dict_list.append(alternative_dict)
                rf.close()
                    
            if csv == "parametric_log.csv":
                rf = open(csv_file,"r")
                line_list = rf.readlines()
                line_list = line_list[1:]
                parm_2dlist = []
                for line in line_list:
                    #each line is a design alternative
                    element_list = line.split(",")
                    parm_list = element_list[3:15]
                    if parm_list not in parm_2dlist:
                        #this means there is no repeat of parameters
                        parm_2dlist.append(parm_list)
                        if float(element_list[1]) != 0.0:
                            #it means the alternatives geometries are broken
                            alternative_dict = {}
                            alternative_dict["far"] = float(element_list[1])
                            alternative_dict["usffai"] = float(element_list[2])
                            alternative_dict["nparms"] = int(element_list[15])
                            alternative_dict["nsurfaces"] = int(element_list[16])
                            alternative_dict["time"] = float(element_list[17].replace("\n",""))
                            alternative_dict["concept_name"] = concept_name
                            alternative_dict["student_id"] = student_id
                            alternative_dict["stage"] = "stage2"
                            alternative_dict["name"] = concept_name
                            p_alternative_dict_list.append(alternative_dict)
                rf.close()
                if "exploration_log.csv" not in csv_list:
                    srf_cnt_csv = os.path.join(csv_dir, "massing_srf_cnt.csv")
                    srf_cnt_csv_file = open(srf_cnt_csv)
                    srf_cnt = srf_cnt_csv_file.readlines()[0].replace("\n","")
                    #print "READLINES#===============",
                    design_concept_dict["initial_nsurfaces"] = float(srf_cnt)
                    
            if csv == "optimisation_log.csv":
                rf = open(csv_file,"r")
                line_list = rf.readlines()
                line_list = line_list[1:]
                
                opt_time_filepath = os.path.join(csv_dir, "optimisation_time_log.csv")
                rf2 = open(opt_time_filepath,"r")
                line_list2 = rf2.readlines()
                line_list2 = line_list2[1:]
                line_list3 = []
                index_list = []
                l2_cnt = 0
                for line2 in line_list2:
                    #find all the new_run keywords
                    line2 = line2.replace("\n","")
                    
                    if line2 == "new_run":
                        index_list.append(l2_cnt)
                        line_list3.append(line2)
                    else:
                        line_list3.append(float(line2))
                        
                    l2_cnt +=1
                    
                nindex = len(index_list)
                opt_time_list = []
                for index_cnt in range(nindex):
                    if nindex == 1:
                        opt_time_list.append(line_list3[index_list[index_cnt]+1:])
                    else:
                        if index_cnt != nindex-1:
                            opt_time_list.append(line_list3[index_list[index_cnt]+1:index_list[index_cnt+1]])
                        else:
                            opt_time_list.append(line_list3[index_list[index_cnt]+1:])
                        
                l_cnt = 0
                for line in line_list:
                    #each line is a design alternative
                    element_list = line.split(",")
                    optimisation_setting = {}
                    nparms = int(element_list[13])
                    optimisation_setting["nparms"] = nparms
                    optimisation_setting["design_space"] = int(element_list[14])
                    optimisation_setting["opt_time"] = sum(opt_time_list[l_cnt])
                    
                    
                    #read the xml and get all the design alternatives
                    xml_dir = os.path.join(design_concept_dir,"xml", str(l_cnt))
                    overall_filepath = os.path.join(xml_dir,"overall.xml")
                    inds = pyoptimise.analyse_xml.get_inds_frm_xml(overall_filepath)
                    o_alternative_dict_2dlist.append([])
                    for ind in inds:
                        score_list = pyoptimise.analyse_xml.get_score(ind)
                        ind_id = pyoptimise.analyse_xml.get_id(ind)
                        derived_parm_list = pyoptimise.analyse_xml.get_derivedparam(ind)
                        usffai = score_list[0]
                        far = score_list[1]
                        if far>0:
                            alternative_dict = {}
                            alternative_dict["far"] = float(far)
                            alternative_dict["usffai"] = float(usffai)
                            alternative_dict["nparms"] = nparms
                            alternative_dict["nsurfaces"] = int(derived_parm_list[0])
                            alternative_dict["concept_name"] = concept_name
                            alternative_dict["student_id"] = student_id
                            alternative_dict["stage"] = "stage3"
                            alternative_dict["name"] = ind_id
                            
                            o_alternative_dict_2dlist[-1].append(alternative_dict)
                        
                    ninds = len(inds)
                    ngen = ninds/25
                    optimisation_setting["ngen"] = ngen
                    optimisation_run_dict_list.append(optimisation_setting)
                    l_cnt+=1
                    
                rf.close()
                rf2.close()
                        
        design_concept_dict["design_alternatives_exp"] = e_alternative_dict_list
        design_concept_dict["design_alternatives_para"] = p_alternative_dict_list
        design_concept_dict["design_alternatives_opt"] = o_alternative_dict_2dlist
        design_concept_dict["optimisation_setting"] = optimisation_run_dict_list
        design_concept_dict["name"] = name
        return design_concept_dict
        
def extract_fai_usffai_from_dict(alternative_dict_list):
    far_usffai_dict = {}
    far_list = []
    usffai_list = []
    for adict in alternative_dict_list:
        far = adict["far"]
        usffai = adict["usffai"]

        far_list.append(far)
        usffai_list.append(usffai)
        
    far_min = min(far_list)
    far_max = max(far_list)
    far_range = far_max-far_min
    far_usffai_dict["far"] = far_list
    far_usffai_dict["far_min"] = far_min
    far_usffai_dict["far_max"] = far_max
    far_usffai_dict["far_range"] = far_range
    
    usffai_min = min(usffai_list)
    usffai_max = max(usffai_list)
    usffai_range = usffai_max - usffai_min
    far_usffai_dict["usffai"] = usffai_list
    far_usffai_dict["usffai_min"] = usffai_min
    far_usffai_dict["usffai_max"] = usffai_max
    far_usffai_dict["usffai_range"] = usffai_range
    return far_usffai_dict

def extract_avg_srf_cnt(alternative_dict_list):
    nsurfaces_list = []
    for adict in alternative_dict_list:
        nsurfaces = adict["nsurfaces"]
        nsurfaces_list.append(nsurfaces)
    
    avg_surfaces = sum(nsurfaces_list)/len(nsurfaces_list)
    return avg_surfaces

def extract_nparms(alternative_dict_list):
    nparms_list = []
    for adict in alternative_dict_list:
        nparms = adict["nparms"]
        nparms_list.append(nparms)
    min_nparm = min(nparms_list)
    max_nparm = max(nparms_list)
    return [min_nparm,max_nparm]

def extract_time(alternative_dict_list):
    time_list = []
    for adict in alternative_dict_list:
        time = adict["time"]
        if time > 0:
            time_list.append(time)
    return time_list

def extract_stage_lvl_core_info(alternative_dict_list):
    stage_dict = {}
    nsurfaces = extract_avg_srf_cnt(alternative_dict_list)
    n_alternatives = len(alternative_dict_list)
    far_usffai_dict = extract_fai_usffai_from_dict(alternative_dict_list)
    n_alt_for_feedback_time_calc_list = []
    #alternatives with time as -1 means incomplete result
    for adict in alternative_dict_list:
        if "time" in adict:
            if adict["time"] > 0:
                n_alt_for_feedback_time_calc_list.append(adict)
        else:
            n_alt_for_feedback_time_calc_list.append(adict)
                
    
    stage_dict["nsurfaces"] = nsurfaces
    stage_dict["nalternatives"] = n_alternatives
    stage_dict["nalternatives_feedback"] = len(n_alt_for_feedback_time_calc_list)
    stage_dict["far_min"] = far_usffai_dict["far_min"]
    stage_dict["far_max"] = far_usffai_dict["far_max"]
    stage_dict["far_range"] = far_usffai_dict["far_range"]
    stage_dict["usffai_min"] = far_usffai_dict["usffai_min"]
    stage_dict["usffai_max"] = far_usffai_dict["usffai_max"]
    stage_dict["usffai_range"] = far_usffai_dict["usffai_range"]
    
    return stage_dict
    
def extract_info_design_concept(design_concept_dict):
    concept_info_dict = {}
    total_alternative_dict_list = []
    #====================================================
    #design alternatives from exploration process
    #====================================================
    e_alternative_dict_list = design_concept_dict["design_alternatives_exp"]
    e_total_time = 0
    if e_alternative_dict_list:
        total_alternative_dict_list.extend(e_alternative_dict_list)
        stage1_dict = extract_stage_lvl_core_info(e_alternative_dict_list)
        
        e_feedback_time_list = extract_time(e_alternative_dict_list) 
        e_total_time = sum(e_feedback_time_list)
        if e_total_time == 0:
            e_feedback_time = -1
        else:
            e_feedback_time = e_total_time/stage1_dict["nalternatives_feedback"]
        
        stage1_dict["total_time"] = e_total_time 
        stage1_dict["feedback_time"] = e_feedback_time 
        concept_info_dict["stage1"] = stage1_dict
    #====================================================
    #design alternatives from parametric process
    #====================================================
    p_alternative_dict_list = design_concept_dict["design_alternatives_para"] 
    p_total_time = 0
    if p_alternative_dict_list:
        total_alternative_dict_list.extend(p_alternative_dict_list)
        
        stage2_dict = extract_stage_lvl_core_info(p_alternative_dict_list)
        
        p_feedback_time_list = extract_time(p_alternative_dict_list)
        p_total_time = sum(p_feedback_time_list)
        if p_total_time == 0:
            p_feedback_time = -1
        else:
            p_feedback_time = p_total_time/stage2_dict["nalternatives_feedback"]
        
        min_max_nparm_list = extract_nparms(p_alternative_dict_list)
        
        stage2_dict["total_time"] = p_total_time 
        stage2_dict["feedback_time"] = p_feedback_time 
        stage2_dict["parm_range"] = min_max_nparm_list
        concept_info_dict["stage2"] = stage2_dict
    
    #=======================================================================
    #design alternatives and optimisation settings from algorithmic process
    #=======================================================================
    optimisation_run_dict_list = design_concept_dict["optimisation_setting"]
    o_total_time = 0
    if optimisation_run_dict_list:
        o_alternative_dict_2dlist = ds["design_alternatives_opt"]
        design_space_list = []
        o_total_time_list = []
        ngen_list = []
        o_total_alternative_dict_list = []
        
        ocnt = 0
        for o_alternative_dict_list in o_alternative_dict_2dlist:
            o_total_alternative_dict_list.extend(o_alternative_dict_list)
            
            opt_dict = optimisation_run_dict_list[ocnt]
            design_space = opt_dict["design_space"]
            o_time = opt_dict["opt_time"]
            ngen = opt_dict["ngen"]
            
            design_space_list.append(design_space)
            o_total_time_list.append(o_time)
            ngen_list.append(ngen)
            ocnt+=1
            
        total_alternative_dict_list.extend(o_total_alternative_dict_list)
        stage3_dict = extract_stage_lvl_core_info(o_total_alternative_dict_list)
        
        o_total_time = sum(o_total_time_list)
        o_feedback_time = o_total_time/stage3_dict["nalternatives_feedback"]
        avg_design_space = sum(design_space_list)/len(design_space_list)
        avg_gen = sum(ngen_list)/len(ngen_list)
        max_gen = max(ngen_list)
        stage3_dict["total_time"] = o_total_time
        stage3_dict["feedback_time"] = o_feedback_time
        stage3_dict["avg_design_space"] = avg_design_space
        stage3_dict["avg_gen"] = avg_gen
        stage3_dict["max_gen"] = max_gen
        
        concept_info_dict["stage3"] = stage3_dict
        
    #=======================================================================
    #design alternatives overall
    #=======================================================================
    overall_dict = extract_stage_lvl_core_info(total_alternative_dict_list)
    total_time = e_total_time + p_total_time + o_total_time
    if total_time == 0:
        feedback_time = -1
    else:
        feedback_time = total_time/overall_dict["nalternatives_feedback"]
    
    overall_dict["total_time"] = total_time
    overall_dict["feedback_time"] = feedback_time
    overall_dict["alternative_list"] = total_alternative_dict_list
    concept_info_dict["overall_dict"] = overall_dict
    return concept_info_dict

def alternative_dict_list2_score_2d_list(alternative_dict_list):
    score_2dlist = []
    for alternative in alternative_dict_list:
        far = alternative["far"]
        usffai = alternative["usffai"]
        score_list = [far, usffai]
        score_2dlist.append(score_list)
    return score_2dlist

def extract_pareto_front_alt_dict(alternative_dict_list, score_2dlist):
    pareto_list = []
    npareto_list = []
    for alt_dict in alternative_dict_list:
        score_list = [alt_dict["far"], alt_dict["usffai"]]
        if (len(score_list)-1) !=0:     
            if pyoptimise.analyse_xml.on_pareto_front(score_list, score_2dlist, [1,1]):
                pareto_list.append(alt_dict)
            else:
                npareto_list.append(alt_dict) 
    return pareto_list, npareto_list

def draw_pareto_scatterplot(pareto_list, npareto_list, label, res_img_filepath):
    pts = []
    labellist =[]
    arealist = []
    colourlist = []
    
    for na in npareto_list:
        score_list = [na["far"], na["usffai"]]
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("black")
        
    for pa in pareto_list:
        score_list = [pa["far"], pa["usffai"]]
        idx = pa[label]
        print idx
        pts.append(score_list)
        labellist.append(str(idx))
        #labellist.append("")
        arealist.append(60)
        colourlist.append("red")
    
    pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=14, labellist = labellist,
                                                xlabel = "FAR", ylabel = "USFFAI", savefile = res_img_filepath)

#=================================================================
#MAIN SCRIPT
#=================================================================  
data_dir = "F:\\kianwee_work\\smart\\journal\\enabling_opt_design\\data"
total_alternative_list = []
total_alternative_list2 = []
total_time_list2 = []
pareto_2dlist = []
far_max_limit = 15
far_min_limit = 2
for cnt in range(28):
    #=================================================================
    #INPUTS
    #=================================================================
    #specify the student folder to analyse
    student_id = cnt
    #=================================================================
    #MAIN SCRIPT
    #=================================================================  
    student_dir = os.path.join(data_dir, str(student_id))
    student_alt_list = []
    #=================================================================
    #extract information about all unsuccessful design concept
    #=================================================================
    unsuccessful_dir = os.path.join(student_dir,"unsuccessful")
    u_dir_list = [name for name in os.listdir(unsuccessful_dir)]
    u_design_concept_dict_list = []
    for u_dir in u_dir_list:
        u_design_concept_dir = os.path.join(unsuccessful_dir, u_dir)
        u_design_concept_dict = extract_design_concept(u_design_concept_dir, student_id)
        if u_design_concept_dict:
            u_design_concept_dict_list.append(u_design_concept_dict)
    
    #=================================================================
    #extract information about all the successful design concept
    #=================================================================
    successful_dir = os.path.join(student_dir,"successful")
    #print successful_folder
    dir_list = [name for name in os.listdir(successful_dir)]
    
    design_concept_dict_list = []
    for adir in dir_list:
        #each directory is a design concept
        design_concept_dir = os.path.join(successful_dir, adir)
        design_concept_dict = extract_design_concept(design_concept_dir, student_id)
        if design_concept_dict:
            design_concept_dict_list.append(design_concept_dict)
            
    #==========================================================================================
    #process the extracted information
    #==========================================================================================
    #student level lists
    total_time_list = []
    total_nalternatives_list = []
    total_time_alternatives = []
    total_srf_cnt_list = []
    far_min_list = []
    far_max_list = []
    usffai_min_list = []
    usffai_max_list = []
    max_gen_list = []
    avg_design_space_list =[]
    
    #student design stages level list
    stage1_concept_list = []
    stage2_concept_list = []
    stage3_concept_list = []
    
    stage1_alternative_list = []
    stage2_alternative_list = []
    stage3_alternative_list = []
    
    stage1_far_min_list = []
    stage2_far_min_list = []
    stage3_far_min_list = []
    
    stage1_far_max_list = []
    stage2_far_max_list = []
    stage3_far_max_list = []
    
    stage1_usffai_min_list = []
    stage2_usffai_min_list = []
    stage3_usffai_min_list = []
    
    stage1_usffai_max_list = []
    stage2_usffai_max_list = []
    stage3_usffai_max_list = []
    
    stage1_time_list = []
    stage2_time_list = []
    stage3_time_list = []
    
    stage1_alternative_time_list = []
    stage2_alternative_time_list = []
    stage3_alternative_time_list = []
    
    concept_str = "student_id,name,srf_cnt,nparms,design_space,n_design_alternatives,feedback_time,far_min,far_max,far_range,usffai_min,usffai_max,usffai_range\n"
    
    for ds in design_concept_dict_list:
        name = ds["name"]
        concept_info_dict = extract_info_design_concept(ds)
        overall_dict = concept_info_dict["overall_dict"]
        
        concept_alternative_list = overall_dict["alternative_list"]
        total_alternative_list.extend(concept_alternative_list)
        
        concept_alternative_list2 = overall_dict["nalternatives_feedback"]
        total_alternative_list2.append(concept_alternative_list2)
        
        student_alt_list.extend(concept_alternative_list)
        
        time = overall_dict["total_time"]
        total_time_list.append(time)
        total_time_list2.append(time)
        nalternatives = overall_dict["nalternatives"]
        total_nalternatives_list.append(nalternatives)
        ntime_alternatives = overall_dict["nalternatives_feedback"]
        total_time_alternatives.append(ntime_alternatives)
        c_far_min = overall_dict["far_min"]
        far_min_list.append(c_far_min)
        c_far_max = overall_dict["far_max"]
        far_max_list.append(c_far_max)
        c_usffai_min = overall_dict["usffai_min"]
        usffai_min_list.append(c_usffai_min)
        c_usffai_max = overall_dict["usffai_max"]
        usffai_max_list.append(c_usffai_max)
        
        #==========================================================================================
        #concept level data
        #==========================================================================================
        c_feedback_time = overall_dict["feedback_time"]
        c_far_range = c_far_max - c_far_min
        c_usffai_range = c_usffai_max - c_usffai_min
        if "stage1" in concept_info_dict:
            stage1_dict = concept_info_dict["stage1"]
            srf_cnt = stage1_dict["nsurfaces"]
            e_nalternatives = stage1_dict["nalternatives"]
            e_far_min = stage1_dict["far_min"]
            e_far_max = stage1_dict["far_max"]
            e_usffai_min = stage1_dict["usffai_min"]
            e_usffai_max = stage1_dict["usffai_max"]
            e_time = stage1_dict["total_time"]
            e_nalternatives_time = stage1_dict["nalternatives_feedback"]
            
            stage1_concept_list.append(ds)
            stage1_alternative_list.append(e_nalternatives)
            stage1_far_min_list.append(e_far_min)
            stage1_far_max_list.append(e_far_max)
            stage1_usffai_min_list.append(e_usffai_min)
            stage1_usffai_max_list.append(e_usffai_max)
            stage1_time_list.append(e_time)
            stage1_alternative_time_list.append(e_nalternatives_time)
        else:
            #look for the csv that documents the srf cnt of the initial model
            srf_cnt = ds["initial_nsurfaces"]
            
        total_srf_cnt_list.append(srf_cnt)
        nparms = str(0)
        if "stage2" in concept_info_dict:
            stage2_dict = concept_info_dict["stage2"]
            parm_range = stage2_dict["parm_range"]
            nparms = str(parm_range[0]) + "_" + str(parm_range[1])
            
            p_nalternatives = stage2_dict["nalternatives"]
            p_far_min = stage2_dict["far_min"]
            p_far_max = stage2_dict["far_max"]
            p_usffai_min = stage2_dict["usffai_min"]
            p_usffai_max = stage2_dict["usffai_max"]
            p_time = stage2_dict["total_time"]
            p_nalternatives_time = stage2_dict["nalternatives_feedback"]
            
            stage2_concept_list.append(ds)
            stage2_alternative_list.append(p_nalternatives)
            stage2_far_min_list.append(p_far_min)
            stage2_far_max_list.append(p_far_max)
            stage2_usffai_min_list.append(p_usffai_min)
            stage2_usffai_max_list.append(p_usffai_max)
            stage2_time_list.append(p_time)
            stage2_alternative_time_list.append(p_nalternatives_time)
            
        design_space = 0
        if "stage3" in concept_info_dict:
            stage3_dict = concept_info_dict["stage3"]
            max_gen = stage3_dict["max_gen"]
            max_gen_list.append(max_gen)
            
            design_space = stage3_dict["avg_design_space"]
            avg_design_space_list.append(design_space)
            o_nalternatives = stage3_dict["nalternatives"]
            o_far_min = stage3_dict["far_min"]
            o_far_max = stage3_dict["far_max"]
            o_usffai_min = stage3_dict["usffai_min"]
            o_usffai_max = stage3_dict["usffai_max"]
            o_time = stage3_dict["total_time"]
            o_nalternatives_time = stage3_dict["nalternatives_feedback"]
            
            stage3_concept_list.append(ds)
            stage3_alternative_list.append(o_nalternatives)
            stage3_far_min_list.append(o_far_min)
            stage3_far_max_list.append(o_far_max)
            stage3_usffai_min_list.append(o_usffai_min)
            stage3_usffai_max_list.append(o_usffai_max)
            stage3_time_list.append(o_time)
            stage3_alternative_time_list.append(o_nalternatives_time)
        
        concept_str = concept_str + str(student_id) + "," + name + "," + str(srf_cnt) + "," + nparms + "," + str(design_space)\
                + "," + str(nalternatives) + "," + str(c_feedback_time) + "," + str(c_far_min) + "," + str(c_far_max)\
                + "," + str(c_far_range) + "," + str(c_usffai_min) + "," + str(c_usffai_max)\
                + "," + str(c_usffai_range) + "\n"
        
    #==========================================================================================
    #student level data
    #==========================================================================================
    n_success = len(design_concept_dict_list)
    n_unsuccess = len(u_design_concept_dict_list)
    ndc = n_success + n_unsuccess
    total_design_alternatives = sum(total_nalternatives_list)  
    
    srf_cnt_min = min(total_srf_cnt_list)
    srf_cnt_max = max(total_srf_cnt_list)
    total_time = sum(total_time_list)
    n_alternatives_with_time = sum(total_time_alternatives)
    feedback_time = int(total_time/n_alternatives_with_time)
    
    far_min = min(far_min_list)
    far_max = max(far_max_list)
    far_range = far_max-far_min
    usffai_min = min(usffai_min_list)
    usffai_max = max(usffai_max_list)
    usffai_range = usffai_max - usffai_min
    
    ngen_max = -1
    if max_gen_list:
        ngen_max = max(max_gen_list)
    #get the pareto fronts for each student
    far_list_filtered = []
    usffai_list_filtered = []
    stu_falt_list = []
    stu_nparms_list = []
    for stu_alt in student_alt_list:
        stu_nparms = stu_alt["nparms"]
        stu_nparms_list.append(stu_nparms)
        stu_far = stu_alt["far"]
        stu_usffai = stu_alt["usffai"]
        if far_min_limit<=stu_far<far_max_limit:
            stu_falt_list.append(stu_alt)
            far_list_filtered.append(stu_far)
            usffai_list_filtered.append(stu_usffai)
        
    student_score_2dlist = alternative_dict_list2_score_2d_list(stu_falt_list)
    stu_pareto_list, stu_npareto_list = extract_pareto_front_alt_dict(stu_falt_list, student_score_2dlist)
    
    #if student_id == 26:
    #    res_img_filepath = "F:\\kianwee_work\\smart\\journal\\enabling_evo_design\\img\\png\\ind_pareto.png"
    #    draw_pareto_scatterplot(stu_pareto_list, stu_npareto_list,"concept_name", res_img_filepath)
    
    stage1_list = []
    stage2_list = []
    stage3_list = []
    stu_concept_list = []
    for pa in stu_pareto_list:
        stage = pa["stage"]
        p_far = pa["far"]
        p_usffai = pa["usffai"]
        if stage == "stage1":
            stage1_list.append([p_far, p_usffai])
        if stage == "stage2":
            stage2_list.append([p_far, p_usffai])
        if stage == "stage3":
            stage3_list.append([p_far, p_usffai])
            
    npa = float(len(stu_pareto_list))
    print "STUDENT ID", student_id
    if stage1_list:
        s1_dist_list = pyoptimise.analyse_xml.crowd_distance_assignment(stage1_list)
        h1 = pyoptimise.analyse_xml.hyper_volume(stage1_list, (0,0), (1,1))
        s1_dist_list = s1_dist_list[1:-1]
        print "STAGE1 H", h1
        if len(s1_dist_list) !=0:
            print "STAGE1", sum(s1_dist_list)/float(len(s1_dist_list))
        
    if stage2_list:
        h2 = pyoptimise.analyse_xml.hyper_volume(stage2_list, (0,0), (1,1))
        s2_dist_list = pyoptimise.analyse_xml.crowd_distance_assignment(stage2_list)
        s2_dist_list = s2_dist_list[1:-1]
        print "STAGE2 H",h2
        if len(s2_dist_list) !=0:
            print "STAGE2", sum(s2_dist_list)/float(len(s2_dist_list))
    
    if stage3_list:
        h3 = pyoptimise.analyse_xml.hyper_volume(stage3_list, (0,0), (1,1))
        s3_dist_list = pyoptimise.analyse_xml.crowd_distance_assignment(stage3_list)
        s3_dist_list = s3_dist_list[1:-1]
        print "STAGE3 H",h3
        if len(s3_dist_list) !=0:
            print "STAGE3", sum(s3_dist_list)/float(len(s3_dist_list))
        
    stage1_percent = len(stage1_list)
    stage2_percent = len(stage2_list)
    stage3_percent = len(stage3_list)
    
    avg_nparms = sum(stu_nparms_list)/len(stu_nparms_list)
    stu_avg_design_space = 0
    if avg_design_space_list:
        stu_avg_design_space = sum(avg_design_space_list)/len(avg_design_space_list)
    
    n_pareto = len(stu_pareto_list)
    
    
    
    pareto_2dlist.append(stu_pareto_list)
    
    #print "FILTERED VS UNFILTERED DA:", len(student_alt_list), len(stu_falt_list)
    far_min_filtered = min(far_list_filtered)
    far_max_filtered = max(far_list_filtered)
    far_range_filtered = far_max_filtered-far_min_filtered
    usffai_min_filtered = min(usffai_list_filtered)
    usffai_max_filtered = max(usffai_list_filtered)
    usffai_range_filtered = usffai_max_filtered - usffai_min
    
    student_str = "student_id,n_design_concept_explored,success,unsuccessful,avg_nparms,srf_cnt_min, srf_cnt_max,"+\
                "n_design_alternatives,feedback_time,far_min,far_max,far_range,usffai_min,usffai_max,usffai_range,ngen,"+\
                "stage1%,stage2%,stage3%,avg_design_space,npareto,dominate,avg_c_measure,s_measure\n"
               
    student_str = student_str + str(student_id) + "," + str(ndc) + "," + str(n_success) + "," + str(n_unsuccess)\
                + "," + str(avg_nparms) + "," + str(srf_cnt_min) + "," + str(srf_cnt_max) + "," + str(total_design_alternatives)\
                + "," + str(feedback_time) + "," + str(far_min) + "," + str(far_max) + "," + str(far_range)\
                + "," + str(usffai_min) + "," + str(usffai_max) + "," + str(usffai_range) + "," + str(ngen_max)\
                + "," + str(stage1_percent) + "," + str(stage2_percent) + "," + str(stage3_percent)\
                + "," + str(stu_avg_design_space) + "," + str(n_pareto) + "\n"
    '''
    student_str = student_str + str(student_id) + "," + str(ndc) + "," + str(n_success) + "," + str(n_unsuccess)\
                + "," + str(avg_nparms) + "," + str(srf_cnt_min) + "," + str(srf_cnt_max) + "," + str(total_design_alternatives)\
                + "," + str(feedback_time) + "," + str(far_min_filtered) + "," + str(far_max_filtered) + "," + str(far_range_filtered)\
                + "," + str(usffai_min_filtered) + "," + str(usffai_max_filtered) + "," + str(usffai_range_filtered) + "," + str(ngen_max)\
                + "," + str(stage1_percent) + "," + str(stage2_percent) + "," + str(stage3_percent)\
                + "," + str(stu_avg_design_space) + "," + str(n_pareto) + "\n"
    '''    
    student_filepath = os.path.join(student_dir, "student_exploration.csv")
    sf = open(student_filepath, "w")
    sf.write(student_str)
    sf.close()
    
    #==========================================================================================
    #write to concept file
    #==========================================================================================
    concept_filepath = os.path.join(student_dir, "concept_exploration.csv")
    cf = open(concept_filepath, "w")
    cf.write(concept_str)
    cf.close()
    
    #==========================================================================================
    #student level design stage level data
    #==========================================================================================
    stage_str = "student_id,n_design_concept1,n_design_alternatives1,feedback_time1,far_min1,far_max1,far_range1,usffai_min1,usffai_max1,usffai_range1,"+\
                "n_design_concept2,n_design_alternatives2,feedback_time2,far_min2,far_max2,far_range2,usffai_min2,usffai_max2,usffai_range2," +\
                "n_design_concept3,n_design_alternatives3,feedback_time3,far_min3,far_max3,far_range3,usffai_min3,usffai_max3,usffai_range3\n"
    #stage1
    nconcept1 = len(stage1_concept_list)
    nalternative1 = sum(stage1_alternative_list)
    far_min1 = min(stage1_far_min_list)
    far_max1 = max(stage1_far_max_list)
    far_range1 = far_max1-far_min1
    usffai_min1 = min(stage1_usffai_min_list)
    usffai_max1 = max(stage1_usffai_max_list)
    usffai_range1 = usffai_max1 - usffai_min1
    time1 = sum(stage1_time_list)
    nalt_time1 = sum(stage1_alternative_time_list)
    if time1 == 0:
        feedback_time1 = -1
    else:
        feedback_time1 = time1/nalt_time1
            
    stage1_str = str(student_id) + "," + str(nconcept1) + "," + str(nalternative1) + "," + str(feedback_time1) + "," + str(far_min1) + "," + str(far_max1) +\
                "," + str(far_range1) + "," + str(usffai_min1) + "," + str(usffai_max1) + "," + str(usffai_range1) + ","
    
    #stage2
    if stage2_concept_list:
        nconcept2 = len(stage2_concept_list)
        nalternative2 = sum(stage2_alternative_list)
        far_min2 = min(stage2_far_min_list)
        far_max2 = max(stage2_far_max_list)
        far_range2 = far_max2-far_min2
        usffai_min2 = min(stage2_usffai_min_list)
        usffai_max2 = max(stage2_usffai_max_list)
        usffai_range2 = usffai_max2 - usffai_min2
        time2 = sum(stage2_time_list)
        nalt_time2 = sum(stage2_alternative_time_list)
        if time2 == 0:
            feedback_time2 = -1
        else:
            feedback_time2 = time2/nalt_time2
    
        stage2_str = str(nconcept2) + "," + str(nalternative2) + "," + str(feedback_time2) + "," + str(far_min2) + "," + str(far_max2) +\
                    "," + str(far_range2) + "," + str(usffai_min2) + "," + str(usffai_max2) + "," + str(usffai_range2) + ","
    else:
        stage2_str = "0,0,-1,-1,-1,-1,-1,-1,-1,"
    
    #stage3
    if stage3_concept_list:
        nconcept3 = len(stage3_concept_list)
        nalternative3 = sum(stage3_alternative_list)
        far_min3 = min(stage3_far_min_list)
        far_max3 = max(stage3_far_max_list)
        far_range3 = far_max3-far_min3
        usffai_min3 = min(stage3_usffai_min_list)
        usffai_max3 = max(stage3_usffai_max_list)
        usffai_range3 = usffai_max3 - usffai_min3
        time3 = sum(stage3_time_list)
        nalt_time3 = sum(stage3_alternative_time_list)
        feedback_time3 = time3/nalt_time3
        if time3 == 0:
            feedback_time3 = -1
        else:
            feedback_time3 = time3/nalt_time3
        
        stage3_str = str(nconcept3) + "," + str(nalternative3) + "," + str(feedback_time3) + "," + str(far_min3) + "," + str(far_max3) +\
                    "," + str(far_range3) + "," + str(usffai_min3) + "," + str(usffai_max3) + "," + str(usffai_range3) + "\n"
    else:
        stage3_str = "0,0,-1,-1,-1,-1,-1,-1,-1\n"
        
    stage_str = stage_str + stage1_str + stage2_str + stage3_str
    
    stage_filepath = os.path.join(student_dir, "stage_exploration.csv")
    sf2 = open(stage_filepath, "w")
    sf2.write(stage_str)
    sf2.close()

#=================================================================
#GET THE PARETO FRONT OF ALL THE DESIGN ALTERNATIVES 
#=================================================================  
#filter the alternatives to make sure there are no ridiculous far 
res_img_filepath = "F:\\kianwee_work\\smart\\journal\\enabling_opt_design\\img\\png\\overall_pareto.png"
min_max_list = [1,1]
#filter the dict list to make sure all of the alt make sense
print "TOTAL NO. OF ALTERNATIVES:", len(total_alternative_list)
f_alt_list = []
for alt_dict in total_alternative_list:
    far = alt_dict["far"]
    usffai = alt_dict["usffai"]
    if far_min_limit<= far < far_max_limit:
        f_alt_list.append(alt_dict)
    
score_2dlist = alternative_dict_list2_score_2d_list(f_alt_list)
pareto_list, npareto_list = extract_pareto_front_alt_dict(f_alt_list, score_2dlist)
#draw_pareto_scatterplot(pareto_list, npareto_list,"name", res_img_filepath)
print "TOTAL NO. OF ALTERNATIVES:", len(f_alt_list)
print "NO. OF PARETO:", len(pareto_list)
print "NO. OF NON-PARETO:", len(npareto_list)
#=====================================================================
#MEASURE THE PARETO FRONT OF ALL STUDENTS WITH S MEASURE AND C MEASURE
#=====================================================================
avg_feedback_time = sum(total_time_list2)/len(total_alternative_list)

print "AVG FEEDBACK TIME", avg_feedback_time, sum(total_time_list2), len(total_alternative_list)/28

npareto = len(pareto_2dlist)
ref_pt = [0,0]
pcnt = 0
for pareto_list in pareto_2dlist:
    student_filepath = os.path.join(data_dir, str(pcnt),"student_exploration.csv")
    sf = open(student_filepath, "r")
    lines = sf.readlines()
    line0 = lines[0]
    line1 = lines[1]
    
    sf.close()
    score_2dlist1 = alternative_dict_list2_score_2d_list(pareto_list)
    s_measure = round(pyoptimise.analyse_xml.hyper_volume(score_2dlist1, ref_pt, min_max_list),2)
    #print "S MEASURES:", s_measure
    pareto_2dlist2 = pareto_2dlist[:]
    pareto_2dlist2.pop(pcnt)
    dominate_list = []
    c_measure_list = []
    for pareto_list2 in pareto_2dlist2:
        score_2dlist2 = alternative_dict_list2_score_2d_list(pareto_list2)
        c_measure1 = pyoptimise.analyse_xml.c_measures(score_2dlist1, score_2dlist2, min_max_list)
        c_measure2 = pyoptimise.analyse_xml.c_measures(score_2dlist2, score_2dlist1, min_max_list)
        c_measure_list.append(c_measure1)
        if c_measure1 > c_measure2:
            dominate_list.append(pareto_list2)
        #print "CMEASURE:", c_measure1, c_measure2
        
    domination = len(dominate_list)
    avg_cmeasure = round(sum(c_measure_list)/len(c_measure_list),2)
    #print "DOMINATION:", domination
    line1.replace("\n","")
    index = line1.index("\n")
    line1 = line1[0:index]
    line1 = line1 + "," + str(domination) + "," + str(avg_cmeasure) + "," + str(s_measure) + "\n"
    sf = open(student_filepath, "w")
    sf.write(line0+line1)
    sf.close()
    pcnt+=1    