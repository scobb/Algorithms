'''
Created on Sep 27, 2014

@author: scobb
'''
import os
import subprocess
from find_mwmcm import main

def rename(dir, files, results_dir, tag):
    out_tag = 'test_out'
    for file in files:
        if 'out' in file:
            new_filename = tag + file.replace('file','').replace('out', out_tag)
        else:
            new_filename = tag + file.replace('file', '')
        subprocess.call(['cp', os.path.join(dir, file),
                        os.path.join(results_dir, new_filename)])


def check(dir):
    outputs = []
    correct_outputs = []
    for f in os.listdir(dir):
        if '.out' in f:
            outputs.append(os.path.join(dir, f))
        elif '.test_out' in f:
            correct_outputs.append(os.path.join(dir, f))
    outputs.sort()
    correct_outputs.sort()
    for i in range(len(outputs)):
        process = subprocess.Popen(['diff', outputs[i], correct_outputs[i]], stdout=subprocess.PIPE)
        out, err = process.communicate()
        if out:
            print ('Failed diff:\nours: %s\ntheirs: %s\ndiff: %s\n' %(outputs[i],
                                                                      correct_outputs[i],
                                                                      out))
            return
    print( "Check returned successful.")

if __name__ == '__main__':
    script_dir = os.getcwd()
    test_dir = os.path.join(script_dir, 'test_dir')
    small_dir = os.path.join(test_dir, 'small')
    med_dir = os.path.join(test_dir, 'medium')
    large_dir = os.path.join(test_dir, 'large')
    results_dir = os.path.join(test_dir, 'results')
    
    small_files = os.listdir(small_dir)
    med_files = os.listdir(med_dir)
    large_files = os.listdir(large_dir)
    
    rename(small_dir, small_files, results_dir, 'small')
    rename(med_dir, med_files, results_dir, 'med')
    rename(large_dir, large_files, results_dir, 'large')
    
    #for in_file in os.listdir(results_dir):
    #    if '.in' in in_file:
    #        main(os.path.join(results_dir, in_file))
            
    check(results_dir)
        
    
    
