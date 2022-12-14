import os 
import subprocess
import sys
import argparse

def creat_dir(turns_file):
    import os
    if not os.path.exists(turns_file):
        os.makedirs(turns_file)


def get_parent_name(row_info,loc):
        if "gen" not in row_info[loc]:
            PA = row_info[loc]
        elif "gen" in row_info[loc]:
            PA = row_info[loc].split("_")[-1]
        return PA


def get_ch1_ch2_name(CH):
    CH1 = CH.split("bk")[0].split("_")[-1]
    if "_" in CH.split("bk")[1]:
        CH2 = CH.split("bk")[1].split("/")[0].split("_")[-1]
    else:
        CH2 = "lin"+CH.split("bk")[1].split("/")[0].split("lin")[-1]
    return CH1,CH2


def run_3seq(filepath):
    generations_list = [4,6]
    for genera in generations_list:
        path = filepath+"/seq_method/gener"+str(genera)+"/"
        os.chdir(path)
        files= os.listdir(path)
        for file in files:
            if os.path.isdir(path+file): 
                for fi in os.listdir(path+file):
                    if "parental_seq.fasta" in fi:
                        parene_file_path = path+file+"/"+fi
                    elif "recom_seq.fasta" in fi:
                        child_file_path = path+file+"/"+fi
                        record_para = path+file+"/"+fi.split("_recom_seq")[0]

                subprocess.call (["cd /home/soniali/Downloads/3seq_build/ && \
                    echo y | ./3seq -f %s %s -id %s -t1" % (parene_file_path, child_file_path,record_para)],shell=True)
                

    for genera in generations_list:
        path = filepath+"/seq_method/gener"+str(genera)+"/" 
        os.chdir(path)
        
        files = os.listdir(path)
        files = []
        for i in range(1,11):
            files.append("turns"+str(i))
            
        each_condi_correct_rate = {}
        for file in files:
            turns_inter = 0
            if os.path.isdir(path+file): 
                
                for fi in os.listdir(path+file):
                    if "recom_seq.fasta" in fi:
                        child_file_path = path+file+"/"+fi
                        record_para = path+file+"/"+fi.split("_recom_seq")[0]
                        with open(child_file_path) as h:
                            lines = h.readlines()
                            for l in lines:
                                if ">" in l:
                                    CH1,CH2 = get_ch1_ch2_name(l.strip())
                                    if CH1 != CH2:
                                        turns_inter += 1
                
                para_record = "genera"+str(genera)+"turns"+file.split("turns")[1]
                if os.path.exists(path+file+"/"+para_record+".3s.rec"):
                    file_path = path+file+"/"+para_record+".3s.rec"
                elif os.path.exists(path+file+"/"+para_record+"_.3s.rec"):
                    file_path = path+file+"/"+para_record+"_.3s.rec"
                else:
                    continue
                    
                with open(file_path,"r") as hseq:
                    rows = hseq.readlines()

                    seq3_true_pos = 0
                    seq3_false_pos = 0
                    seq3_true_neg = 0
                    seq3_false_neg = 0

                    non_sig = 0
                    correct_num = 0
                    false_num = 0
                    if len(rows) == 1:
                        overall_correct_rate = 0
                    else:
                        for row in range(1,len(rows)):
                            row_info  = rows[row].split("\t")
                            PA = get_parent_name(row_info,0)
                            PB = get_parent_name(row_info,1)
                                
                            CH = rows[row].split("\t")[2]
                            pvalue = float(rows[row].split("\t")[9])
                            if pvalue >= 0.05:
                                non_sig+=1
                            elif pvalue < 0.05:
                                CH1 = CH.split("bk")[0].split("_")[-1]
                                if "_" in CH.split("bk")[1]:
                                    CH2 = CH.split("bk")[1].split("/")[0].split("_")[-1]
                                else:
                                    CH2 = "lin"+CH.split("bk")[1].split("/")[0].split("lin")[-1]

                                CH_set = {CH1,CH2}
                                PARENT_set = {PA,PB}
                                if  (CH_set - PARENT_set) == set(): # Correct
                                    correct_num+=1
                                    if CH1 != CH2:
                                        seq3_true_pos += 1 #TP
                                    elif CH1 == CH2:
                                        seq3_true_neg += 1 #TN
                                elif (CH_set - PARENT_set) != set(): #Wrong
                                    false_num+=1
                                    if CH1 != CH2:
                                        seq3_false_pos += 1 #FP
                                    elif CH1 == CH2:
                                        seq3_false_neg += 1 #FN
                        print(seq3_true_pos,seq3_false_neg,seq3_false_pos,seq3_true_neg)
                                    
                        if (false_num+correct_num+non_sig) == (len(rows)-1) and turns_inter != 0:
                                overall_correct_rate = round(seq3_true_pos/turns_inter,4)
                        else:
                            overall_correct_rate = ""
            
                each_condi_correct_rate[file] = overall_correct_rate

        # each_condi_correct_rate_sort = dict(sorted(each_condi_correct_rate.items(),key = lambda item:item[1], reverse=True))
        outpath = filepath+"/seq_method/"
        with open(outpath+"3seq_result_gener"+str(genera)+".txt","w+") as seq_file:
            for k in each_condi_correct_rate:
                seq_file.write(k+":\t"+str(each_condi_correct_rate[k])+"\n")
            

def main(sysargs=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Simulator_CovRecombTest',
        usage='''python seq3_run.py -smp 6 -f "/home/soniali/Desktop/03_CovRecomb/CovRecomb_Simulation_Test/CovRecomb_compare_3SEQ/"''')

    parser.add_argument("-smp", help="The number of differential feature mutations in each seed's generation process \n Default: 6", default=6)
    parser.add_argument("-sr", "--sample_rate", help="The sample rate for all the generated sequences for analyzing \n Default: 1", default=1)
    parser.add_argument("-f", "--temp_file", help="The file address \n", default="/home/soniali/Desktop/03_CovRecomb/CovRecomb_Simulation_Test/CovRecomb_compare_3SEQ/")
    
    if len(sysargs) < 1:
        parser.print_help()
        sys.exit(-1)
    else:
        args = parser.parse_args(sysargs)
    
    seed_mut_perlin = int(args.smp)
    temp_file = args.temp_file
    sample_rate = int(args.sample_rate)
    filepath = temp_file+"output_smp"+str(seed_mut_perlin)+"_sr"+str(sample_rate)+"/"
    run_3seq(filepath)


if __name__ == '__main__':
    main()
    