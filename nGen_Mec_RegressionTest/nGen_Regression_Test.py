#-*- coding: utf-8 -*-
import sys
import difflib
import os
import subprocess
import datetime
import logging
import re
import emaillib

glogger = None
mail_text = []

def log(message, lvl=logging.INFO):
    if message[-1] == '\n':
        message = message[0:-1]

    if glogger:
        glogger.log(lvl, message)
    else:
        logging.log(lvl, message)


def GetLogger(root_path):
    logger = logging.getLogger('nGen_RT_app')
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(root_path + "\\log.log", "w", encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    handlerSt = logging.StreamHandler()
    handlerSt.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='[%(asctime)s]%(message)s',
        datefmt='%Y/%m/%d %I:%M')

    handler.setFormatter(formatter)
    handlerSt.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(handlerSt)
    return logger


def diff_mecFile(base_mec_path, tgt_mec_path):
    file_name = os.path.split(base_mec_path)[1].decode('cp949').encode('utf-8')
    title = " from |   to\t\tCompare [{}]".format(file_name)
    log(title)
    base_file = open(base_mec_path, "r")
    tgt_file = open(tgt_mec_path, "r")

    text1 = base_file.readlines()
    text2 = tgt_file.readlines()

    diff = difflib.ndiff(text1, text2)

    file_modified = False
    line_from_cnt = 1
    line_to_cnt = 1
    prev_modified = False

    for line in diff:
        if line[0] == '?':
            continue

        fmt_from_cnt = ''
        fmt_to_cnt = ''

        isModified = False
        if not line[0] == '+':
            fmt_from_cnt = '%5d' % line_from_cnt
            line_from_cnt += 1
        else:
            isModified = True
            fmt_from_cnt = '     '
            file_modified = True

        if not line[0] == '-':
            fmt_to_cnt = '%5d' % line_to_cnt
            line_to_cnt += 1
        else:
            isModified = True
            fmt_to_cnt = '     '
            file_modified = True

        if isModified != prev_modified:
            log('\n')

        prev_modified = isModified

        line_fmt = '{} |{}\t\t{}'.format(fmt_from_cnt, fmt_to_cnt, line)
        if isModified == True:
            log(line_fmt)

    base_file.close()
    tgt_file.close()

    temp = '[status : {0}] {1}\n'.format('X' if file_modified == True else 'O', file_name)
    mail_text.append(temp)

    return file_modified

def search_files(dirname):
    files = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        files.append(filename)
    return files

def main():
    print('hello wolrd')
    if len(sys.argv) < 4:
        print("error")
        return

    global glogger
    global mail_text
    dt = datetime.datetime.now()

    Program_Path = os.path.abspath(sys.argv[1])
    Base_root_Path = os.path.abspath(sys.argv[2])
    Base_upper_Path = os.path.abspath(Base_root_Path + '\..')
    RTModelPath = os.path.abspath(sys.argv[3])
    if len(sys.argv) > 4:
        toEmail = sys.argv[4]

    CopytoPath = Base_upper_Path + '\\Target Mec Files\\' + dt.strftime('%Y-%m-%d_%H_%M')
    fullpath = r'"{}" -RT PATH:"{}" COPYTO:"{}"'.format(Program_Path, RTModelPath, CopytoPath)
    subprocess.Popen(fullpath, shell=True).wait()

    glogger = GetLogger(CopytoPath)

    base_mec_files = search_files(Base_root_Path)
    tgt_mec_files = search_files(CopytoPath)

    mail_text.append("nGen Regression Test 문제 발생 !!\n")
    mail_text.append("자세한 비교 내용은 " + CopytoPath + " 참고 !!\n\n")

    file_modified = False
    for base_mec_path in base_mec_files:
        if not base_mec_path in tgt_mec_files:
            #log("not found Target Files\n\n\n\n")
            continue

        full_path_base = os.path.join(Base_root_Path, base_mec_path)
        full_path_tgt = os.path.join(CopytoPath, base_mec_path)
        file_stat = diff_mecFile(full_path_base, full_path_tgt)
        file_modified = file_stat or file_modified
        log('\n\n\n\n')

    if file_modified == True:
        eMailInst = emaillib.emaillib()
        eMailInst.sendMail(toEmail, [], mail_text)

if __name__ == "__main__":
    main()